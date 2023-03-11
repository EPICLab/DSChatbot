<script lang="ts">
  import { createChatInstance, type IChatInstance } from "../chatinstance";
  import type { ILoaderForm } from "../common/chatbotInterfaces";
  import type { NotebookCommModel } from "../dataAPI/NotebookCommModel";
  import AutoCompleteInput from "./chat/AutoCompleteInput.svelte";
  import Chat from "./chat/Chat.svelte";
  import Header from './header/Header.svelte';
  import IconButton from "./IconButton.svelte";
  import DynamicInput from "./jsonform/DynamicInput.svelte";

  export let model: NotebookCommModel;

  const chatInstances = model.chatInstances;
  const chatLoaders = model.chatLoaders;
  let chatInstance: IChatInstance | null = null;
  let instanceName: string | null;
  let mode: string = "";
  let newForm: ILoaderForm | null = null;

  let formValues: { [id: string]: {
    type: string,
    value: any
  } } = {};

  function deselectEverything() {
    instanceName = null;
    chatInstance = null;
    newForm = null;
  }

  function refreshLoaders() {
    model.refresh();
  }

  function selectExisting(key: string) {
    mode = "existing:" + key;
    instanceName = key;
    chatInstance = $chatInstances[key]
    if (chatInstance) {
      chatInstance.refresh();
      $chatInstance = $chatInstance;
    }
    newForm = null;
  }

  function selectMode() {
    if (mode.startsWith("existing:")) {
      selectExisting(mode.substring("existing:".length));
      newForm = null;
    } else if (mode.startsWith("new:")) {
      instanceName = null;
      chatInstance = null;
      newForm = $chatLoaders[mode.substring("new:".length)] || {};
      for (const [key, [type_, config]] of Object.entries(newForm)) {
        formValues[key] = {type: type_, value: config.value};
      }

    } else {
      deselectEverything();
    }
  }

  function createInstance() {
    let newKey = crypto.randomUUID();
    let newMode = mode.substring("new:".length);
    $chatInstances[newKey] = createChatInstance(model, newKey, newMode);
    let data: { [id: string]: string | null } = {};
    for (const [key, { value }] of Object.entries(formValues)) {
      data[key] = value;
    }
    model.sendCreateInstance(newKey, newMode, data);
    selectExisting(newKey);
  }

  function removeInstance() {
    if ((instanceName !== null) && confirm(`Do you want to remove ${instanceName}?`)) {
      model.sendRemoveInstance(instanceName)
    }
  }

  

  chatInstances.subscribe((newValue) => {
    if ((instanceName !== null) && !(instanceName in newValue)) {
      deselectEverything();
      mode = "";
    }
  })

  chatLoaders.subscribe((newValue) => {
    if (mode.startsWith("new:")) {
      const loader = mode.substring("new:".length);
      if (!(loader in newValue)) {
        deselectEverything();
        mode = "";
      }
    }
  })


</script>

<div class="panel">
  <div class="selector">
    <label>
      Chat mode:
      <select bind:value={mode} on:change={selectMode}>
        {#each Object.entries($chatInstances) as [key, instance] }
          <option value="existing:{key}">Existing: {instance.mode} ({key})</option>
        {/each}
        {#each Object.keys($chatLoaders) as loader }
          <option value="new:{loader}">Create: {loader}</option>
        {/each}
      </select>
    </label>
    <IconButton
      title="Refresh"
      on:click={refreshLoaders}>↻</IconButton>

    {#if chatInstance && (mode !== 'existing:base')}
      <IconButton
        title="Remove"
        on:click={removeInstance}>❌</IconButton>
    {/if}
  </div>

  {#if newForm }
  <form>
    {#each Object.entries(newForm) as [key, [type, config]] (key)}
      <DynamicInput {key} {type} {config} bind:value={formValues[key].value}/>
    {/each}
    <button on:click|preventDefault={createInstance}>Create</button>
  </form>
  {/if}

  {#if chatInstance}
    <Header {chatInstance} title="{chatInstance.mode} - {model.name }" showConfigs={false}/>
    <Chat {chatInstance}/>
    <AutoCompleteInput {chatInstance}/>
  {/if}
</div>

<style>
  .panel {
    height: 100%;
  }

  .selector {
    padding: 1em;
    display: flex;
    flex-wrap: wrap;
  }

  form {
    padding: 0 1em;
  }

  button {
    cursor: pointer;
  }

  label {
    display: flex;
    box-sizing: border-box;
  }
</style>