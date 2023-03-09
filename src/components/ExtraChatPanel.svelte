<script lang="ts">
  import { createChatInstance } from "../chatinstance";
  import type { IChatInstance, ILoaderForm } from "../common/chatbotInterfaces";
  import type { NotebookCommModel } from "../dataAPI/NotebookCommModel";
  import AutoCompleteInput from "./chat/AutoCompleteInput.svelte";
  import Chat from "./chat/Chat.svelte";

  // ToDo: add wizardmod

  export let model: NotebookCommModel;

  const chatInstances = model.chatInstances;
  const chatLoaders = model.chatLoaders;
  let chatInstance: IChatInstance | null = null;
  let instanceName: string | null;
  let mode: string = "";
  let newForm: ILoaderForm | null = null;

  let formValues: { [id: string]: {
    type: string,
    value: string | null
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
    chatInstance.refresh();
    $chatInstance = $chatInstance;
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
      for (const [key, [type_, defval]] of Object.entries(newForm)) {
        formValues[key] = {type: type_, value: defval};
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
    if (instanceName !== null) {
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

{ model.name }

<div class="panel">

<div>
  <button on:click={refreshLoaders}>Refresh</button>
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
</div>

{#if newForm }
<form>
  {#each Object.entries(newForm) as [key, [type, _]] (key)}
    {#if type == "str"}
      <label>{key}: <input type=text bind:value={formValues[key].value}></label>
    {/if}
    <br>
  {/each}
  <button on:click|preventDefault={createInstance}>Create</button>
</form>
{/if}


{#if chatInstance}
  {#if mode !== 'existing:base'}
    <button on:click={removeInstance}>Remove</button>
  {/if}
  <Chat {chatInstance}/>
  <AutoCompleteInput {chatInstance}/>
{/if}

</div>

<style>
  .panel {
    height: 100%;

  }

  button {
    cursor: pointer;
  }
</style>