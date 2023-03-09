import type { JupyterFrontEnd } from '@jupyterlab/application';
import { type Writable, writable, get } from 'svelte/store';
import { type IChatMessage, MessageDisplay, type IChatInstance, type IConfigVar, type Subset, type ILoaderForm } from './common/chatbotInterfaces';
import { DocPanelView } from './components/DocPanelView';
import type { NotebookCommModel } from './dataAPI/NotebookCommModel';
import { mainChatIcon } from './iconimports';
import { requestAPI } from './server';
import { checkTarget, cloneMessage, messageTarget } from './common/messages';
import type { ISanitizer } from '@jupyterlab/apputils';
import type { IRenderMimeRegistry } from '@jupyterlab/rendermime';

function createErrorHandler() {
  let current: string[] = [];
  const { subscribe, set } = writable(current);
  let _id: number = 0;

  if (!('toJSON' in Error.prototype)) {
    Object.defineProperty(Error.prototype, 'toJSON', {
      value: function () {
        const alt = {};

        Object.getOwnPropertyNames(this).forEach((key: any) => {
          (alt as any)[key] = (this as any)[key];
        }, this);

        return alt;
      },
      configurable: true,
      writable: true
    });
  }

  function clear(): void {
    current = [];
    set(current);
  }

  function report(error: any, func: string, params: any): any {
    /* eslint @typescript-eslint/explicit-module-boundary-types: 0 */
    if ({}.hasOwnProperty.call(error, 'reportId')) {
      error.reportParent = error.reportId;
    }
    if (typeof error === 'object') {
      error.reportId = _id++;
    } else {
      error = {
        reportId: _id++,
        message: error,
        otype: typeof error
      };
    }
    const date = new Date();
    const result = {
      error: error,
      func: func,
      params: params,
      date: date
    };
    current.push(
      `${date} - ${func}:\n  ${error.toString()}\n  ${JSON.stringify(
        params.toString()
      )}`
    );
    set(current);

    requestAPI<any>('error', {
      body: JSON.stringify(result),
      method: 'POST'
    }).catch((reason: any) => {
      console.error(
        `The newton server extension appears to be missing.\n${reason}`
      );
      return reason;
    });

    console.error('[Newton] Error:', func, error, params);
    return error;
  }

  return {
    subscribe,
    clear,
    report
  };
}

function createStatus() {
  let current = {
    connectedOnce: writable(false),
    connectedNow: writable(false),
    serverSide: writable(false),
    hasKernel: writable(false)
  };
  const { subscribe, set, update } = writable(current);

  function reset() {
    current.connectedOnce.set(false);
    current.connectedNow.set(false);
    current.serverSide.set(false);
    current.hasKernel.set(false);
    set(current);
  }

  function setattr(
    attr: 'connectedOnce' | 'connectedNow' | 'serverSide' | 'hasKernel',
    value: boolean
  ) {
    current[attr].set(value);
    set(current);
  }

  return {
    subscribe,
    set,
    update,
    reset,
    setattr
  };
}

