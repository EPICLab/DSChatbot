<script lang="ts">
  import { notebookCommModel, wizardMode } from "../../stores";
  import Renderer from "./status/Renderer.svelte";
  import { onKeyPress } from '../../common/utils';
  import { openPanel } from "../SveltePanelView";
  import type { IChatInstance } from "../../chatinstance";
  import ExtraChatPanel from "../ExtraChatPanel.svelte";
  import WizardCellPanel from "../WizardCellPanel.svelte";
  import IconButton from "../IconButton.svelte";

  export let chatInstance: IChatInstance;
  export let title: string;
  export let showConfigs: boolean = true;
  
  let { processInKernel, enableAutoComplete, showReplied, showIndex, showTime, showBuildMessages, showKernelMessages, enableAutoLoading, loading } = chatInstance.config;

  function openExtraChat() {
    const model = $notebookCommModel;
    if (model) {
      openPanel(ExtraChatPanel, "Extra chat", { model });
    }
    
  }

  function openWizardCell() {
    const model = $notebookCommModel;
    if (model) {
      openPanel(WizardCellPanel, "Wizard cell", { model });
    }
  }

  function toggleWizardConfigs() {
    showConfigs = !showConfigs;
  }

  const refresh = (): void => {
    $notebookCommModel?.refresh();
  }
  
</script>

<div>
  <header>
    <div class="top">
      <div class="left">
      <div class="title" class:supermode={$wizardMode} on:click={refresh} on:keypress={(e) => onKeyPress(refresh, e)} title="Click to refresh">{title}</div>
        {#if $wizardMode}
          <IconButton
            title={showConfigs? "Hide configs" : "Show configs"}
            on:click={toggleWizardConfigs}
            selected={showConfigs}
          >⚙️</IconButton>
        {/if}
        {#if $loading}
          <span class="loading-icon">⌛️</span>
        {/if}
      </div>
      <div class="middle">
      </div>
      <div class="right">
        <Renderer/>
      </div>
    </div>
    {#if $wizardMode && showConfigs}
      <div>
        <label>
          <input type=checkbox bind:checked={$processInKernel}>
          Message
        </label>
        <label>
          <input type=checkbox bind:checked={$enableAutoComplete}>
          Autocomplete
        </label>
        <label>
          <input type=checkbox bind:checked={$enableAutoLoading}>
          Auto Loading
        </label>
        <label>
          <input type=checkbox bind:checked={$showTime}> 
          Time
        </label>
      </div>
      <div>
        <label>
          <input type=checkbox bind:checked={$loading}>
          Loading
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
          <input type=checkbox bind:checked={$showReplied}> 
          Reply
        </label>
        <label>
          <input type=checkbox bind:checked={$showIndex}> 
          Index
        </label>
      </div>
      <div>
        <button on:click={openExtraChat}>Extra Chat</button>
        <button on:click={openWizardCell}>Wizard cell</button>
      </div>
    {/if}
  </header>
  
</div>

<style>
  .top {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  .top > div {
    align-items: center;
    justify-content: center;
    display: flex;
    text-align: center;
    min-height: 16px;

  }

  header {
    border-bottom: var(--jp-border-width) solid var(--jp-border-color2);
    flex: 0 0 auto;
    font-size: var(--newton-title-font-size);
    font-weight: 600;
    letter-spacing: 1px;
    margin: 0px;
    padding: 4px 0 4px 12px;
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

  .loading-icon {
    font-size: 2em;
  }

  button {
    cursor: pointer;
  }

</style>