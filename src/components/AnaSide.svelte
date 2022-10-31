<script lang="ts">
  import { anaSideReady, anaSideModel, kernelStatus, anaRestrict } from '../stores';
  import Chat from './chat/Chat.svelte';
  import AutoCompleteInput from './chat/AutoCompleteInput.svelte';
  import Header from './header/Header.svelte';

  // Locals
  let name: string;
  $: if ($anaSideReady && $anaSideModel) {
    name = $anaSideModel.name;
  }
  $: ({ hasKernel } = $kernelStatus);
</script>

{#if $anaSideModel && ($anaRestrict === null || $anaRestrict === name) }
  <Header title="Ana - {name}"></Header>
  <Chat></Chat>
  {#if $hasKernel}
    <AutoCompleteInput></AutoCompleteInput>
  {/if}
{:else}
  <Header title="Ana"></Header>
  {#if $anaRestrict !== null}
    Currently, the chatbot only works on files named {$anaRestrict}.
  {/if}
{/if}
