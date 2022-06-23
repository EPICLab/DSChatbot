

<script type="ts">
  import type { IChatMessage } from '../../../common/anachatInterfaces';
  import { anaSuperMode } from '../../../stores';

  import Cell from './Cell.svelte';
  import Default from './Default.svelte';
  import Options from './Options.svelte';

  export let message: IChatMessage;
  export let scrollBottom: () => void = () => {};
</script>

{#if !message.hidden || $anaSuperMode}
  {#if message.type === 'options'}
    <Options {message}/>
  {:else if message.type === 'cell'}
    <Cell {message} {scrollBottom}/>
  {:else}
    <Default {message}/>
  {/if}
{/if}