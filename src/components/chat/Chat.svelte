
<script type="ts">
  import { beforeUpdate, afterUpdate } from 'svelte';
  import { chatHistory } from '../../stores';
  import Cell from './message/Cell.svelte';
  import Default from './message/Default.svelte';
  import Options from './message/Options.svelte';

  let div: HTMLElement;
  let autoscroll = true;

  beforeUpdate(() => {
    autoscroll = div && (div.offsetHeight + div.scrollTop) > (div.scrollHeight - 20);
  });

  export function scrollBottom() {
    if (autoscroll) div.scrollTo(0, div.scrollHeight);
  }

  afterUpdate(() => {
    scrollBottom();
  });

</script>

<style>
  div {
    overflow: auto;
    height: 100%;
    padding-top: 0.8em;
    scrollbar-gutter: stable;
  }
</style>

<div bind:this={div}>
  {#each $chatHistory as message}
    {#if message.type === 'options'}
      <Options {message}/>
    {:else if message.type === 'cell'}
      <Cell {message} {scrollBottom}/>
    {:else}
      <Default {message}/>
    {/if}
  {/each}
</div>