<script lang="ts">
  import { anaSideModel, anaSuperMode, anaQueryEnabled, anaMessageEnabled } from "../../stores";
  import Renderer from "./status/Renderer.svelte";

  export let title: string;

  function superModeToggleAutoComplete(event: any) {
    $anaSideModel?.sendSupermode({ query_processing: event.target.checked });
  }
  
  function superModeToggleMessage(event: any) {
    $anaSideModel?.sendSupermode({ message_processing: event.target.checked });
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
    text-transform: uppercase;
  }

  .title {
    display: inline-block;
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
</style>

<div>
  <header>
    <div class="title" class:supermode={$anaSuperMode} on:click={refresh} title="Click to refresh">{title}</div>
    <Renderer/>

    {#if $anaSuperMode}
    <br>
    <label>
      <input type=checkbox on:change={superModeToggleAutoComplete} checked={$anaQueryEnabled}>
      Autocomplete
    </label>
    <label>
      <input type=checkbox on:change={superModeToggleMessage} checked={$anaMessageEnabled}>
      Message
    </label>
    {/if}
  </header>
</div>