<script lang="ts">
  import { connectionReady, notebookCommModel, kernelStatus, restrictNotebooks, wizardMode } from '../stores';
  import Chat from './chat/Chat.svelte';
  import AutoCompleteInput from './chat/AutoCompleteInput.svelte';
  import Header from './header/Header.svelte';
  import SuperChat from './chat/SuperChat.svelte';
  import type { IChatInstance } from '../common/chatbotInterfaces';
  import { get } from 'svelte/store';

  let chatInstance: IChatInstance;
  let name: string;
  $: if ($notebookCommModel) {
    chatInstance = get($notebookCommModel.chatInstances)["base"]
  }
  $: if ($connectionReady && $notebookCommModel) {
    name = $notebookCommModel.name;
  }
  $: ({ hasKernel } = $kernelStatus);
</script>

{#if chatInstance}
  {#if $notebookCommModel && ($restrictNotebooks.length === 0 || $restrictNotebooks.includes(name)) }
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
    {#if $restrictNotebooks.length !== 0}
      Currently, the chatbot only works on files named {$restrictNotebooks.join(" or ")}.
    {/if}
  {/if}

{/if}
