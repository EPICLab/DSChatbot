import { JSONObject } from '@lumino/coreutils';
import { ISessionContext } from '@jupyterlab/apputils';
import { Signal } from '@lumino/signaling';
import { KernelMessage } from '@jupyterlab/services';
import {
  IComm,
  IKernelConnection
} from '@jupyterlab/services/lib/kernel/kernel';
import {
  IErrorMsg,
  IInfoReply
} from '@jupyterlab/services/lib/kernel/messages';
import { GenericMatcher, IChatMessage, IKernelMatcher } from './interfaces';
import { IDisposable } from '@lumino/disposable';
import { NotebookPanel } from '@jupyterlab/notebook';
import { ErrorHandler } from './errorhandler';

export class NotebookComm implements IDisposable {
  private _language: IKernelMatcher | null;

  private _kernelRestarted = new Signal<this, Promise<void>>(this);
  private _isDisposed = false;
  private _nbPanel: NotebookPanel;
  private _session: ISessionContext;
  private _ready: Promise<void>;
  private _update: () => void;
  private _addChatMessage: (message: IChatMessage) => void;
  private _eh: ErrorHandler;
  private _icomm: IComm | null;
  private _chatHistory: IChatMessage[];

  public hasKernel: boolean;

  _boundQueryCall: (
    sess: ISessionContext,
    args: KernelMessage.IMessage<KernelMessage.MessageType>
  ) => void;

  constructor(
    session: ISessionContext,
    nbPanel: NotebookPanel,
    eh: ErrorHandler,
    update: () => void,
    addChatMessage: (message: IChatMessage) => void
  ) {
    this._eh = eh;
    try {
      this.hasKernel = false;

      this._session = session;
      this._nbPanel = nbPanel;
      this._update = update;
      this._addChatMessage = addChatMessage;
      this._ready = new Promise((resolve, reject) => {
        // Empty function
      });
      this._language = GenericMatcher;
      this._icomm = null;
      this._boundQueryCall = this._queryCall.bind(this);

      session.statusChanged.connect(
        (sender: ISessionContext, status: KernelMessage.Status) => {
          if (status.endsWith('restarting')) {
            this._kernelRestarted.emit(this._session.ready);
          }
        }
      );

      this._chatHistory = [];
    } catch (error) {
      throw this._report(error, 'constructor', [nbPanel.title.label]);
    }
  }

  private _report(error: any, func: string, params: any): any {
    console.log('bbbbbbbbbbb', this._eh);
    return this._eh.report(error, 'NotebookComm:' + func, params);
  }

  getKernel(): Promise<IKernelConnection> {
    return new Promise((resolve, reject) => {
      const kernel = this._session.session?.kernel;
      if (kernel) {
        resolve(kernel);
      } else {
        reject('Kernel not found');
      }
    });
  }

  findLanguage(
    kernelName: string,
    languageName: string
  ): Promise<IKernelMatcher> {
    return new Promise((resolve, reject) => {
      if (kernelName.match('python') || languageName.match('python')) {
        resolve({
          language: 'python',
          initScript: 'import anachat.comm; anachat.comm.init()',
          evalue: "No module named 'anachat.comm'"
        });
        return;
      }
      resolve(GenericMatcher);
    });
  }

  getKernelLanguage(): Promise<IKernelMatcher> {
    try {
      return this.getKernel().then(kernel => {
        return kernel.info.then((infoReply: IInfoReply) => {
          return this.findLanguage(kernel.name, infoReply.language_info.name);
        });
      });
    } catch (error) {
      throw this._report(error, 'getKernelLanguage', []);
    }
  }

  createComm(): void {
    this.getKernel().then(kernel => {
      kernel.registerCommTarget('anachat.comm', (comm, msg) => {
        this._icomm = comm;
        this._icomm.onMsg = this._receiveAnaChatQuery.bind(this);
        // console.log('ICOMM!', this._icomm.commId);
      });
    });
  }

