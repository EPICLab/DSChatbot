<script type="ts">
  import { onMount, tick } from 'svelte';
  import type { IChatMessage } from "../../../common/anachatInterfaces";
  import { ContentFactory, ModelFactory } from "./cellutils";
  export let message: IChatMessage;
  export let scrollBottom: () => void;

  let div: HTMLElement;
  onMount(async () => {
    const factory = new ContentFactory();
    const modelFactory = new ModelFactory({});

    const cell = factory.createRawCell({
      model: modelFactory.createRawCell({}),
    });
    cell.readOnly = true;
    cell.model.mimeType = "text/x-python";
    cell.model.value.text = message.text as string;
    div.appendChild(cell.node)
    if (scrollBottom) {
      await tick();
      await new Promise(r => setTimeout(r, 100));
      await tick();
      scrollBottom();
    }
  });
</script>

<style>
  .outer {
    padding: 0 10px;
    width: inherit;
  }

  .inner :global(.jp-InputArea-prompt) {
    flex: none;
  }

  .outer :global(.CodeMirror) {
    z-index: 0;
  }

</style>

<div class="outer">
  <div class="inner {message.type}" bind:this={div}/>
</div>