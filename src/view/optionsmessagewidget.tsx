import React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { IChatMessage, IOptionItem } from '../interfaces';

export interface IMessageProps {
  message: IChatMessage;
  sendText: (text: string) => void;
}

export class OptionsMessageWidget extends ReactWidget {
  private message: IChatMessage;
  private sendText: (text: string) => void;

  constructor(options: IMessageProps) {
    super();
    this.message = options.message;
    this.sendText = options.sendText;
    this.addClass('anachat-message');
  }

  protected render(): JSX.Element {
    const className = 'anachat-message-inner anachat-message-options';
    const options = this.message.text as IOptionItem[];
    const optionsDiv = options.map(el => {
      const key = 'option-' + el.key;
      return (
        <div
          className="anachat-option-item"
          key={key}
          onClick={() => {
            this.sendText(el.label);
          }}
        >
          {el.key}. {el.label}
        </div>
      );
    });
    console.log(this.message);
    return <div className={className}>{optionsDiv}</div>;
  }
}
