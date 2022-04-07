import { IChatMessage } from '../interfaces';
import { MessageWidget } from './messagewidget';
import { Panel, Widget } from '@lumino/widgets';
import { OptionsMessageWidget } from './optionsmessagewidget';
import { Cell } from '@jupyterlab/cells';
import { ContentFactory, IContentFactory, ModelFactory } from './cellutils';

interface IChatProps {
  messages: IChatMessage[];
  sendText: (text: string) => void;
}


export class ChatWidget extends Panel {
  private messages: IChatMessage[];
  private sendText: (text: string) => void;
  private contentFactory: IContentFactory;
  private modelFactory: ModelFactory;

  constructor(options: IChatProps) {
    super();
    this.messages = options.messages;
    this.sendText = options.sendText;
    this.contentFactory = new ContentFactory();
    this.modelFactory = new ModelFactory({});
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
    } else if (message.type === 'cell') {
      let cell: Cell = this._createCodeCell();
      cell.model.value.text = message.text as string;

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

  /*private _createCodeCellOptions(): CodeCell.IOptions {
    const contentFactory = this.contentFactory;
    const modelFactory = this.modelFactory;
    const model = modelFactory.createCodeCell({});
    const rendermime = this.rendermime;
    return { model, rendermime, contentFactory, placeholder: false };
  }*/

  private _createCodeCell(): Cell {
    const factory = this.contentFactory;
    //const options = this._createCodeCellOptions();
    const modelFactory = this.modelFactory;
    const cell = factory.createRawCell({
      model: modelFactory.createRawCell({}),
    });
    cell.readOnly = true;
    cell.model.mimeType = "text/x-python";
    return cell;
  }
}
