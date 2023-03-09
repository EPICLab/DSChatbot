import type { JSONObject } from '@lumino/coreutils';
import type { ISessionContext } from '@jupyterlab/apputils';
import { get, writable, type Writable } from 'svelte/store';

import {
  notebookCommModel,
  connectionReady,
  errorHandler,
  kernelStatus,
} from '../stores';
import { NotebookActions, type NotebookPanel } from '@jupyterlab/notebook';
import type {
  IComm,
  IKernelConnection
} from '@jupyterlab/services/lib/kernel/kernel';
import {
  GenericMatcher,
  type IAutoCompleteItem,
  type IChatMessage,
  type IKernelMatcher,
  type ILoaderForm,
  type Subset
} from '../common/chatbotInterfaces';
import type { KernelMessage } from '@jupyterlab/services';
import type { IErrorMsg } from '@jupyterlab/services/lib/kernel/messages';
import { createChatInstance, type IChatInstance } from '../chatinstance';

export class NotebookCommModel {
  private _sessionContext: ISessionContext;
  public _notebook: NotebookPanel;
  private _icomm: IComm | null;
  private _language: IKernelMatcher;
  public chatInstances: Writable<{ [id: string]: IChatInstance }>;
  public chatLoaders: Writable<{ [id: string]: ILoaderForm }>;
  /*private _boundQueryCall: (
    sess: ISessionContext,
    args: KernelMessage.IMessage<KernelMessage.MessageType>
  ) => void;*/

  constructor(notebook: NotebookPanel) {
    this._sessionContext = notebook.sessionContext;
    this._notebook = notebook;
    this._icomm = null;
    this._language = GenericMatcher;
    this.chatInstances = writable({
      "base": createChatInstance(this, "base", "newton") // Passing this here may cause a memory leak, but I haven't checked
    });
    this.chatLoaders = writable({});
    //this._boundQueryCall = this._queryCall.bind(this);
  }

  get session(): ISessionContext {
    return this._sessionContext;
  }

  get language(): string | null {
    return this._language?.language;
  }

  get name(): string {
    return this.session?.name;
  }

  public async connectNotebook() {
    console.log('Connecting notebook to Newton');
    this.resetData();

    await this.session.ready;
    kernelStatus.setattr('connectedOnce', true);
    this.listenForRestart();
    await this.initBot();
    connectionReady.set(true);
  }

  public refresh() {
    console.log("refresh", this.name)
    this.sendRefreshLoaders();
    for (const instance of Object.keys(get(this.chatInstances))) {
      this.sendRefreshInstance(instance);
    }
  }

  public insertAbove(text: string) {
    const content = this._notebook.content;
    NotebookActions.insertAbove(content);
    const activeCell = content.activeCell;
    if (activeCell) {
      activeCell.model.value.text = text;
      activeCell.editorWidget.editor.focus();
    }
  }

  public insertBelow(text: string) {
    const content = this._notebook.content;
    NotebookActions.insertBelow(content);
    const activeCell = content.activeCell;
    if (activeCell) {
      activeCell.model.value.text = text;
      activeCell.editorWidget.editor.focus();
    }
  }

  public insertBottom(text: string) {
    const content = this._notebook.content;
    content.activeCellIndex = content.widgets.length - 1;
    NotebookActions.insertBelow(content);
    const activeCell = content.activeCell;
    if (activeCell) {
      activeCell.model.value.text = text;
      activeCell.editorWidget.editor.focus();
    }
  }

  public async listenForRestart() {
    this.session.session?.kernel?.statusChanged.connect((_, status) => {
      if (status.endsWith('restarting')) {
        kernelStatus.setattr('hasKernel', false);
        // DO something
        console.log('[Newton] resetting data on kernel restart.');
        this.resetData();
        this.initBot().then();
      }
    });
  }

