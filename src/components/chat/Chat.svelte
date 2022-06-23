
<script type="ts">
  import { beforeUpdate, afterUpdate } from 'svelte';
  import { chatHistory } from '../../stores';
  import Message from './message/Message.svelte';

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
    <Message {message} {scrollBottom}/>
  {/each}
</div>