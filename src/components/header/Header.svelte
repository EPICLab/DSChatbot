<script lang="ts">
  import { notebookCommModel, wizardMode } from "../../stores";
  import Renderer from "./status/Renderer.svelte";
  import { onKeyPress } from '../../common/utils';
  import { openPanel } from "../SveltePanelView";
  import type { IChatInstance } from "../../chatinstance";
  import ExtraChatPanel from "../ExtraChatPanel.svelte";
  import WizardCellPanel from "../WizardCellPanel.svelte";
  import IconButton from "../generic/IconButton.svelte";
  import DynamicInput from "../jsonform/DynamicInput.svelte";
  import ToggleButton from "../generic/ToggleButton.svelte";
  import Robot from "../icons/fa-robot.svelte";
  import Save from "../icons/fa-save.svelte";
  import Load from "../icons/fa-load.svelte";
  import Cog from "../icons/fa-cog.svelte";
  import WizardCell from "../icons/wizardcell.svelte";

  export let chatInstance: IChatInstance;
  export let title: string;
  export let showConfigs: boolean = true;
  export let showLoadConfig: boolean = false;
  
  let { processInKernel, enableAutoComplete, showReplied, showIndex, showTime, showBuildMessages, showKernelMessages, enableAutoLoading, loading, showMetadata, processBaseChatMessage, directSendToUser } = chatInstance.config;
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
          ><Cog/></IconButton>
          {#if showConfigs}
            <IconButton
              title={showLoadConfig? "Close load intances form" : "Load instances from file"}
              on:click={toggleLoadConfig}
              selected={showLoadConfig}
            ><Load/></IconButton>
            <IconButton
              title="Save instances"
              on:click={saveInstances}
            ><Save/></IconButton>
            <IconButton
              title="Open extra chat"
              on:click={openExtraChat}><Robot/></IconButton>
            <IconButton
              title="Open wizard cell"
              on:click={openWizardCell}><WizardCell/></IconButton>
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
        <ToggleButton bind:checked={$processInKernel} title="Automatically process message in kernel">Message</ToggleButton>
        <ToggleButton bind:checked={$enableAutoComplete} title="Display autocomplete toggle to user">Autocomplete</ToggleButton>
        <ToggleButton bind:checked={$enableAutoLoading} title="Show loading icon in every received message">Auto Loading</ToggleButton>
        <ToggleButton bind:checked={$showTime} title="Show message time">Time</ToggleButton>
        <ToggleButton bind:checked={$processBaseChatMessage} title="Process user message from base chat">Replicate base</ToggleButton>
      </div>
      <div>
        <ToggleButton bind:checked={$loading} title="Toggle global loading icon">Loading</ToggleButton>
        <ToggleButton bind:checked={$showKernelMessages} title="Show kernel messages in wizard mode">Kernel</ToggleButton>
        <ToggleButton bind:checked={$showBuildMessages} title="Show build messages in wizard mode">Build</ToggleButton>
        <ToggleButton bind:checked={$showReplied} title="Show replied message in all messages">Reply</ToggleButton>
        <ToggleButton bind:checked={$showIndex} title="Show message index">Index</ToggleButton>
        <ToggleButton bind:checked={$showMetadata} title="Show message metadata">Metadata</ToggleButton>
        <ToggleButton bind:checked={$directSendToUser} title="Display button to send message directly to user">Direct send</ToggleButton>
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