  public async initBot() {
    const kernel = this.session.session?.kernel;
    if (!kernel) {
      throw errorHandler.report(undefined, 'NotebookCommModel:initBot', []);
    }
    await this._setKernelLanguage(kernel);
    kernelStatus.setattr('connectedOnce', true);
    kernelStatus.setattr('connectedNow', !!get(notebookCommModel));
    kernel.registerCommTarget('newton.comm', (comm, msg) => {
      this._icomm = comm;
      this._icomm.onMsg = this._receiveNewtonQuery.bind(this);
    });
    await this._initOnKernel(kernel);
    //this._sessionContext.iopubMessage.disconnect(this._boundQueryCall);
    //this._sessionContext.iopubMessage.connect(this._boundQueryCall);
  }

  public resetData() {
    connectionReady.set(false);
    kernelStatus.reset();
    for (const chatInstance of Object.values(get(this.chatInstances))) {
      chatInstance.reset();
    }
  }

  /**
   * Send data to icomm
   * @param data
   */
  public send(data: JSONObject): void {
    const session = this._sessionContext.session;
    if (
      this._icomm &&
      session &&
      session.kernel &&
      session.kernel.hasComm(this._icomm.commId)
    ) {
      this._icomm.send(data);
    }
  }

  /**
   * Send a init command to the kernel
   */
  public sendInitKernel(): void {
    this.send({
      operation: 'init',
      instance: "<all>"
    });
  }

  /**
   * Send a init command to the kernel
   */
  public sendMessageKernel(instance: string, message: IChatMessage): void {
    this.send({
      operation: 'message',
      instance,
      message: message as unknown as JSONObject
    });
  }

  /**
   * Send a cell execution command to the kernel
   */
  /*public sendExecKernel(): void {
    this.send({
      operation: 'exec',
      instance: "<all>"
    });
  }*/

  /**
   * Send a create instance command to the kernel
   */
  public sendCreateInstance(name: string, mode: string, data: { [id: string]: string | null }): void {
    this.send({
      operation: 'new-instance',
      instance: '<meta>',
      name,
      mode,
      data
    });
  }

  /**
   * Send a remove instance command to the kernel
   */
  public sendRemoveInstance(name: string): void {
    this.send({
      operation: 'remove-instance',
      instance: '<meta>',
      name
    });
  }

  /**
   * Send a refresh command to the kernel
   */
  public sendRefreshLoaders(): void {
    this.send({
      operation: 'refresh',
      instance: '<meta>'
    });
  }

  /**
   * Send a refresh command to the kernel
   */
  public sendRefreshInstance(instance: string): void {
    this.send({
      operation: 'refresh',
      instance
    });
  }

  /**
   * Send a config command to the kernel
   */
  public sendConfig(instance: string, data: any): void {
    data.operation = 'config';
    data.instance = instance;
    this.send(data);
  }

  /**
   * Send a message sync command to the kernel
   */
  public sendSyncMessage(instance: string, message: Pick<IChatMessage, 'id'> & Subset<IChatMessage>): void {
    this.send({
      operation: 'sync-message',
      instance,
      message
    })
  }

  /**
   * Send a subject query command to the kernel
   */
   public sendAutoCompleteQuery(instance: string, requestId: number, query: string): void {
    this.send({
      operation: 'autocomplete-query',
      instance,
      requestId: requestId,
      query: query,
    });
  }

  private async _setKernelLanguage(kernel: IKernelConnection) {
    const infoReply = await kernel.info;
    this._language = GenericMatcher;
    if (
      kernel.name.match('python') ||
      infoReply?.language_info.name.match('python')
    ) {
      this._language = {
        language: 'python',
        initScript: 'import anachat.comm; anachat.comm.init()',
        evalue: "No module named 'anachat.comm'"
      };
    }
  }

  private async _initOnKernel(kernel: IKernelConnection) {
    const code = this._language.initScript;
    if (!code) {
      return;
    }
    const language = this._language;
    const content: KernelMessage.IExecuteRequestMsg['content'] = {
      code: code,
      stop_on_error: false,
      store_history: false,
      silent: true
    };
    const future = kernel.requestExecute(content, false);
    future.onIOPub = (msg: KernelMessage.IIOPubMessage): void => {
      if (
        msg.header.msg_type === 'error' &&
        (msg as IErrorMsg).content.evalue === language.evalue
      ) {
        const err: IErrorMsg = msg as IErrorMsg;
        errorHandler.report(undefined, '_initOnKernel', [
          err.content.ename,
          err.content.evalue,
          err.content.traceback
        ]);
      }
      this.sendInitKernel();
    };
    return future;
  }