  configureHandler(language: IKernelMatcher): void {
    try {
      this._language = language;
      this._ready = this._session.ready.then(() => {
        this.createComm();
        this._initOnKernel();
      });

      this._kernelRestarted.connect(
        (sender: any, kernelReady: Promise<void>) => {
          this.hasKernel = false; // Restarting...
          this._update();

          this._ready = kernelReady.then(() => {
            this.createComm();
            this._initOnKernel();
          });
        }
      );
    } catch (error) {
      throw this._report(error, 'configureHandler', [language.language]);
    }
  }

  addMessage(newMessage: IChatMessage): void {
    this._chatHistory.push(newMessage);
    this._addChatMessage(newMessage);
    this.sendMessageKernel(newMessage);
  }

  get chatHistory(): IChatMessage[] {
    return this._chatHistory;
  }

  get name(): string {
    return this._session.path;
  }

  get nbPanel(): NotebookPanel {
    return this._nbPanel;
  }

  get isDisposed(): boolean {
    return this._isDisposed;
  }

  get ready(): Promise<void> {
    return this._ready;
  }

  /**
   * Disposes the kernel connector.
   */
  dispose(): void {
    try {
      if (this.isDisposed) {
        return;
      }
      this._isDisposed = true;
      Signal.clearData(this);
    } catch (error) {
      throw this._report(error, 'dispose', []);
    }
  }

  private _createPromise(error: any = null): Promise<any> {
    return new Promise<void>((resolve, reject) => {
      if (!error) {
        resolve();
      } else {
        reject(error);
      }
    });
  }

  private initScript(): Promise<void> {
    try {
      if (this._language === null) {
        return this._createPromise('Language not loaded');
      }
      const language = this._language;
      const code = language.initScript;
      console.log('init', code);
      if (code === null) {
        return this._createPromise();
      }
      const content: KernelMessage.IExecuteRequestMsg['content'] = {
        code: code,
        stop_on_error: false,
        store_history: false,
        silent: true
      };
      return this.getKernel()
        .then(kernel => {
          console.log(content);
          const future = kernel.requestExecute(content, false);
          future.onIOPub = (msg: KernelMessage.IIOPubMessage): void => {
            if (
              msg.header.msg_type === 'error' &&
              (msg as IErrorMsg).content.evalue === language.evalue
            ) {
              const err: IErrorMsg = msg as IErrorMsg;
              this._report(undefined, 'initScript', [
                err.content.ename,
                err.content.evalue,
                err.content.traceback
              ]);
            }
            this.sendInitKernel();
          };
          return future.done.then(() => {
            return;
          });
        })
        .catch(error => {
          return Promise.reject(new Error('Require kernel to run anachat!'));
        });
    } catch (error) {
      throw this._report(error, 'initScript', []);
    }
  }

  public send(data: JSONObject): void {
    const session = this._session.session;
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
   * Send a init command to the kernel
   */
  public sendRefreshKernel(): void {
    this.send({
      operation: 'refresh'
    });
  }

  /**
   * Initializes the kernel by running the set up script located at _initScriptPath.
   */
  private _initOnKernel(): Promise<void> {
    return this.initScript().then(() => {
      this._session.iopubMessage.disconnect(this._boundQueryCall);
      this._session.iopubMessage.connect(this._boundQueryCall);
    });
  }

  /*
   * Handle query response
   */
  private _receiveAnaChatQuery(
    msg: KernelMessage.ICommMsgMsg
  ): void | PromiseLike<void> {
    try {
      const operation = msg.content.data.operation;
      console.log('Receive op', operation);
      if (operation === 'init' || operation === 'refresh') {
        this.hasKernel = true;
        this._chatHistory = msg.content.data
          .history as unknown as IChatMessage[];
        this._update();
      } else if (operation === 'reply') {
        this.hasKernel = true;
        const message: IChatMessage = msg.content.data
          .message as unknown as IChatMessage;
        this._chatHistory.push(message);
        this._addChatMessage(message);
      } else if (operation === 'error') {
        this._report('Failed to run ICOMM command', '_receiveAnaChatQuery', [
          msg.content.data.command,
          msg.content.data.message
        ]);
      }
    } catch (error) {
      throw this._report(error, '_receiveAnaChatQuery', [msg]);
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
      throw this._report(error, '_queryCall', [args.content]);
    }
  }
}
