<script lang="ts">
  import { anaSideReady, anaSideModel, kernelStatus, anaRestrict, anaSuperMode } from '../stores';
  import Chat from './chat/Chat.svelte';
  import AutoCompleteInput from './chat/AutoCompleteInput.svelte';
  import Header from './header/Header.svelte';
  import SuperChat from './chat/SuperChat.svelte';

  // Locals
  let name: string;
  $: if ($anaSideReady && $anaSideModel) {
    name = $anaSideModel.name;
  }
  $: ({ hasKernel } = $kernelStatus);
</script>

{#if $anaSideModel && ($anaRestrict.length === 0 || $anaRestrict.includes(name)) }
  <Header title="Newton - {name}"/>
  <Chat/>
  {#if $hasKernel}
    {#if $anaSuperMode}
      <SuperChat/>
    {:else}
      <AutoCompleteInput/>
    {/if}
  {/if}
{:else}
  <Header title="Newton"/>
  {#if $anaRestrict.length !== 0}
    Currently, the chatbot only works on files named {$anaRestrict.join(" or ")}.
  {/if}
{/if}
