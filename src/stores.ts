import type { JupyterFrontEnd } from '@jupyterlab/application';
import { type Writable, writable, get } from 'svelte/store';
import type { IChatMessage, IAutoCompleteItem } from './common/anachatInterfaces';
import { AnaPanelView } from './components/AnaPanelView';
import type { AnaSideModel } from './dataAPI/AnaSideModel';
import { anaChatIcon } from './iconimports';
import { requestAPI } from './server';

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
    current.push(newMessage);
    set(current);
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

  function load_url(url: string, title="Info") {
    let current = get(store)
    if (!current || !current?.isVisible) {
      if (current) {
        current.dispose();
      }
      current = new AnaPanelView(url, title);
      current.id = "AnaPanel-" + (id++);
      current.title.closable = true;
      get(jupyterapp)?.shell.add(current, 'main', { mode: 'split-right' })
    } else{
      current.set_props(url, title);
    }
    current.title.label = title;
    current.title.icon = anaChatIcon.bindprops({ stylesheet: 'mainAreaTab' });;
    set(current);
  }

  return {
    subscribe,
    set,
    update,
    load_url,
  };

}

// ~~~~~~~~~~~ Stores ~~~~~~~~~~~~~~~~
export const anaRestrict: Writable<string | null> = writable(null);
export const jupyterapp: Writable<JupyterFrontEnd | null> = writable(null);
export const anaSideModel: Writable<AnaSideModel | null> = writable(null);
export const anaSideReady: Writable<boolean> = writable(false);
export const anaSuperMode: Writable<boolean> = writable(false);
export const anaLoading: Writable<boolean> = writable(false);
export const anaQueryEnabled: Writable<boolean> = writable(true);
export const anaMessageEnabled: Writable<boolean> = writable(true);
export const anaTimes: Writable<boolean> = writable(true);
export const subjectItems: Writable<{responseId: Writable<number>, sitems: Writable<IAutoCompleteItem[]>}> = writable({responseId: writable(-1), sitems: writable([])})
export const chatHistory = createChatHistory();
export const kernelStatus = createStatus();
export const panelWidget = createPanelWidget();

export const errorHandler = createErrorHandler();
