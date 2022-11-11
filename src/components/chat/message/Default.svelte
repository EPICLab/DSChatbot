<script type="ts">
  import { MessageDisplay, type IChatMessage } from "../../../common/anachatInterfaces";
  import { anaTimes, anaSuperMode, anaSideModel } from "../../../stores";
  export let message: IChatMessage;
  export let width = 100;
  export let loading = false;
  export let index: number | null = null;

  let timestamp = message.timestamp;
  if (!Number.isInteger(timestamp)) {
    timestamp = timestamp * 1000;
  }

  function clickLoading() {
    if (!$anaSuperMode || !toggleableLoading) return;
    if (loading) {
      $anaSideModel?.sendSupermode({ loading: false });
      loading = false;
    } else {
      $anaSideModel?.sendSupermode({ loading: index });
    }
  }

  $: toggleableLoading = ($anaSuperMode && (index !== null));
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

  .build {
    border-style: dotted;
    border-color: blue;
  }

  .timestamp-user {
    text-align: right;
  }

  
  .togglableLoading span {
    display: none;
  }

  .togglableLoading:hover span {
    display: inline-block;
  }

  span.clickable:hover {
    cursor: pointer;
  }
</style>

<div class="outer">
  {#if $anaTimes}
    <div class:togglableLoading={toggleableLoading && !loading} class="timestamp-{message.type}"> 
      { new Date(timestamp).toLocaleTimeString("en-US") }
      {#if loading || toggleableLoading}
        <span class:clickable={$anaSuperMode} on:click|preventDefault={clickLoading}>⌛️</span>
      {/if}
    </div>
  {/if}
  <div 
    class:hidden={message.display == MessageDisplay.Hidden} 
    class:build={message.display == MessageDisplay.SupermodeInput} 
    class="inner {message.type}" bind:clientWidth={width}
  >
    <slot>
      {#if message.type !== 'user'}
        {@html message.text}
      {:else}
        {message.text}
      {/if}
    </slot>
  </div>
</div>