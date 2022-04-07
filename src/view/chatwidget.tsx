import { IChatMessage } from '../interfaces';
import { MessageWidget } from './messagewidget';
import { Panel, Widget } from '@lumino/widgets';
import { OptionsMessageWidget } from './optionsmessagewidget';
import { CodeCell } from '@jupyterlab/cells';
import { ContentFactory, IContentFactory, ModelFactory } from './cellutils';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { KernelMessage } from '@jupyterlab/services';
import { each } from '@lumino/algorithm';
import { IObservableList, ObservableList } from '@jupyterlab/observables';
import { Signal } from '@lumino/signaling';
import { ISessionContext } from '@jupyterlab/apputils';

interface IChatProps {
  messages: IChatMessage[];
  sendText: (text: string) => void;
  rendermime: IRenderMimeRegistry;
  sessionContext: ISessionContext | null;
}


export class ChatWidget extends Panel {
  private messages: IChatMessage[];
  private sendText: (text: string) => void;
  private contentFactory: IContentFactory;
  private modelFactory: ModelFactory;
  private rendermime: IRenderMimeRegistry;
  private _cells: IObservableList<CodeCell>;
  private _executed = new Signal<this, Date>(this);
  private sessionContext: ISessionContext | null;

  constructor(options: IChatProps) {
    super();
    this.messages = options.messages;
    this.sendText = options.sendText;
    this.rendermime = options.rendermime;
    this.sessionContext = options.sessionContext;
    this.contentFactory = new ContentFactory();
    this.modelFactory = new ModelFactory({});
    this._cells = new ObservableList<CodeCell>();
    this.create();
  }

  create(): void {
    this.addClass('jp-anachat-content');
    this.messages.forEach(this.addMessage.bind(this));
  }

  addMessage(message: IChatMessage): void {
    if (message.type === 'options') {
      this.addWidget(
        new OptionsMessageWidget({ message, sendText: this.sendText })
      );
    } else if ((message.type === 'cell') && (this.sessionContext != null)) {
      let cell: CodeCell = this._createCodeCell();
      cell.model.value.text = message.text as string;

      cell.model.contentChanged.connect(this.update, this);
      const onSuccess = (value: void | KernelMessage.IExecuteReplyMsg) => {
        if (this.isDisposed) {
          return;
        }
        if (value && value.content.status === 'ok') {
          const content = value.content;
          // Use deprecated payloads for backwards compatibility.
          if (content.payload && content.payload.length) {
            const setNextInput = content.payload.filter(i => {
              return (i as any).source === 'set_next_input';
            })[0];
            if (setNextInput) {
              const text = (setNextInput as any).text;
              // Ignore the `replace` value and always set the next cell.
              cell.model.value.text = text;
            }
          }
        } else if (value && value.content.status === 'error') {
          each(this._cells, (cell: CodeCell) => {
            if (cell.model.executionCount === null) {
              cell.setPrompt('');
            }
          });
        }
        cell.model.contentChanged.disconnect(this.update, this);
        this.update();
        this._executed.emit(new Date());
      };
      const onFailure = () => {
        if (this.isDisposed) {
          return;
        }
        cell.model.contentChanged.disconnect(this.update, this);
        this.update();
      };
      CodeCell.execute(cell, this.sessionContext).then(
        onSuccess,
        onFailure
      );
      this.addWidget(cell);
    } else {
      this.addWidget(new MessageWidget({ message }));
    }
  }

  refresh(messages: IChatMessage[]) {
    let diff = messages.filter(x => !this.messages.includes(x) );
    diff.forEach(this.addMessage.bind(this));
  }

  protected onChildAdded(msg: Widget.ChildMessage): void {
    setTimeout(() => {
      const node = this.node;
      node.scrollTop = node.scrollHeight - node.clientHeight;
    }, 300);
  }

  private _createCodeCellOptions(): CodeCell.IOptions {
    const contentFactory = this.contentFactory;
    const modelFactory = this.modelFactory;
    const model = modelFactory.createCodeCell({});
    const rendermime = this.rendermime;
    return { model, rendermime, contentFactory, placeholder: false };
  }

  private _createCodeCell(): CodeCell {
    const factory = this.contentFactory;
    const options = this._createCodeCellOptions();
    const cell = factory.createCodeCell(options);
    cell.readOnly = true;
    //cell.model.mimeType = this._mimetype;
    return cell;
  }
}
