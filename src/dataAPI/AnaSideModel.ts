import type { JSONObject } from '@lumino/coreutils';
import type { ISessionContext } from '@jupyterlab/apputils';
import { get } from 'svelte/store';

import {
  anaSideModel,
  anaSideReady,
  chatHistory,
  errorHandler,
  kernelStatus,
  subjectItems,
  anaQueryEnabled,
  anaMessageEnabled,
  anaLoading,
  anaAutoLoading,
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
  type IKernelMatcher
} from '../common/anachatInterfaces';
import type { KernelMessage } from '@jupyterlab/services';
import type { IErrorMsg } from '@jupyterlab/services/lib/kernel/messages';

export class AnaSideModel {
  private _sessionContext: ISessionContext;
  private _notebook: NotebookPanel;
  private _icomm: IComm | null;
  private _language: IKernelMatcher;
  private _boundQueryCall: (
    sess: ISessionContext,
    args: KernelMessage.IMessage<KernelMessage.MessageType>
  ) => void;

  constructor(notebook: NotebookPanel) {
    this._sessionContext = notebook.sessionContext;
    this._notebook = notebook;
    this._icomm = null;
    this._language = GenericMatcher;
    this._boundQueryCall = this._queryCall.bind(this);
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
    console.log('Connecting notebook to AnaChat');
    this.resetData();

    await this.session.ready;
    kernelStatus.setattr('connectedOnce', true);
    this.listenForRestart();
    await this.initAna();
    anaSideReady.set(true);
  }

  public refresh() {
    this.sendRefreshKernel();
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
        console.log('[AnaChat] resetting data on kernel restart.');
        this.resetData();
        this.initAna().then();
      }
    });
  }

  public async initAna() {
    const kernel = this.session.session?.kernel;
    if (!kernel) {
      throw errorHandler.report(undefined, 'AnaSideModel:initAna', []);
    }
    await this._setKernelLanguage(kernel);
    kernelStatus.setattr('connectedOnce', true);
    kernelStatus.setattr('connectedNow', !!get(anaSideModel));
    kernel.registerCommTarget('anachat.comm', (comm, msg) => {
      this._icomm = comm;
      this._icomm.onMsg = this._receiveAnaChatQuery.bind(this);
    });
    await this._initOnKernel(kernel);
    this._sessionContext.iopubMessage.disconnect(this._boundQueryCall);
    this._sessionContext.iopubMessage.connect(this._boundQueryCall);
  }

  public resetData() {
    anaSideReady.set(false);
    kernelStatus.reset();
    chatHistory.reset();
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
      operation: 'init'
    });
  }

  /**
   * Send a init command to the kernel
   */
  public sendMessageKernel(message: IChatMessage): void {
    this.send({
      operation: 'message',
      message: message as unknown as JSONObject
    });
  }

  /**
   * Send a cell execution command to the kernel
   */
  public sendExecKernel(): void {
    this.send({
      operation: 'exec'
    });
  }

  /**
   * Send a refresh command to the kernel
   */
  public sendRefreshKernel(): void {
    this.send({
      operation: 'refresh'
    });
  }

  /**
   * Send a supermode command to the kernel
   */
   public sendSupermode(data: any): void {
    data.operation = 'supermode';
    this.send(data);
  }


  /**
   * Send a subject query command to the kernel
   */
   public sendSubjectQuery(requestId: number, query: string): void {
    this.send({
      operation: 'query',
      type: 'subject',
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
  private _receiveAnaChatQuery(
    msg: KernelMessage.ICommMsgMsg
  ): void | PromiseLike<void> {
    try {
      const operation = msg.content.data.operation;
      if (operation === 'init' || operation === 'refresh') {
        kernelStatus.setattr('hasKernel', true);
        chatHistory.load(msg.content.data.history as unknown as IChatMessage[]);
        anaQueryEnabled.set(msg.content.data.query_processing_enabled as unknown as boolean);
        anaMessageEnabled.set(msg.content.data.message_processing_enabled as unknown as boolean);
        anaLoading.set(msg.content.data.loading as unknown as (boolean | number)[]);
        anaAutoLoading.set(msg.content.data.auto_loading as unknown as boolean);
      } else if (operation === 'reply') {
        kernelStatus.setattr('hasKernel', true);
        const message: IChatMessage = msg.content.data
          .message as unknown as IChatMessage;
        chatHistory.push(message);
      } else if (operation === 'error') {
        errorHandler.report(
          'Failed to run ICOMM command',
          '_receiveAnaChatQuery',
          [msg.content.data.command, msg.content.data.message]
        );
      } else if (operation === 'subjects') {
        const { responseId, sitems } = get(subjectItems);
        responseId.set(msg.content.data.responseId as number);
        sitems.set(msg.content.data.items as unknown as IAutoCompleteItem[]);
      }
    } catch (error) {
      throw errorHandler.report(error, '_receiveAnaChatQuery', [msg]);
    }
  }

  /*
   * Invokes a inspection if the signal emitted from specified session is an 'execute_input' msg.
   */
  private _queryCall(
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
  }
}
