import { ActivityMonitor } from '@jupyterlab/coreutils';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { Message } from '@lumino/messaging';

import { Panel, Widget } from '@lumino/widgets';
import { ErrorHandler } from './errorhandler';
import { anaChatIcon } from './iconimports';
import { IAnaChatStatus, IChatMessage, IKernelMatcher } from './interfaces';
import { NotebookComm } from './notebookcomm';
import { ChatWidget } from './view/chatwidget';
import { HeaderWidget } from './view/headerwidget';
import { KERNEL_CONNECTED, statusMessage } from './view/statusrenderer';

/**
 * Timeout for throttling AnaChat rendering.
 */
const RENDER_TIMEOUT = 1000;

/**
 * A widget for hosting a notebook anachat.
 */
export class AnaChat extends Panel {
  private _docmanager: IDocumentManager;
  private _currentWidget: Widget | null;
  private _visibleWidget: Widget | null;
  private _currentHandler: NotebookComm | null;
  private _mainWidget: Panel | null;
  private _monitor: ActivityMonitor<any, any> | null;
  private _tracker: INotebookTracker | null;
  private _status: IAnaChatStatus;
  private _eh: ErrorHandler;
  public handlers: { [id: string]: Promise<NotebookComm> };

  constructor(
    docmanager: IDocumentManager,
    tracker: INotebookTracker,
    eh: ErrorHandler
  ) {
    super();
    this._mainWidget = null;
    this._docmanager = docmanager;
    this._tracker = tracker;
    this._eh = eh;
    this.handlers = {};

    this._status = {
      connectedOnce: false,
      connectedNow: false,
      serverSide: false,
      hasKernel: false
    };

    this._currentHandler = null;
    this._currentWidget = null;
    this._visibleWidget = null;
    this._monitor = null;
  }

  private _report(error: any, func: string, params: any): any {
    console.log('bbbbbbbbbbb');
    return this._eh.report(error, 'AnaChat:' + func, params);
  }

  addNewNotebook(nbPanel: NotebookPanel): void {
    //A promise that resolves after the initialization of the handler is done.
    try {
      const handlers = this.handlers;
      const update = this.update.bind(this);
      this.handlers[nbPanel.id] = new Promise((resolve, reject) => {
        const session = nbPanel.sessionContext;
        const handler = new NotebookComm(session, nbPanel, this._eh, update);
        const scripts = session.ready.then(
          handler.getKernelLanguage.bind(handler)
        );
        scripts.then((language: IKernelMatcher) => {
          this._status.connectedOnce = true;
          handler.configureHandler(language);
        });
        scripts.catch((result: string) => {
          reject(result);
        });

        nbPanel.disposed.connect(() => {
          delete handlers[nbPanel.id];
          handler.dispose();
        });
        resolve(handler);
      });
    } catch (error) {
      throw this._report(error, 'addNewNotebook', [nbPanel.title.label]);
    }
  }

  changeActiveWidget(widget: Widget): void {
    try {
      this._currentWidget = widget;
      const future = this.handlers[widget.id];
      if (future !== undefined) {
        future.then((source: NotebookComm) => {
          this.currentHandler = source;
        });
      } else if (this._currentHandler !== null) {
        this.currentHandler = null;
      }
    } catch (error) {
      throw this._report(error, 'changeActiveWidget', [widget.title.label]);
    }
  }

  refreshAnaChat(): void {
    if (this.currentHandler) {
      this.currentHandler.sendRefreshKernel();
    }
    this.updateAnaChat();
  }

  sendText(text: string): void {
    if (this.currentHandler) {
      this.currentHandler.addMessage({
        text: text,
        type: 'user',
        timestamp: +new Date()
      });
    }
  }

  updateAnaChat(): void {
    try {
      if (this._mainWidget !== null && this.contains(this._mainWidget)) {
        this._mainWidget.dispose();
        this._mainWidget = null;
      }
      let title = 'Ana';
      this.title.icon = anaChatIcon.bindprops({ stylesheet: 'sideBar' });
      this._status.connectedNow = false;
      this._status.hasKernel = false;

      let showInput = true;
      let messages: IChatMessage[] = [];

      if (this.currentHandler) {
        this._status.connectedNow = true;
        this._status.hasKernel = this.currentHandler.hasKernel;
        this._visibleWidget = this.currentHandler.nbPanel;

        messages = this.currentHandler.chatHistory;
        const [status] = statusMessage(this._status);

        if (status !== KERNEL_CONNECTED) {
          messages = [
            ...messages,
            {
              text: status,
              type: 'error',
              timestamp: +new Date()
            }
          ];
          showInput = false;
        }

        title = 'Ana - ' + this.currentHandler.name;
      } else {
        messages = [
          {
            text: 'Please select a notebook',
            type: 'error',
            timestamp: +new Date()
          }
        ];
        showInput = false;
      }

      const headerWidget = new HeaderWidget(
        title,
        this._status,
        this._eh,
        this.refreshAnaChat.bind(this)
      );
      const chatWidget = new ChatWidget({
        messages,
        showInput,
        sendText: this.sendText.bind(this)
      });
      this._mainWidget = new Panel();
      this._mainWidget.addClass('jp-AnaChat');
      this._mainWidget.addWidget(headerWidget);
      this._mainWidget.addWidget(chatWidget);
      this.addWidget(this._mainWidget);
    } catch (error) {
      throw this._report(error, 'update', []);
    }
  }

  /**
   * Rerender after showing.
   */
  protected onAfterShow(msg: Message): void {
    try {
      this.update();
    } catch (error) {
      throw this._report(error, 'onAfterShow', []);
    }
  }

  protected onUpdateRequest(msg: Message): void {
    try {
      this.updateAnaChat();
    } catch (error) {
      throw this._report(error, 'onUpdateRequest', []);
    }
  }

  dispose(): void {
    try {
      if (this.isDisposed) {
        return;
      }
      if (this._currentHandler) {
        this._currentHandler.disconnectHandler();
        this._currentHandler = null;
      }
      super.dispose();
    } catch (error) {
      throw this._report(error, 'dispose', []);
    }
  }

  get currentHandler(): NotebookComm | null {
    return this._currentHandler;
  }

  set currentHandler(newHandler: NotebookComm | null) {
    try {
      const widget = this._currentWidget;
      if (this._currentHandler !== newHandler) {
        if (this._currentHandler !== null) {
          this._currentHandler.disconnectHandler();
        }
        this._currentHandler = newHandler;
        if (this._currentHandler !== null) {
          this._currentHandler.connectHandler();
        }
      }
      if (!newHandler || widget !== newHandler.nbPanel) {
        this.updateAnaChat();
        return;
      }
      if (
        this._tracker &&
        this._tracker.has(widget) &&
        widget !== this._visibleWidget
      ) {
        // Dispose an old activity monitor if it existsd
        if (this._monitor) {
          this._monitor.dispose();
          this._monitor = null;
        }

        // Find the document model associated with the widget.
        const context = this._docmanager.contextForWidget(widget);
        if (!context || !context.model) {
          throw Error('Could not find a context for Ana');
        }

        // Throttle the rendering rate of anachat.
        this._monitor = new ActivityMonitor({
          signal: context.model.contentChanged,
          timeout: RENDER_TIMEOUT
        });
        this._monitor.activityStopped.connect(this.update, this);
      }
      this.updateAnaChat();
    } catch (error) {
      throw this._report(error, 'set currentHandler', [newHandler?.name]);
    }
  }
}
