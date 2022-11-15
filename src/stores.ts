import type { JupyterFrontEnd } from '@jupyterlab/application';
import { type Writable, writable, get } from 'svelte/store';
import { type IChatMessage, type IAutoCompleteItem, MessageDisplay } from './common/anachatInterfaces';
import { AnaPanelView } from './components/AnaPanelView';
import type { AnaSideModel } from './dataAPI/AnaSideModel';
import { anaChatIcon } from './iconimports';
import { requestAPI } from './server';
import { cloneMessage, messageTarget } from './common/messages';
import type { ISanitizer } from '@jupyterlab/apputils';

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
        `The anachat server extension appears to be missing.\n${reason}`
      );
      return reason;
    });

    console.error('[AnaChat] Error:', func, error, params);
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

function createChatHistory() {
  let current: IChatMessage[] = [];
  const { subscribe, set, update } = writable(current);

  function push(newMessage: IChatMessage) {
    newMessage.new = true;
    current.push(newMessage);
    set(current);
    if (get(anaSuperMode) != (newMessage.type != 'user')) {
      replying.set(newMessage['id']);
    }
    if (newMessage.display == MessageDisplay.SupermodeInput) {
      let buildMessage = cloneMessage(newMessage, messageTarget('user'))
      superModePreviewMessage.set([...get(superModePreviewMessage), buildMessage]);
    }
  }

  function addNew(newMessage: IChatMessage) {
    //current.push(newMessage);
    const model = get(anaSideModel);
    //set(current);
    if (model) {
      model.sendMessageKernel(newMessage);
    }
  }

  function load(data: IChatMessage[]) {
    current = data;
    const lastMessage = data[data.length - 1];
    if (get(anaSuperMode) != (lastMessage.type != 'user')) {
      replying.set(lastMessage['id']);
    }
    set(current);
  }

  function reset() {
    current = [];
    set(current);
  }

  return {
    subscribe,
    set,
    update,
    push,
    addNew,
    reset,
    load
  };
}


function createPanelWidget() {
  let id = 1;
  let store = writable<AnaPanelView | null>(null);
  const { subscribe, set, update } = store;

  function load_panel(content: string, title: string, type: 'url' | 'html' | 'text') {
    let current = get(store)
    if (!current || !current?.isVisible) {
      if (current) {
        current.dispose();
      }
      current = new AnaPanelView(content, title, type);
      current.id = "AnaPanel-" + (id++);
      current.title.closable = true;
      get(jupyterapp)?.shell.add(current, 'main', { mode: 'split-right' })
    } else{
      current.set_props(content, title, type);
    }
    current.title.label = title;
    current.title.icon = anaChatIcon.bindprops({ stylesheet: 'mainAreaTab' });;
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
export const anaRestrict: Writable<string[]> = writable([]);
export const jupyterapp: Writable<JupyterFrontEnd | null> = writable(null);
export const jupyterSanitizer: Writable<ISanitizer | null> = writable(null);
export const anaSideModel: Writable<AnaSideModel | null> = writable(null);
export const anaSideReady: Writable<boolean> = writable(false);
export const anaSuperMode: Writable<boolean> = writable(true);
export const anaLoading: Writable<boolean | number> = writable(false);
export const anaAutoLoading: Writable<boolean> = writable(false);
export const anaQueryEnabled: Writable<boolean> = writable(true);
export const anaMessageEnabled: Writable<boolean> = writable(true);
export const anaTimes: Writable<boolean> = writable(true);
export const subjectItems: Writable<{responseId: Writable<number>, sitems: Writable<IAutoCompleteItem[]>}> = writable({responseId: writable(-1), sitems: writable([])})
export const superModePreviewMessage: Writable<IChatMessage[]> = writable([]);
export const chatHistory = createChatHistory();
export const kernelStatus = createStatus();
export const panelWidget = createPanelWidget();

export const errorHandler = createErrorHandler();
