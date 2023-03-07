import React from 'react';
import { get } from 'svelte/store';
import { Dialog, showDialog } from '@jupyterlab/apputils';

import { errorHandler } from '../../../stores';

export function clickError(): void {
  try {
    const text = get(errorHandler).join('\n\n');

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
          <textarea className="newton-error-text" value={text} />
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
            errorHandler.clear();
          }
        } catch (error) {
          throw errorHandler.report(error, 'StatusErrorDialog:clickError.ok', [
            ok
          ]);
        }
      });
    });
  } catch (error) {
    throw errorHandler.report(error, 'StatusErrorDialog:clickError', []);
  }
}
