import { Widget } from '@lumino/widgets';
import Main from './Main.svelte';

export class MainView extends Widget {
  constructor() {
    super();
    this.addClass('jp-NewtonChat');
    new Main({
      target: this.node,
      props: {}
    });  

  }
}
