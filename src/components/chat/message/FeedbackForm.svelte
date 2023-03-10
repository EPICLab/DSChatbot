<script type="ts">
  import type { IChatInstance } from "../../../chatinstance";
  import type { IChatMessage } from "../../../common/chatbotInterfaces";
  import { messageTarget } from "../../../common/messages";


  export let chatInstance: IChatInstance;
  export let message: IChatMessage;

  let { enableAutoLoading } = chatInstance.config;
  let typingTimer: ReturnType<typeof setTimeout>;
  

  function feedback(event: any) {
    let feedback_msg = message.feedback.reason;
    if (feedback_msg == "Other") {
      feedback_msg = message.feedback.otherreason;
    }
    chatInstance.addNew({
      id: crypto.randomUUID(),
      text: `Feedback: ${feedback_msg}`,
      type: 'user',
      timestamp: +new Date(),
      reply: message.id,
      feedback: {
        rate: 0,
        reason: "",
        otherreason: ""
      },
      loading: $enableAutoLoading,
      ...messageTarget('bot')
    })
  }

  function changeFeedback() {
    chatInstance.submitSyncMessage({
      id: message.id,
      feedback: { 
        reason: message.feedback.reason,
        otherreason: message.feedback.otherreason
      }
    })
  }

  function feedbackkeyup() {
    clearTimeout(typingTimer);
    typingTimer =  setTimeout(changeFeedback, 3000);
  }

  function feedbackkeydown() {
    clearTimeout(typingTimer);
  }

</script>

{#if message.feedback.rate == -1}
  <div class="rate">
    <label>Help me improve. Why did you rate the message this way?
      <select bind:value={message.feedback.reason} on:change={changeFeedback}>
        <option></option>
        <option>The message is too basic</option>
        <option>The message is too advanced</option>
        <option>The message did not help</option>
        <option>I still do not know what to do</option>
        <option>Other</option>
      </select>
    </label>
    {#if message.feedback.reason === "Other"}
      <label>Other: <input type=text bind:value={message.feedback.otherreason} on:keydown={feedbackkeydown} on:keyup={feedbackkeyup}></label>
    {/if}
    <button 
      disabled={message.feedback.reason === "" || (message.feedback.reason === "Other" && message.feedback.otherreason === "")}
      on:click={feedback} 
      title="Submit feedback message to get a new reply with a new answer"
    >Submit as message</button>
  </div>
{/if}

<style>
  button {
    cursor: pointer;
  }

  .rate {
    border-top: 1px solid black;
  }

  .rate label {
    display: block;
    margin: 0.5em;
  }

  .rate button {
    display: block;
    margin: 0.5em;
  }

  .rate select, .rate input {
    max-width: 100%;
    width: 100%;
    box-sizing: border-box;
  }
</style>