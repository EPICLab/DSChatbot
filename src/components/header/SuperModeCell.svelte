<script lang="ts">
  import { onMount } from "svelte";
  import { ContentFactory, execute_cell, ModelFactory } from "../chat/message/cellutils";
  import { jupyterRenderMime, anaSideModel } from "../../stores";
  import type { CodeCell } from "@jupyterlab/cells";

  let div: HTMLElement;
  let cell: CodeCell | null = null;

  let display: boolean = false;

  function _onEditorKeydown(editor: any, event: KeyboardEvent) {
    if (event.shiftKey && event.keyCode === 13 && cell && $anaSideModel?.session) {
      execute_cell(cell, $anaSideModel?.session)
      return true;
    }
  }

  onMount(async () => {
    if (!$jupyterRenderMime) {
      return;
    }
    const factory = new ContentFactory();
    const modelFactory = new ModelFactory({});
    const rendermime = $jupyterRenderMime;
    const options = {
      model: modelFactory.createCodeCell({}),
      rendermime,
      contentFactory: factory,
      placeholder: false
    };
    cell = factory.createCodeCell(options);
    cell.model.mimeType = "text/x-python";
    cell.model.value.text = '';
    const editor = cell.editor;
    editor!.addKeydownHandler(_onEditorKeydown as any);
    div.appendChild(cell.node)
  })
</script>

<style>
  .super-cell {
    display: none;
  }

  .super-cell.visible {
    display: block;
  }

  .super-cell :global(.jp-InputArea-prompt) {
    display: none;
  }

  .super-cell :global(.jp-InputCollapser) {
    display: none;
  }

  .super-cell :global(.jp-OutputPrompt) {
    display: none;
  }

  .super-cell :global(.jp-Cell) {
    padding: 0;
  }

  .super-cell :global(.CodeMirror) {
    z-index: 0;
    font-size: 1em;
  }

</style>


<label>
  <input type=checkbox bind:checked={display}> 
  Super Cell
</label>
<div class:visible={display} class="super-cell" bind:this={div}/>
