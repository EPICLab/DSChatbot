<script lang="ts">
  import { notebookCommModel, kernelStatus } from "../../../stores";
  import Disconnected from "../../icons/disconnected.svelte";
  import Kerneloff from "../../icons/kerneloff.svelte";
  import Kernelon from "../../icons/kernelon.svelte";
  import Neverconnected from "../../icons/neverconnected.svelte";
  import Inner from "./Inner.svelte";

  $: ({ connectedOnce, connectedNow, hasKernel } = $kernelStatus);
  $: if ($notebookCommModel) {
    $connectedNow = true;
  }

</script>


{#if $notebookCommModel}
  {#if !$connectedOnce}
    <Inner title="Newton did not connect to a notebook">
      <Neverconnected/>
    </Inner>
  {:else if !$connectedNow}
    <Inner title="Newton is not connected to a notebook">
      <Disconnected/>
    </Inner>
  {:else if !$hasKernel}
    <Inner title="Kernel not found">
      <Kerneloff/>
    </Inner>
  {:else}
    <Inner title="Kernel connected">
      <Kernelon/>
    </Inner>
  {/if}
{/if}