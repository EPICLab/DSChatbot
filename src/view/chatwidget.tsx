import { IChatMessage } from '../interfaces';
import { MessageWidget } from './messagewidget';
import { Panel, Widget } from '@lumino/widgets';
import { OptionsMessageWidget } from './optionsmessagewidget';

interface IChatProps {
  messages: IChatMessage[];
  sendText: (text: string) => void;
}

export class ChatWidget extends Panel {
  private messages: IChatMessage[];
  private sendText: (text: string) => void;

  constructor(options: IChatProps) {
    super();
    this.messages = options.messages;
    this.sendText = options.sendText;
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
    } else {
      this.addWidget(new MessageWidget({ message }));
    }
  }

  protected onChildAdded(msg: Widget.ChildMessage): void {
    setTimeout(() => {
      const node = this.node;
      node.scrollTop = node.scrollHeight - node.clientHeight;
    }, 300);
  }
}
