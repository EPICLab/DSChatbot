import {
  ILabShell,
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { IDocumentManager } from '@jupyterlab/docmanager';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { AnaChat } from './anachat';

import { requestAPI } from './server';
import { anaChatIcon } from './iconimports';
import { ErrorHandler } from './errorhandler';

/**
 * Initialization data for the anachat extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'anachat:plugin',
  autoStart: true,
  requires: [IDocumentManager, ILabShell, ILayoutRestorer, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    docmanager: IDocumentManager,
    labShell: ILabShell,
    restorer: ILayoutRestorer,
    notebookTracker: INotebookTracker
  ) => {
    const eh = new ErrorHandler();
    try {
      // Create the widget
      const anaChat = new AnaChat(docmanager, notebookTracker, eh);

      // Add the widget to the right area
      anaChat.title.icon = anaChatIcon.bindprops({ stylesheet: 'sideBar' });
      anaChat.title.caption = 'ana';
      anaChat.id = 'ana';
      labShell.add(anaChat, 'right', { rank: 700 });

      // Add the widget to the application restorer
      restorer.add(anaChat, 'jupyterlab-anachat');

      /**
       * Subscribes to the creation of new notebooks. If a new notebook is created, build a new handler for the notebook.
       * Adds a promise for a instanced handler to the 'handlers' collection.
       */
      notebookTracker.widgetAdded.connect((sender, nbPanel: NotebookPanel) => {
        anaChat.addNewNotebook(nbPanel);
      });

      // Change the julynter when the active widget changes.
      labShell.currentChanged.connect((sender, args) => {
        const widget = args.newValue;
        if (!widget) {
          return;
        }
        anaChat.changeActiveWidget(widget);
      });

      requestAPI<any>('get_example')
        .then(data => {
          console.log(data);
        })
        .catch(reason => {
          console.error(
            `The anachat server extension appears to be missing.\n${reason}`
          );
        });
      console.log('JupyterLab extension anachat is activated!');
    } catch (error) {
      throw eh.report(error, 'activate', []);
    }
  }
};

export default plugin;
