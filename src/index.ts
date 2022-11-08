import {
  ILabShell,
  ILayoutRestorer,
  type JupyterFrontEnd,
  type JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { AnaChat } from './anachat';
import type { IServerConfig } from './common/anachatInterfaces';
import { requestAPI } from './server';
import { anaRestrict, errorHandler, jupyterapp } from './stores';


function startPlugin(
  app: JupyterFrontEnd,
  labShell: ILabShell,
  restorer: ILayoutRestorer,
  notebookTracker: INotebookTracker,
  config: IServerConfig
) {
  try {
    console.log("Restrict: %s", config.restrict)
    anaRestrict.set(config.restrict);
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
      anaChat.changeActiveWidget(labShell, notebookTracker, widget as NotebookPanel);
    });
  } catch (error) {
    throw errorHandler.report(error, 'main', undefined);
  }
}

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
    requestAPI<any>('config', {
      method: 'GET'
    }).then((config: IServerConfig) => {
      startPlugin(app, labShell, restorer, notebookTracker, config);
    }).catch((reason: any) => {
      console.error(
        `The anachat server extension appears to be missing.\n${reason}\nStarting with default config`
      );
      startPlugin(app, labShell, restorer, notebookTracker, { restrict: [] });
    });
  }
  
};

export default plugin;
