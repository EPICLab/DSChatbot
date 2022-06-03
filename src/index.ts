import {
  ILabShell,
  ILayoutRestorer,
  type JupyterFrontEnd,
  type JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { AnaChat } from './anachat';
import { errorHandler, jupyterapp } from './stores';

/**
 * Initialization data for the anachat extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'anachat:plugin',
  autoStart: true,
  requires: [ILabShell, ILayoutRestorer, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    labShell: ILabShell,
    restorer: ILayoutRestorer,
    notebookTracker: INotebookTracker
  ) => {
    try {
      jupyterapp.set(app);
      // Create the widget
      const anaChat = new AnaChat();

      // Add the widget to the right area
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
        anaChat.changeActiveWidget(notebookTracker, widget as NotebookPanel);
      });
    } catch (error) {
      throw errorHandler.report(error, 'main', undefined);
    }
  }
};

export default plugin;
