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
  
    .inner {
        margin-bottom: 0.8em;
    }

    .inner :global(.jp-InputArea-prompt) {
      flex: none;
      padding: 0;
    }
  
    .inner :global(.CodeMirror) {
      z-index: 0;
      font-size: 1em;
    }

    .inner :global(.jp-Cell) {
        padding: 0;
    }

    .inner :global(.jp-InputCollapser) {
        display: none;
    }

    .inner :global(.jp-InputArea-editor) {
        border-radius: 5px;
        border: 1px solid gray;
        white-space: pre-line;
    }

    .inner.usercode :global(.CodeMirror) {
      background-color: #D0FDFF;
    }

    .inner.usercode :global(.jp-InputArea-editor) {
        border-radius: 0.5rem 0.5rem 0 0.5rem;
    }
  
    .usercode {
        margin-left: 4em;
    }

    .botcode {
        margin-right: 4em;
    }

    .inner.botcode :global(.CodeMirror) {
      background-color: #F2F2F2;
    }

    .inner.botcode :global(.jp-InputArea-editor) {
        border-radius: 0.5rem 0.5rem 0.5rem 0;
    }
  

    
  </style>
  
  <div class="outer">
    <div class="inner {message.type}" bind:this={div}/>
  </div>