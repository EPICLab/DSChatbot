<script lang="ts">
  import type { NotebookCommModel } from "../dataAPI/NotebookCommModel";
  import SuperModeCell from "./header/SuperModeCell.svelte";
  export let model: NotebookCommModel;

</script>

<div>
  Wizard cell: { model.name }
  <SuperModeCell { model } />
</div>

<style>
  div {
    padding: 1em;
  }

</style>