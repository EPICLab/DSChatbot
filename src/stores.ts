import { type Writable, writable, get } from 'svelte/store';
import type { IChatMessage } from './common/anachatInterfaces';
import type { AnaSideModel } from './dataAPI/AnaSideModel';
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
    current.push(newMessage);
    const model = get(anaSideModel);
    set(current);
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

// ~~~~~~~~~~~ Stores ~~~~~~~~~~~~~~~~
export const anaSideModel: Writable<AnaSideModel | null> = writable(null);
export const anaSideReady: Writable<boolean> = writable(false);
export const chatHistory = createChatHistory();
export const kernelStatus = createStatus();

export const errorHandler = createErrorHandler();
