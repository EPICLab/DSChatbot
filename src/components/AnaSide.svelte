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

{#if $anaSideModel && ($anaRestrict.length === 0 || $anaRestrict.includes(name)) }
  <Header title="Newton - {name}"></Header>
  <Chat></Chat>
  {#if $hasKernel}
    <AutoCompleteInput></AutoCompleteInput>
  {/if}
{:else}
  <Header title="Newton"></Header>
  {#if $anaRestrict.length !== 0}
    Currently, the chatbot only works on files named {$anaRestrict.join(" or ")}.
  {/if}
{/if}
