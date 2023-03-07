import { Widget } from '@lumino/widgets';
import { chatInstances } from '../stores';
import AnaSide from './AnaSide.svelte';

export class AnaSideView extends Widget {
  constructor() {
    super();
    this.addClass('jp-AnaChat');
    new AnaSide({
      target: this.node,
      props: {
        chatInstance: chatInstances["base"]
      }
    });
  }
}
