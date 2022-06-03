<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();
  export let url: string;
  export let title: string;
  
  let detached = false;

  const toolbarcls = "lm-Widget p-Widget jp-Toolbar jp-NotebookPanel-toolbar";
  function detach() {
    if (!detached) {
      detached = true;
		  dispatch('detach');
    }
	}
</script>

<style>
  iframe {
    width: 100%;
    height: 100%;
  }
</style>

<div class={toolbarcls}>
  {#if !detached}
    <button on:click={detach} title="Allows the creation of other panels without replacing this one"> Keep </button>
  {/if}
  URL: {url}
</div>
<iframe src={ url } { title }></iframe>
