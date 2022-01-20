import * as React from 'react';
import { LabIcon } from '@jupyterlab/ui-components';
import {
  neverconnectedIcon,
  disconnectedIcon,
  kerneloffIcon,
  kernelonIcon
} from '../iconimports';
import { ErrorHandler } from '../errorhandler';
import { Dialog, showDialog } from '@jupyterlab/apputils';

export interface IAnaChatStatus {
  connectedOnce: boolean;
  connectedNow: boolean;
  serverSide: boolean;
  hasKernel: boolean;
}

export interface IAnaChatStatusProps extends IAnaChatStatus {
  errorHandler: ErrorHandler;
}

export const KERNEL_CONNECTED = 'Kernel connected';

export function statusMessage(status: IAnaChatStatus): [string, LabIcon] {
  if (!status.connectedOnce) {
    return ['Ana did not connect to a notebook', neverconnectedIcon];
  }
  if (!status.connectedNow) {
    return ['Ana is not connected to a notebook', disconnectedIcon];
  }
  if (!status.hasKernel) {
    return ['Kernel not found', kerneloffIcon];
  }
  return [KERNEL_CONNECTED, kernelonIcon];
}

export class StatusRenderer extends React.Component<IAnaChatStatusProps> {
  chooseMessageIcon(): [string, LabIcon] {
    try {
      return statusMessage(this.props);
    } catch (error) {
      throw this.props.errorHandler.report(
        error,
        'StatusRenderer:chooseMessageIcon',
        []
      );
    }
  }

  clickError(): void {
    try {
      const text = this.props.errorHandler.errorStack.join('\n\n');

      showDialog({
        title: 'List of errors',
        body: (
          <div>
            <div>Please, submit the following log as a Bug report to</div>
            <div>
              <a
                target="_blank"
                rel="noreferrer"
                href="https://github.com/JoaoFelipe/anachat/issues"
              >
                https://github.com/JoaoFelipe/anachat/issues
              </a>
            </div>
            <textarea className="anachat-error-text" value={text} />
            <div>* Check the Browser console as well.</div>
          </div>
        ),
        buttons: [
          Dialog.cancelButton({ label: 'Dismiss' }),
          Dialog.okButton({ label: 'Clear' })
        ]
      }).then(result => {
        Promise.resolve(result.button.accept).then((ok: boolean) => {
          try {
            if (ok) {
              this.props.errorHandler.clear();
              this.forceUpdate();
            }
          } catch (error) {
            throw this.props.errorHandler.report(
              error,
              'StatusRenderer:clickError.ok',
              [ok]
            );
          }
        });
      });
    } catch (error) {
      throw this.props.errorHandler.report(
        error,
        'StatusRenderer:clickError',
        []
      );
    }
  }

  render(): JSX.Element | null {
    try {
      const [message, icon] = this.chooseMessageIcon();
      let error: JSX.Element | null = null;

      if (this.props.errorHandler.errorStack.length > 0) {
        error = (
          <span
            className="anachat-error-display"
            onClick={this.clickError.bind(this)}
            title="Click to see errors"
          >
            [Error]
          </span>
        );
      }

      return (
        <div className="jp-AnaChat-kernel" title={message}>
          {error}
          <icon.react
            elementSize="normal"
            className="anachat-icon"
            elementPosition="center"
          />
        </div>
      );
    } catch (error) {
      throw this.props.errorHandler.report(error, 'StatusRenderer:render', []);
    }
  }
}
