<script type="ts">
  import { onMount, tick } from 'svelte';
  import type { IChatMessage } from "../../../common/anachatInterfaces";
  import { ContentFactory, ModelFactory } from "./cellutils";
  import { anaSideModel } from "../../../stores";
  import Above from "../../icons/above.svelte";
  import Below from "../../icons/below.svelte";
  import Bottom from "../../icons/bottom.svelte";
  import Copy from "../../icons/copy.svelte";
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

  function onClickInsertAbove() {
    $anaSideModel?.insertAbove(message.text as string);
  }

  function onClickInsertBelow() {
    $anaSideModel?.insertBelow(message.text as string);
  }

  function onClickInsertBottom() {
    $anaSideModel?.insertBottom(message.text as string);
  }

  function onClickCopy() {
    navigator.clipboard.writeText(message.text as string);
  }
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

  button {
    border: none;
    background: none;
  }

  button:hover {
    background-color: #ccc;
    cursor: pointer;
  }

  .buttons {
    padding: 0 20px;
  }

</style>

<div class="outer">
  <div class="inner {message.type}" bind:this={div}/>
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
</div>