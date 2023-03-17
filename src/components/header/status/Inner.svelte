<script lang="ts">
  import Error from "./Error.svelte";
  import { wizardMode } from "../../../stores";
  export let title: string;

  function contextMenu(event: MouseEvent) {
    if (event.ctrlKey) {
      if ($wizardMode) {
        alert("Wizardmode disabled!");
        $wizardMode = false;
      } else if (confirm("Do you want to enable Newton wizardmode?")) {
        $wizardMode = true;
      }
    }
  }

</script>

<style>
  .icon {
    height: 16px;
    width: 16px;
    margin-right: 8px;
    align-items: center;
  }
</style>

<div {title} class="outer" on:contextmenu|preventDefault={contextMenu}>
  <Error/>
  <div class="icon">
      <slot></slot>
  </div>
</div>