<script lang="ts">
  import { anaSideModel, kernelStatus } from "../../../stores";
  import Disconnected from "../../icons/disconnected.svelte";
  import Kerneloff from "../../icons/kerneloff.svelte";
  import Kernelon from "../../icons/kernelon.svelte";
  import Neverconnected from "../../icons/neverconnected.svelte";
  import Inner from "./Inner.svelte";

  $: ({ connectedOnce, connectedNow, hasKernel } = $kernelStatus);
  $: if ($anaSideModel) {
    $connectedNow = true;
  }

</script>


{#if $anaSideModel}
  {#if !$connectedOnce}
    <Inner title="Ana did not connect to a notebook">
      <Neverconnected/>
    </Inner>
  {:else if !$connectedNow}
    <Inner title="Ana is not connected to a notebook">
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