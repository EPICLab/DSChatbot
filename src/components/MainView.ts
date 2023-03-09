import { get } from 'svelte/store';
import { Widget } from '@lumino/widgets';
import { chatInstances } from '../stores';
import Main from './Main.svelte';

export class MainView extends Widget {
  constructor() {
    super();
    this.addClass('jp-NewtonChat');
    new Main({
      target: this.node,
      props: {
        chatInstance: get(chatInstances)["base"]
      }
    });
  }
}
