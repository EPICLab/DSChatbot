import { Widget } from '@lumino/widgets';
import { panelWidget } from '../stores';
import ExtraChatPanel from './ExtraChatPanel.svelte';

export class ExtraChatPanelView extends Widget {
  private _panel: ExtraChatPanel;
  private _detached: boolean;
  
  constructor() {
    super();
    this._detached = false;
    this._panel = new ExtraChatPanel({
      target: this.node,
      props: {}
    });
    this._panel.$on('detach', event => {
      panelWidget.set(null);
      this._detached = true;
    })
  }

  dispose(): void {
    if (!this._detached) {
      panelWidget.set(null);
    }
    super.dispose();
  }
}
