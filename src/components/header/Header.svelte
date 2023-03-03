<script lang="ts">
  import { anaSideModel, anaSuperMode, anaMessageEnabled, anaLoading, anaAutoLoading, anaTimes, anaShowKernelMessages, anaShowBuildMessages, anaDebugReply } from "../../stores";
  import Renderer from "./status/Renderer.svelte";
  import { onKeyPress } from '../../common/utils';
  import SuperModeCell from "./SuperModeCell.svelte";

  export let title: string;
  
  function superModeToggleMessage(event: any) {
    $anaSideModel?.sendSupermode({ message_processing: event.target.checked });
  }

  function superModeToggleLoading(event: any) {
    $anaSideModel?.sendSupermode({ loading: event.target.checked });
  }

  function superModeToggleAutoLoading(event: any) {
    $anaSideModel?.sendSupermode({ auto_loading: event.target.checked });
  }

  const refresh = (): void => {
    $anaSideModel?.refresh();
  }
  
</script>

<style>
  header {
    border-bottom: var(--jp-border-width) solid var(--jp-border-color2);
    flex: 0 0 auto;
    font-size: var(--anachat-title-font-size);
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
    <div class="title" class:supermode={$anaSuperMode} on:click={refresh} on:keypress={(e) => onKeyPress(refresh, e)} title="Click to refresh">{title}</div>
    <Renderer/>
    {#if $anaLoading.includes(true)}
      <span>⌛️</span>
    {/if}
    
    {#if $anaSuperMode}
      <br>
      
      <label>
        <input type=checkbox on:change={superModeToggleMessage} checked={$anaMessageEnabled}>
        Message
      </label>
      <label>
        <input type=checkbox on:change={superModeToggleLoading} checked={$anaLoading.length > 0}>
        Loading
      </label>
      <label>
        <input type=checkbox on:change={superModeToggleAutoLoading} checked={$anaAutoLoading}>
        Auto Loading
      </label>

      <label>
        <input type=checkbox bind:checked={$anaTimes}> 
        Time
      </label>
      <label>
        <input type=checkbox bind:checked={$anaShowKernelMessages}> 
        Kernel
      </label>
      <label>
        <input type=checkbox bind:checked={$anaShowBuildMessages}> 
        Build
      </label>
      <label>
        <input type=checkbox bind:checked={$anaDebugReply}> 
        Debug
      </label>
      <br>
      <SuperModeCell/>
    {/if}
  </header>
</div>