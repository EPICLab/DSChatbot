import type { ISessionContext } from '@jupyterlab/apputils';
import type { Message } from '@lumino/messaging';

import { Panel } from '@lumino/widgets';
import { mainChatIcon } from './iconimports';
import { NotebookCommModel } from './dataAPI/NotebookCommModel';
import { MainView } from './components/MainView';
import { restrictNotebooks, notebookCommModel } from './stores';
import type { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { get } from 'svelte/store';
import type { ILabShell } from '@jupyterlab/application';

/**
 * A widget for hosting a notebook chatbot.
 */
export class MainChat extends Panel {
  private _sessionContext: ISessionContext | null;
  private _view: MainView;
  private _handlers: { [id: string]: Promise<NotebookCommModel> };

  constructor() {
    super();
    this.title.icon = mainChatIcon.bindprops({ stylesheet: 'sideBar' });
    this.title.caption = 'Newton';
    this.id = 'newton';
    this._sessionContext = null;
    this._handlers = {};

    // VIEW init
    this._view = new MainView();
    this.addWidget(this._view);
  }

  public addNewNotebook(widget: NotebookPanel): void {
    this._handlers[widget.id] = new Promise((resolve, reject) => {
      const handler = new NotebookCommModel(widget);

      widget.disposed.connect(() => {
        delete this._handlers[widget.id];
      });
      resolve(handler);
    });
  }

  public changeActiveWidget(
  labShell: ILabShell,
  tracker: INotebookTracker,
    widget: NotebookPanel
  ): void {
    const future = this._handlers[widget.id];
    if (future !== undefined) {
      future.then((model: NotebookCommModel) => {
        widget.revealed.then(async () => {
          if (tracker.currentWidget == widget) {
            this._sessionContext = widget.sessionContext;
            await model.connectNotebook();
            notebookCommModel.set(model);
            if (get(restrictNotebooks).includes(model.name)) {
              labShell.activateById(this.id);
            } else if (get(restrictNotebooks).length !== 0) {
              labShell.collapseRight();
            }
          }
        });
      });
    }
  }

  dispose(): void {
    this._sessionContext?.dispose();
    super.dispose();
  }

  protected onCloseRequest(msg: Message): void {
    super.onCloseRequest(msg);
    this.dispose();
  }
}
