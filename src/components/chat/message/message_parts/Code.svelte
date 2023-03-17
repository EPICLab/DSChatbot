<script type="ts">
  import { onMount, tick } from 'svelte';
  import type { IMessagePart } from "../../../../common/chatbotInterfaces";
  import { notebookCommModel } from "../../../../stores";
  import { ContentFactory, ModelFactory } from "../cellutils";
  import Above from "../../../icons/above.svelte";
  import Below from "../../../icons/below.svelte";
  import Bottom from "../../../icons/bottom.svelte";
  import Copy from "../../../icons/fa-copy.svelte";

  export let messagePart: IMessagePart;
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
    cell.model.value.text = messagePart.text;
    div.appendChild(cell.node)
    if (scrollBottom) {
      await tick();
      await new Promise(r => setTimeout(r, 100));
      await tick();
      scrollBottom();
    }
  });

  function onClickInsertAbove() {
    $notebookCommModel?.insertAbove(messagePart.text as string);
  }

  function onClickInsertBelow() {
    $notebookCommModel?.insertBelow(messagePart.text as string);
  }

  function onClickInsertBottom() {
    $notebookCommModel?.insertBottom(messagePart.text as string);
  }

  function onClickCopy() {
    navigator.clipboard.writeText(messagePart.text as string);
  }

</script>

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

  button {
    border: none;
    background: none;
  }

  button:hover {
    background-color: #ccc;
    cursor: pointer;
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

<div class="outer" class:direct={direct}>
  <div class="inner" bind:this={div}/>
  {#if !direct}
    <div class="buttons">
      <button on:click|preventDefault={onClickCopy} title="Copy to Clipboard">
        <Copy/>
      </button>
      <button on:click|preventDefault={onClickInsertAbove} title="Insert Cell Above">
        <Above/>
      </button>
      <button on:click|preventDefault={onClickInsertBelow} title="Insert Cell Below">
        <Below/>
      </button>
      <button on:click|preventDefault={onClickInsertBottom} title="Insert Cell at the Bottom">
        <Bottom/>
      </button>
    </div>
  {/if}
</div>