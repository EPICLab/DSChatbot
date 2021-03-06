import type { ISessionContext } from '@jupyterlab/apputils';
import type { Message } from '@lumino/messaging';

import { Panel } from '@lumino/widgets';
import { anaChatIcon } from './iconimports';
import { AnaSideModel } from './dataAPI/AnaSideModel';
import { AnaSideView } from './components/AnaSideView';
import { anaSideModel } from './stores';
import type { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

/**
 * A widget for hosting a notebook anachat.
 */
export class AnaChat extends Panel {
  private _sessionContext: ISessionContext | null;
  private _view: AnaSideView;
  private _handlers: { [id: string]: Promise<AnaSideModel> };

  constructor() {
    super();
    this.title.icon = anaChatIcon.bindprops({ stylesheet: 'sideBar' });
    this.title.caption = 'ana';
    this.id = 'ana';
    this._sessionContext = null;
    this._handlers = {};

    // VIEW init
    this._view = new AnaSideView();
    this.addWidget(this._view);
  }

  public addNewNotebook(widget: NotebookPanel): void {
    this._handlers[widget.id] = new Promise((resolve, reject) => {
      const handler = new AnaSideModel(widget);

      widget.disposed.connect(() => {
        delete this._handlers[widget.id];
      });
      resolve(handler);
    });
  }

  public changeActiveWidget(
    tracker: INotebookTracker,
    widget: NotebookPanel
  ): void {
    const future = this._handlers[widget.id];
    if (future !== undefined) {
      future.then((model: AnaSideModel) => {
        widget.revealed.then(async () => {
          if (tracker.currentWidget == widget) {
            this._sessionContext = widget.sessionContext;
            await model.connectNotebook();
            anaSideModel.set(model);
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
