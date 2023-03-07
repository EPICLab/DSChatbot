<script lang="ts">
  import { renderText } from '@jupyterlab/rendermime';
  import { createEventDispatcher, onMount } from 'svelte';
  import { jupyterSanitizer } from '../stores';

  const dispatch = createEventDispatcher();
  export let content: string;
  export let title: string;
  export let type: 'url' | 'html' | 'text';
  
  let detached = false;
  let host: HTMLElement;

  const toolbarcls = "lm-Widget p-Widget jp-Toolbar jp-NotebookPanel-toolbar";
  function detach() {
    if (!detached) {
      detached = true;
		  dispatch('detach');
    }
	}

  onMount(async () => {
    if (type == 'text') {
      if ($jupyterSanitizer) {
        host.classList.add('jp-RenderedText')
        renderText({ host, sanitizer: $jupyterSanitizer, source: content}).catch(console.error);
      } else {
        host.innerHTML = content;
      }
    }
  })
</script>

<style>
  iframe {
    width: 100%;
    height: 100%;
  }

  .content {
    width: 100%;
    height: 100%;
    padding: 10px;
  }
</style>

<div class={toolbarcls}>
  {#if !detached}
    <button on:click={detach} title="Allows the creation of other panels without replacing this one"> Keep </button>
  {/if}
  {#if type == 'url'}
    URL: {content}
  {:else}
    { title }
  {/if}
</div>
{#if type == 'url'}
  <iframe src={ content } { title }></iframe>
{:else if type == 'html'}
  <div class="content">{@html content}</div>
{:else}
  <div bind:this={host} class="content"></div>
{/if}
