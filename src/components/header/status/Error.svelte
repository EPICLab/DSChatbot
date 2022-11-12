<script>
  import { clickError } from "./ErrorDialog.tsx"
  import { errorHandler } from "../../../stores";
</script>

<style>
  button {
    float: left;
    margin: 0 3px;

    background: none!important;
    border: none;
    padding: 0!important;
    cursor: pointer;
  }
  button:hover {
    cursor: pointer !important;
  }
</style>

{#if $errorHandler.length > 0}
  <button on:click|preventDefault={clickError} title="Click to see errors">[Error]</button>
{/if}