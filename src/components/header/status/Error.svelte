<script>
  import { clickError } from "./ErrorDialog.tsx"
  import { errorHandler } from "../../../stores";
</script>

<style>
  span {
    float: left;
    margin: 0 3px;
  }
  span:hover {
    cursor: pointer !important;
  }
</style>

{#if $errorHandler.length > 0}
  <span on:click={clickError} title="Click to see errors">[Error]</span>
{/if}