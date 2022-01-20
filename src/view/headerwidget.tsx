import React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { IAnaChatStatus, StatusRenderer } from './statusrenderer';
import { ErrorHandler } from '../errorhandler';

export class HeaderWidget extends ReactWidget {
  update: () => void;
  jtitle: string;
  status: IAnaChatStatus;
  eh: ErrorHandler;

  constructor(
    jtitle: string,
    status: IAnaChatStatus,
    eh: ErrorHandler,
    update: () => void
  ) {
    super();
    this.jtitle = jtitle;
    this.update = update;
    this.status = status;
    this.eh = eh;
    this.addClass('anachat-header-widget');
  }

  titleClick(): void {
    this.update();
  }

  protected render(): JSX.Element {
    return (
      <header>
        <div
          className="anachat-title"
          onClick={this.titleClick.bind(this)}
          title="Click to refresh"
        >
          {this.jtitle}
        </div>
        <StatusRenderer {...this.status} errorHandler={this.eh} />
      </header>
    );
  }
}
