import { Widget } from '@lumino/widgets';
import { panelWidget } from '../stores';
import DocPanel from './DocPanel.svelte';

export class DocPanelView extends Widget {
  private _panel: DocPanel;
  private _detached: boolean;
  
  constructor(content: string, title: string, type: 'url' | 'html' | 'text') {
    super();
    this._detached = false;
    this._panel = new DocPanel({
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
