<script lang="ts">
  import { anaSideModel } from "../../stores";
  import Renderer from "./status/Renderer.svelte";

  export let title: string;

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

  div {
    overflow: initial !important;
  }
</style>

<div>
  <header>
    <div class="title" on:click={refresh} title="Click to refresh">{title}</div>
    <Renderer/>
  </header>
</div>