export function createChatInstance(chatName: string, mode: string): IChatInstance {
  let current: IChatMessage[] = [];
  let autoCompleteResponseId = writable(-1); 
  let autoCompleteItems = writable([]);
  let configMap: { [id: string]: IConfigVar<any>} = {};

  function createConfigVar<T>(name: string, value: T) {
    let { subscribe, set, update } = writable(value);
    let configVar = { subscribe, set, update, load: (_v: T) => {}, initialized: false };
    configVar.set = (new_value: T) => {
      get(notebookCommModel)?.sendConfig(chatName, { 
        key: name, 
        value: new_value, 
        _mode: configVar.initialized? 'update': 'init'
      })
      return set(value);
    }
    configVar.load = (new_value: any) => {
      set(new_value);
    }
    configMap[name] = configVar;
    return configVar;
  }

  let config = {
    processInKernel: createConfigVar("process_in_kernel", true),
    enableAutoComplete: createConfigVar("enable_autocomplete", true),
    enableAutoLoading: createConfigVar("enable_auto_loading", false),
    loading: createConfigVar("loading", false),

    showReplied: createConfigVar("show_replied", false),
    showIndex: createConfigVar("show_index", false),
    showTime: createConfigVar("show_time", true),
    showBuildMessages: createConfigVar("show_build_messages", true),
    showKernelMessages: createConfigVar("show_kernel_messages", true),
  }

  let messageMap: { [key: string]: { position: number, message: IChatMessage} } = {};
  const { subscribe, set, update } = writable(current);

  function push(newMessage: IChatMessage) {
    newMessage.new = true;
    messageMap[newMessage['id']] = { position: current.length, message: newMessage };
    current.push(newMessage);
    
    set(current);
    if ((get(wizardMode) != (newMessage.type != 'user')) && !['kernel', 'build'].includes(checkTarget(newMessage))) {
      replying.set(newMessage['id']);
    }
    if (newMessage.display == MessageDisplay.SupermodeInput) {
      let buildMessage = cloneMessage(newMessage, messageTarget('user'))
      wizardPreviewMessage.set([...get(wizardPreviewMessage), buildMessage]);
    }
  }

  function addNew(newMessage: IChatMessage) {
    get(notebookCommModel)?.sendMessageKernel(chatName, newMessage);
  }

  function load(data: IChatMessage[]) {
    current = data;
    messageMap = {};
    current.forEach((message, index) => {
      messageMap[message['id']] = { position: index, message: message };
    });
    const lastMessage = data[data.length - 1];
    if ((get(wizardMode) != (lastMessage.type != 'user')) && !['kernel', 'build'].includes(checkTarget(lastMessage))) {
      replying.set(lastMessage['id']);
    }
    set(current);
  }

  function updateMessage(message: IChatMessage) {
    let { position } = messageMap[message['id']];
    current[position] = message;
    messageMap[message['id']] = { position, message };
    set(current);
  }

  function submitSyncMessage(message: Pick<IChatMessage, 'id'> & Subset<IChatMessage>) {
    get(notebookCommModel)?.sendSyncMessage(chatName, message);
  }

  function removeLoading(messageId: string) {
    submitSyncMessage({
      id: messageId,
      loading: false
    })
  }

  function reset() {
    current = [];
    messageMap = {};
    autoCompleteResponseId.set(-1);
    autoCompleteItems.set([]);
    set(current);
  }

  function findById(messageId: string | null) {
    if (messageId === null) {
      return null;
    }
    let message = messageMap[messageId];
    if (message === undefined) {
      return null;
    }
    return message.message;
  }

  function sendAutoComplete(requestId: number, query: string) {
    get(notebookCommModel)?.sendAutoCompleteQuery(chatName, requestId, query);
  }

  function refresh() {
    console.log("refresh", chatName)
    get(notebookCommModel)?.sendRefreshInstance(chatName);
  }

  return {
    mode,
    subscribe,
    set,
    update,
    push,
    addNew,
    load,
    submitSyncMessage,
    updateMessage,
    removeLoading,
    reset,
    findById,
    sendAutoComplete,
    refresh,

    configMap,
    config,
    autoCompleteResponseId,
    autoCompleteItems
  };
}


function createPanelWidget() {
  let id = 1;
  let store = writable<DocPanelView | null>(null);
  const { subscribe, set, update } = store;

  function load_panel(content: string, title: string, type: 'url' | 'html' | 'text') {
    let current = get(store)
    if (!current || !current?.isVisible) {
      if (current) {
        current.dispose();
      }
      current = new DocPanelView(content, title, type);
      current.id = "NewtonPanel-" + (id++);
      current.title.closable = true;
      get(jupyterapp)?.shell.add(current, 'main', { mode: 'split-right' })
    } else{
      current.set_props(content, title, type);
    }
    current.title.label = title;
    current.title.icon = mainChatIcon.bindprops({ stylesheet: 'mainAreaTab' });;
    set(current);
  }

  function load_url(url: string, title="Info") {
    load_panel(url, title, 'url')
  }

  function load_html(url: string, title: string) {
    load_panel(url, title, 'html')
  }

  function load_text(url: string, title: string) {
    load_panel(url, title, 'text')
  }

  return {
    subscribe,
    set,
    update,
    load_panel,
    load_url,
    load_html,
    load_text,
  };

}

// ~~~~~~~~~~~ Stores ~~~~~~~~~~~~~~~~
export const replying: Writable<string | null> = writable(null);
export const restrictNotebooks: Writable<string[]> = writable([]);
export const jupyterapp: Writable<JupyterFrontEnd | null> = writable(null);
export const jupyterSanitizer: Writable<ISanitizer | null> = writable(null);
export const jupyterRenderMime: Writable<IRenderMimeRegistry | null> = writable(null);
export const notebookCommModel: Writable<NotebookCommModel | null> = writable(null);
export const connectionReady: Writable<boolean> = writable(false);

export const wizardMode: Writable<boolean> = writable(true);
export const wizardValue: Writable<string> = writable("")
export const wizardPreviewMessage: Writable<IChatMessage[]> = writable([]);

export const kernelStatus = createStatus();
export const panelWidget = createPanelWidget();
export const errorHandler = createErrorHandler();


export const chatInstances: Writable<{ [id: string]: IChatInstance }> = writable({
  "base": createChatInstance("base", "newton")
});



export const chatLoaders: Writable<{ [id: string]: ILoaderForm }> = writable({});
