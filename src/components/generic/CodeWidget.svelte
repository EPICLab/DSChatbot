<script type="ts">
  import { onMount, tick } from 'svelte';
  import Below from "../icons/below.svelte";
  import Bottom from "../icons/bottom.svelte";
  import Copy from "../icons/fa-copy.svelte";
  import { notebookCommModel } from '../../stores';
  import { ContentFactory, ModelFactory } from '../chat/message/cellutils';
  import Above from '../icons/above.svelte';
  import IconButton from './IconButton.svelte';

  export let code: string;
  export let scrollBottom: () => void;
  export let direct: boolean = false;

  let div: HTMLElement;
  onMount(async () => {
    const factory = new ContentFactory();
    const modelFactory = new ModelFactory({});

    const cell = factory.createRawCell({
      model: modelFactory.createRawCell({}),
    });
    cell.readOnly = true;
    cell.model.mimeType = "text/x-python";
    cell.model.value.text = code;
    div.appendChild(cell.node)
    if (scrollBottom) {
      await tick();
      await new Promise(r => setTimeout(r, 100));
      await tick();
      scrollBottom();
    }
  });

  function onClickInsertAbove() {
    $notebookCommModel?.insertAbove(code as string);
  }

  function onClickInsertBelow() {
    $notebookCommModel?.insertBelow(code as string);
  }

  function onClickInsertBottom() {
    $notebookCommModel?.insertBottom(code as string);
  }

  function onClickCopy() {
    navigator.clipboard.writeText(code as string);
  }

</script>
  
  
  
<div class="outer" class:direct={direct}>
  <div class="inner" bind:this={div}/>
  {#if !direct}
    <div class="buttons">
      <IconButton on:click={onClickCopy} title="Copy to Clipboard"><Copy/></IconButton>
      <IconButton on:click={onClickInsertAbove} title="Insert Cell Above"><Above/></IconButton>
      <IconButton on:click={onClickInsertBelow} title="Insert Cell Below"><Below/></IconButton>
      <IconButton on:click={onClickInsertBottom} title="Insert Cell at the Bottom"><Bottom/></IconButton>
    </div>
  {/if}
</div>


<style>
  .inner :global(.jp-InputArea-prompt) {
    display: none;
  }

  .inner :global(.jp-InputCollapser) {
    display: none;
  }

  .inner :global(.jp-Cell) {
    padding: 0;
  }

  .outer :global(.CodeMirror) {
    z-index: 0;
    font-size: 1em;
  }

  .buttons {
    display: flex;
  }

  .direct :global(.CodeMirror) {
    background: none;
  }

  .direct :global(.jp-InputArea-editor) {
    border: none;
    background: none;
    white-space: pre-line;
  }
</style>