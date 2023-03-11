<script lang="ts">
  import { notebookCommModel, wizardMode } from "../../stores";
  import Renderer from "./status/Renderer.svelte";
  import { onKeyPress } from '../../common/utils';
  import { openPanel } from "../SveltePanelView";
  import type { IChatInstance } from "../../chatinstance";
  import ExtraChatPanel from "../ExtraChatPanel.svelte";
  import WizardCellPanel from "../WizardCellPanel.svelte";
  import IconButton from "../IconButton.svelte";
  import DynamicInput from "../jsonform/DynamicInput.svelte";

  export let chatInstance: IChatInstance;
  export let title: string;
  export let showConfigs: boolean = true;
  export let showLoadConfig: boolean = false;
  
  let { processInKernel, enableAutoComplete, showReplied, showIndex, showTime, showBuildMessages, showKernelMessages, enableAutoLoading, loading, showMetadata, processBaseChatMessage } = chatInstance.config;
  let loadInput: HTMLInputElement;
  let loadInstancesData: any = null;
  let loadForms: [string, {[id: string]: [string, any]}, {[id: string]: any}][] = [];

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

  function toggleLoadConfig() {
    showLoadConfig = !showLoadConfig;
  }

  const refresh = (): void => {
    $notebookCommModel?.refresh();
  }

  function findForms(data: any, currentKey: string) {
    if (data == null) {
      return
    } else if (Array.isArray(data)) {
      for (const [i, element] of data.entries()) {
        findForms(element, `${currentKey}[${i}]`);
      }
    } else if (typeof data == "object") {
      for (const [key, value] of Object.entries(data)) {
        if (key == "!form") {
          const formDef = structuredClone(value) as {[id: string]: [string, any]};
          const valueAny: any = value as any;
          for (const [formKey, formValue] of Object.entries(valueAny)) {
            valueAny[formKey] = (formValue as any)[1].value;
          }
          loadForms = [...loadForms, [`${currentKey}.${key}`, formDef, valueAny]]
        } else if (!key.startsWith('!!')) {
          findForms(value, `${currentKey}.${key}`);
        }
      }
    }
  }

  function prepareForms() {
    const files = loadInput.files
    if (files == null) {
      loadInstancesData = null;
      loadForms = [];
      return;
    }
    const file = files[0];
    if (file == null) {
      loadInstancesData = null;
      loadForms = [];
      return;
    }
    const reader = new FileReader();
    reader.addEventListener("load", function () {
      try {
        loadInstancesData = JSON.parse(reader.result as string);
        loadForms = [];
        findForms(loadInstancesData, '.')
        console.log(loadForms)
      } catch (e) {
        console.log(e)
        loadInstancesData = null;
        loadForms = [];
      }
    });
    reader.readAsText(file);
  }

  function loadInstances() {
    $notebookCommModel?.sendLoadInstances(loadInstancesData);
    loadForms = [];
    loadInstancesData = null;
    showLoadConfig = false;
  }

  function saveInstances() {
    $notebookCommModel?.sendSaveInstances();
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
          {#if showConfigs}
            <IconButton
              title={showLoadConfig? "Close load intances form" : "Load instances from file"}
              on:click={toggleLoadConfig}
              selected={showLoadConfig}
            >📂</IconButton>
            <IconButton
              title="Save instances"
              on:click={saveInstances}
            >💾</IconButton>
          {/if}
          
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
      {#if showLoadConfig}
        <div>
          <input bind:this={loadInput} type=file on:change={prepareForms}> 
          <div>
            {#each loadForms as [formkey, configs, formdata] (formkey)}
              {#each Object.entries(configs) as [key, [type, config]] (key)}
               <DynamicInput {key} {type} {config} bind:value={formdata[key]}/>
              {/each}
            {/each}
          </div>
          <button on:click={loadInstances} disabled={loadInstancesData == null}>Load</button>
        </div>
      {/if}
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
        <label>
          <input type=checkbox bind:checked={$processBaseChatMessage}>
          Replicate base
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
        <label>
          <input type=checkbox bind:checked={$showMetadata}> 
          Metadata
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