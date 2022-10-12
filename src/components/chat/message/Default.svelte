<script type="ts">
  import type { IChatMessage } from "../../../common/anachatInterfaces";
import { anaTimes } from "../../../stores";
  export let message: IChatMessage;
  export let width = 100;

  let timestamp = message.timestamp;
  if (!Number.isInteger(timestamp)) {
    timestamp = timestamp * 1000;
  }
</script>

<style>
  .outer {
    padding: 0 10px;
    width: inherit;
  }

  .inner {
    border-radius: 5px;
    border: 1px solid gray;
    margin-bottom: 0.8em;
    padding: 0.4em;
    white-space: pre-line;
  }

  .user {
    margin-left: 4em;
    background-color: #D0FDFF;
    border-radius: 0.5rem 0.5rem 0 0.5rem;
  }

  .bot {
    margin-right: 4em;
    background-color: #F2F2F2;
    border-radius: 0.5rem 0.5rem 0.5rem 0;
  }


  .error {
    margin-right: 4em;
    background-color: lightpink;
    border-radius: 0.5rem 0.5rem 0.5rem 0;
  }

  .options {
    margin-right: 4em;
    background-color: #F2F2F2;
    border-radius: 0.5rem 0.5rem 0.5rem 0;
  }

  .hidden {
    border-style: dotted;
    border-color: red;
  }

  .timestamp-user {
    text-align: right;
  }
</style>

<div class="outer">
  {#if $anaTimes}
    <div class="timestamp-{message.type}"> { new Date(timestamp).toLocaleTimeString("en-US") } </div>
  {/if}
  <div class:hidden={message.hidden} class="inner {message.type}" bind:clientWidth={width}>
    <slot>
      {#if message.type !== 'user'}
        {@html message.text}
      {:else}
        {message.text}
      {/if}
    </slot>
  </div>
</div>