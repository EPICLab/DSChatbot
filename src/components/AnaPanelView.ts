import { Widget } from '@lumino/widgets';
import { panelWidget } from '../stores';
import AnaPanel from './AnaPanel.svelte';

export class AnaPanelView extends Widget {
  private _panel: AnaPanel;
  private _detached: boolean;
  
  constructor(url: string, title: string) {
    super();
    this._detached = false;
    this._panel = new AnaPanel({
      target: this.node,
      props: {
        url: url,
        title: title
      }
    });
    this._panel.$on('detach', event => {
      panelWidget.set(null);
      this._detached = true;
    })
  }

  set_props(url: string, title: string) {
    this._panel.$set({ url, title });
  }

  dispose(): void {
    if (!this._detached) {
      panelWidget.set(null);
    }
    super.dispose();
  }
}
