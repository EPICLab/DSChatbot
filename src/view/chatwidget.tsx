import { IChatMessage } from '../interfaces';
import { MessageWidget } from './messagewidget';
import { Panel } from '@lumino/widgets';

interface IChatProps {
  messages: IChatMessage[];
}

export class ChatWidget extends Panel {
  private messages: IChatMessage[];

  constructor(options: IChatProps) {
    super();
    this.messages = options.messages;
    this.create();
  }

  create(): void {
    this.addClass('jp-anachat-content');
    this.messages.forEach(this.addMessage.bind(this));
  }

  addMessage(message: IChatMessage): void {
    this.addWidget(new MessageWidget({ message }));
  }
}
