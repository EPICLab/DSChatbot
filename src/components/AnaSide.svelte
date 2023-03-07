<script lang="ts">
  import { anaSideReady, anaSideModel, kernelStatus, anaRestrict, wizardMode } from '../stores';
  import Chat from './chat/Chat.svelte';
  import AutoCompleteInput from './chat/AutoCompleteInput.svelte';
  import Header from './header/Header.svelte';
  import SuperChat from './chat/SuperChat.svelte';
  import type { IChatInstance } from '../common/anachatInterfaces';

  export let chatInstance: IChatInstance;

  let name: string;
  $: if ($anaSideReady && $anaSideModel) {
    name = $anaSideModel.name;
  }
  $: ({ hasKernel } = $kernelStatus);
</script>

{#if $anaSideModel && ($anaRestrict.length === 0 || $anaRestrict.includes(name)) }
  <Header {chatInstance} title="Newton - {name}"/>
  <Chat {chatInstance}/>
  {#if $hasKernel}
    {#if $wizardMode}
      <SuperChat {chatInstance}/>
    {:else}
      <AutoCompleteInput {chatInstance}/>
    {/if}
  {/if}
{:else}
  <Header {chatInstance} title="Newton"/>
  {#if $anaRestrict.length !== 0}
    Currently, the chatbot only works on files named {$anaRestrict.join(" or ")}.
  {/if}
{/if}
