<script lang="ts">
  import { onMount } from "svelte";
  import { ContentFactory, execute_cell, ModelFactory } from "../chat/message/cellutils";
  import { jupyterRenderMime } from "../../stores";
  import type { CodeCell } from "@jupyterlab/cells";
  import type { NotebookCommModel } from "../../dataAPI/NotebookCommModel";

  export let model: NotebookCommModel;

  let div: HTMLElement;
  let cell: CodeCell | null = null;

  function _onEditorKeydown(editor: any, event: KeyboardEvent) {
    if (event.shiftKey && event.keyCode === 13 && cell && model.session) {
      execute_cell(cell, model.session)
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

<div class="super-cell" bind:this={div}/>
