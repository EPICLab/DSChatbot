<script lang="ts">
  import { anaSideReady, anaSideModel, kernelStatus } from '../stores';
  import Chat from './chat/Chat.svelte';
  import ChatInput from './chat/ChatInput.svelte';
  import Header from './header/Header.svelte';

  // Locals
  let name: string;
  $: if ($anaSideReady && $anaSideModel) {
    name = $anaSideModel.name;
  }
  $: ({ hasKernel } = $kernelStatus);
</script>

{#if $anaSideModel}
  <Header title="Ana - {name}"></Header>
  <Chat></Chat>
  {#if $hasKernel}
    <ChatInput></ChatInput>
  {/if}
{:else}
  <Header title="Ana"></Header>
{/if}
