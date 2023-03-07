<script lang="ts">
  import Error from "./Error.svelte";
  import { wizardMode } from "../../../stores";
  export let title: string;

  function contextMenu(event: MouseEvent) {
    if (event.ctrlKey) {
      if ($wizardMode) {
        alert("Supermode disabled!");
        $wizardMode = false;
      } else if (confirm("Do you want to enable Newton supermode?")) {
        $wizardMode = true;
      }
    }
  }

</script>

<style>
  .outer {
    float: right;
  }
  .icon {
    float: left;
    height: 12px;
    width: 12px;
    margin-right: 8px;
    align-items: center;
    display: flex;
  }
</style>

<div {title} class="outer" on:contextmenu|preventDefault={contextMenu}>
  <Error/>
  <div class="icon">
      <slot></slot>
  </div>
</div>