<script lang="ts">
  import type { NotebookCommModel } from "../dataAPI/NotebookCommModel";
  import WizardModeCell from "./header/WizardModeCell.svelte";
  export let model: NotebookCommModel;

</script>

<div>
  Wizard cell: { model.name }
  <WizardModeCell { model } />
</div>

<style>
  div {
    padding: 1em;
  }

</style>