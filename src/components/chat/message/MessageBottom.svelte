<script type="ts">
  import type { IChatInstance } from "../../../chatinstance";
  import type { IChatMessage } from "../../../common/chatbotInterfaces";
  import { cloneMessage, messageTarget } from "../../../common/messages";
  import { wizardMode, wizardPreviewMessage, wizardValue } from "../../../stores";
  import IconButton from "../../IconButton.svelte";
  import FeedbackButtons from "./FeedbackButtons.svelte";
  import FeedbackForm from "./FeedbackForm.svelte";
  import Profile from "./Profile.svelte";
  import ReplyButtons from "./ReplyButtons.svelte";

  export let chatInstance: IChatInstance;
  export let message: IChatMessage;
  export let index: number;
  export let viewReplied: boolean;

  let { showTime, showIndex } = chatInstance.config;
  let timestamp = message.timestamp;
  if (!Number.isInteger(timestamp)) {
    timestamp = timestamp * 1000;
  }

  function sendToBuild() {
    let newMessage = cloneMessage(message, messageTarget('user'))
    $wizardPreviewMessage = [...$wizardPreviewMessage, newMessage];
  }

  function sentToInput() {
    $wizardValue = message.text;
  }

</script>

<div class="bottom {message.type}">
  <div class="first">
    <Profile type={message.type} title={message.type == "user" ? "You" : chatInstance.mode}/>
    {#if $showIndex && $wizardMode}
      <div>{index}</div>
    {/if}
    <ReplyButtons {message} viewReplied={viewReplied} on:toggleViewReplied />
    {#if $wizardMode}
      <IconButton title="To build" on:click={sendToBuild}>🛠️</IconButton>
      <IconButton title="To input" on:click={sentToInput}>📝</IconButton>
    {/if}
    {#if message.loading}
      <div class="loading" title="Processing message">⌛️</div>
    {/if}
  </div>
  
  <div class="last">
    {#if message.type !== 'user'}
      <FeedbackButtons {chatInstance} {message}/>
    {/if}
    {#if $showTime}
      <span class="timestamp">{ new Date(timestamp).toLocaleTimeString("en-US") }</span>
    {/if}
  </div>
</div>
<FeedbackForm {chatInstance} {message}/>

<style>
  .bottom {
    height: 25px;
    border-top: 1px solid black;
    display: flex;
    justify-content: space-between;
    flex-direction: row;
  }

  .first {
    display: flex;
    flex-direction: row;
  }

  .first > :global(div) {
    height: 25px;
    min-width: 25px;
    text-align: center;
    display: flex;
       
    align-items: center;
    justify-content: center;
    
  }

  .last {
    font-size: 0.8em;
    padding: 0.3em;
    display: flex;
  }

  .last span {
    align-self: flex-end;
  }

  .user .timestamp {
    text-align: right;
  }

  div.user, .user .first {
    flex-direction: row-reverse;
  }
</style>