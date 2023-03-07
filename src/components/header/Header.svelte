<script lang="ts">
  import { notebookCommModel, wizardMode } from "../../stores";
  import Renderer from "./status/Renderer.svelte";
  import { onKeyPress } from '../../common/utils';
  import SuperModeCell from "./SuperModeCell.svelte";
  import type { IChatInstance } from "../../common/chatbotInterfaces";

  export let chatInstance: IChatInstance;
  export let title: string;
  export let debugReply: boolean = false;
  
  let { processInKernel, enableAutoComplete, showReplied, showIndex, showTime, showBuildMessages, showKernelMessages, enableAutoLoading, loading } = chatInstance.config;
  $: $showReplied = debugReply;
  $: $showIndex = debugReply;

  const refresh = (): void => {
    $notebookCommModel?.refresh();
  }
  
</script>

<style>
  header {
    border-bottom: var(--jp-border-width) solid var(--jp-border-color2);
    flex: 0 0 auto;
    font-size: var(--newton-title-font-size);
    font-weight: 600;
    letter-spacing: 1px;
    margin: 0px;
    padding: 12px 0 4px 12px;
  }

  .title {
    display: inline-block;
    text-transform: uppercase;

  }
  .title:hover {
    cursor: pointer;
  }

  .supermode {
    color: red;
  }

  div {
    overflow: initial !important;
  }

  span {
    font-size: 2em;
  }

</style>

<div>
  <header>
    <div class="title" class:supermode={$wizardMode} on:click={refresh} on:keypress={(e) => onKeyPress(refresh, e)} title="Click to refresh">{title}</div>
    <Renderer/>
    {#if $loading}
      <span>⌛️</span>
    {/if}
    
    {#if $wizardMode}
      <br>
      
      <label>
        <input type=checkbox bind:checked={$processInKernel}>
        Message
      </label>
      <label>
        <input type=checkbox bind:checked={$enableAutoComplete}>
        Autocomplete
      </label>
      <label>
        <input type=checkbox bind:checked={$loading}>
        Loading
      </label>
      <label>
        <input type=checkbox bind:checked={$enableAutoLoading}>
        Auto Loading
      </label>

      <label>
        <input type=checkbox bind:checked={$showTime}> 
        Time
      </label>
      <label>
        <input type=checkbox bind:checked={$showKernelMessages}> 
        Kernel
      </label>
      <label>
        <input type=checkbox bind:checked={$showBuildMessages}> 
        Build
      </label>
      <label>
        <input type=checkbox bind:checked={debugReply}> 
        Debug
      </label>
      <br>
      <SuperModeCell/>
    {/if}
  </header>
</div>