import type { JupyterFrontEnd } from '@jupyterlab/application';
import { type Writable, writable, get } from 'svelte/store';
import type { IChatMessage } from './common/chatbotInterfaces';
import DocPanel from './components/DocPanel.svelte';
import type { NotebookCommModel } from './dataAPI/NotebookCommModel';
import { mainChatIcon } from './iconimports';
import { requestAPI } from './server';
import type { ISanitizer } from '@jupyterlab/apputils';
import type { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { openPanel, SveltePanelView } from './components/SveltePanelView';

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

function createPanelWidget() {
  let store = writable<SveltePanelView | null>(null);
  const { subscribe, set, update } = store;

  function load_panel(content: string, title: string, type: 'url' | 'html' | 'text') {
    let current = get(store)
    if (!current || !current?.isVisible) {
      if (current) {
        current.dispose();
      }
      current = openPanel(DocPanel, title, {content, title, type});
    } else{
      current.set_props({ content, title, type });
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
