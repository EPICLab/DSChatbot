import React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { IChatMessage } from '../interfaces';

interface IMessageProps {
  message: IChatMessage;
}

export class MessageWidget extends ReactWidget {
  private message: IChatMessage;

  constructor(options: IMessageProps) {
    super();
    this.message = options.message;
    this.addClass('anachat-message');
  }

  protected render(): JSX.Element {
    const className = `anachat-message-inner anachat-message-${this.message.type}`;
    return <div className={className}>{this.message.text}</div>;
  }
}
