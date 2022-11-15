import { Widget } from '@lumino/widgets';
import { panelWidget } from '../stores';
import AnaPanel from './AnaPanel.svelte';

export class AnaPanelView extends Widget {
  private _panel: AnaPanel;
  private _detached: boolean;
  
  constructor(content: string, title: string, type: 'url' | 'html' | 'text') {
    super();
    this._detached = false;
    this._panel = new AnaPanel({
      target: this.node,
      props: {
        content,
        title,
        type
      }
    });
    this._panel.$on('detach', event => {
      panelWidget.set(null);
      this._detached = true;
    })
  }

  set_props(content: string, title: string, type: 'url' | 'html' | 'text') {
    this._panel.$set({ content, title, type });
  }

  dispose(): void {
    if (!this._detached) {
      panelWidget.set(null);
    }
    super.dispose();
  }
}