  /*
   * Handle query response
   */
  private _loadInstanceConfig(chatInstance: IChatInstance, config: { [id: string]: any }) {
    for (const [key, value] of Object.entries(config)) {
      let configVar = chatInstance.configMap[key];
      if (configVar !== undefined) {
        configVar.initialized = true;
        configVar.load(value);
      }
    }
  }

  private _loadInstances(instances: { [id: string]: string }) {
    let changed = false;
    let chatInstancesObj = get(this.chatInstances);
    for (const instance of Object.keys(chatInstancesObj)) {
      if (!(instance in instances)) {
        delete chatInstancesObj[instance];
        changed = true;
      }
    }
    for (const [instance, mode] of Object.entries(instances)) {
      if (!(instance in chatInstancesObj)) {
        chatInstancesObj[instance] = createChatInstance(this, instance, mode);
        chatInstancesObj[instance].refresh();
        changed = true;
      }
    }
    if (changed) {
      this.chatInstances.set(chatInstancesObj);
    }
  }

  private _receiveNewtonQuery(
    msg: KernelMessage.ICommMsgMsg
  ): void | PromiseLike<void> {
    try {
      console.log("MSG", msg.content.data);
      const operation = msg.content.data.operation;
      const instance = msg.content.data.instance as string;

      if (instance === "<meta>") {
        if (operation === 'sync-meta') {
          this.chatLoaders.set(msg.content.data.loaders as unknown as { [id: string]: ILoaderForm });
          const instances = msg.content.data.instances as unknown as { [id: string]: string };
          this._loadInstances(instances);
        }
        return;
      }

      const chatInstance = get(this.chatInstances)[instance];

      if (chatInstance === undefined) {
        throw new Error("Invalid instance " + instance);
      }
      if (operation === 'init' || operation === 'refresh') {
        kernelStatus.setattr('hasKernel', true);
        console.log("Load", instance, msg.content.data)
        chatInstance.load(msg.content.data.history as unknown as IChatMessage[]);        
        this._loadInstanceConfig(chatInstance, msg.content.data.config as unknown as { [id: string]: any });
      } else if (operation === 'reply') {
        kernelStatus.setattr('hasKernel', true);
        const message: IChatMessage = msg.content.data
          .message as unknown as IChatMessage;
          chatInstance.push(message);
      } else if (operation === 'update-message') {
        kernelStatus.setattr('hasKernel', true);
        const message: IChatMessage = msg.content.data
          .message as unknown as IChatMessage;
          chatInstance.updateMessage(message);
      } else if (operation === 'update-config') {
        const config: { [id: string]: any } = msg.content.data
          .config as unknown as { [id: string]: any };
        this._loadInstanceConfig(chatInstance, config)
      } else if (operation === 'error') {
        errorHandler.report(
          'Failed to run ICOMM command',
          '_receiveNewtonQuery',
          [msg.content.data.command, msg.content.data.message]
        );
      } else if (operation === 'autocomplete-response') {
        const { autoCompleteResponseId, autoCompleteItems } = chatInstance;
        autoCompleteResponseId.set(msg.content.data.responseId as number);
        autoCompleteItems.set(msg.content.data.items as unknown as IAutoCompleteItem[]);
      }
    } catch (error) {
      throw errorHandler.report(error, '_receiveNewtonQuery', [msg]);
    }
  }

  /*
   * Invokes a inspection if the signal emitted from specified session is an 'execute_input' msg.
   */
  /*private _queryCall(
    sess: ISessionContext,
    args: KernelMessage.IMessage
  ): void {
    try {
      const msg: KernelMessage.IIOPubMessage =
        args as KernelMessage.IIOPubMessage;
      const msgType = msg.header.msg_type;
      switch (msgType) {
        case 'execute_input':
          this.sendExecKernel();
          break;
        default:
          break;
      }
    } catch (error) {
      throw errorHandler.report(error, '_queryCall', [args.content]);
    }
  }*/
}
