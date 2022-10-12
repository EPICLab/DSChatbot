

<script type="ts">
  import type { IChatMessage } from '../../../common/anachatInterfaces';
  import { anaSuperMode } from '../../../stores';

  import Cell from './Cell.svelte';
  import Default from './Default.svelte';
  import Options from './Options.svelte';
  import UserCode from './UserCode.svelte';

  export let message: IChatMessage;
  export let scrollBottom: () => void = () => {};
  export let remove: (() => void) | null = null;
</script>

<style>
  span {
    height: 0px;
    position: relative;
    top: 5px;
    z-index: 1000;
  }

  span:hover {
    cursor: pointer;
  }

</style>

{#if remove}
<span on:click={remove}>❌</span>
{/if}

{#if !message.hidden || $anaSuperMode}
  {#if message.type === 'options'}
    <Options {message}/>
  {:else if message.type === 'cell'}
    <Cell {message} {scrollBottom}/>
  {:else if message.type === 'usercode' || message.type === 'botcode'}
    <UserCode {message} {scrollBottom}/>
  {:else}
    <Default {message}/>
  {/if}
{/if}