<script type="ts">
  import { MessageDisplay, type IChatMessage} from "../../../common/chatbotInterfaces";
  import { replying, wizardMode } from "../../../stores";

  import MessageParts from "./MessageParts.svelte";

  import Robot from "../../icons/robot.svelte";
  import Person from "../../icons/person.svelte";
  import Eye from "../../icons/eye.svelte";
  import Reply from "../../icons/reply.svelte";
  import ThumbsUp from "../../icons/fa-thumbs-up-solid.svelte";
  import ThumbsDown from "../../icons/fa-thumbs-down-solid.svelte";
  import { messageTarget } from "../../../common/messages";
  import type { IChatInstance } from "../../../chatinstance";
  
  export let chatInstance: IChatInstance;
  export let message: IChatMessage
  export let preview: boolean = false
  export let scrollBottom: () => void
  export let width = 100;
  export let chat: HTMLElement | null = null;

  let { showReplied, showTime, enableAutoLoading } = chatInstance.config;

  let timestamp = message.timestamp;
  if (!Number.isInteger(timestamp)) {
    timestamp = timestamp * 1000;
  }

  let inner: IChatMessage | null | undefined = null;

  function select(e: any) {
    if ($replying == message.id) {
      $replying = null;
    } else {
      $replying = message.id;
    }
  }

  function blink(element: HTMLElement | null) {
    if (element) {
      element.onanimationend = () => {
        element.classList.remove("blink-message")
      }
      element.classList.add("blink-message")
    }
  }

  function scroll(event: any) {
    if (
      event instanceof KeyboardEvent &&
      event.key !== "Enter" &&
      event.key !== " "
    ) {
      return;
    }

    if (chat && message.reply) {
      const element: HTMLElement = chat.getElementsByClassName(`message-${message.reply}`)[0] as HTMLElement;
      blink(element);
      chat.scrollTop = Math.max(0, element.offsetTop - 30);
    }
  }

  function setReplyVisibility(visible: boolean) {
    if (visible) {
      inner = chatInstance.findById(message.reply);
    } else {
      inner = null;
    }
  }

  function toggleInner(event: any) {
    setReplyVisibility(!inner);
  }

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

  function thumbsUpClick(event: any) {
    message.feedback.rate = message.feedback.rate === 1? 0 : 1;
    chatInstance.submitSyncMessage({
      id: message.id,
      feedback: { rate: message.feedback.rate }
    })
  }

  function thumbsDownClick(event: any) {
    message.feedback.rate = message.feedback.rate === -1? 0 : -1;
    chatInstance.submitSyncMessage({
      id: message.id,
      feedback: { rate: message.feedback.rate }
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

  $: setReplyVisibility($showReplied && !preview);
  $: selected = $replying == message.id;
  

</script>

<div class="outer {message.type}">
  <div 
    class:hidden={message.display == MessageDisplay.Hidden} 
    class:build={message.display == MessageDisplay.SupermodeInput} 
    class:tobuild={message.kernelDisplay == MessageDisplay.SupermodeInput} 
    class="inner" bind:clientWidth={width}
  >
    <div class="main">
      
      {#if inner}
        <div 
          class="reply reply-{inner.type}" 
          title="Click to go to message"
          role="button"
          aria-pressed="false"
          on:click={scroll}
          on:keypress={scroll}
        >
          <div class="disable-click">
            <MessageParts {chatInstance} message={inner} preview={false} {scrollBottom}/>
          </div>
        </div>
      {/if}
      <MessageParts {chatInstance} {message} {preview} {scrollBottom}/>
    </div>

    {#if !preview}
      <div class="bottom">
        <div class="side">
          <div class="profile">
            {#if message.type == "user"} 
              <div class="profile-inner" title="You">
                <Person/>
              </div>
            {:else}
              <div class="profile-inner" title="Newton">
                <Robot/>
              </div>
            {/if}
          </div>

          <div class="buttons">
            {#if chat && message.reply}
              <button 
                title={inner === null? "View replied message" : "Hide replied message"} 
                class="icon" 
                class:selected={inner!==null}
                on:click={toggleInner}
              ><Eye/></button>
            {/if}

            <button 
              title={selected? "Replying to" : "Reply to"}
              class="icon"
              class:selected={selected} 
              class:hideuserreply={!$wizardMode && message.type == 'user'}
              on:click={select}
            ><Reply/></button>

            

          </div>

          {#if message.loading}
            <div class="loading" title="Processing message">⌛️</div>
          {/if}


        </div>
        
        <div class="timestamp timestamp-{message.type}">
          {#if !$wizardMode && message.type !== 'user'}
            <div class="feedback-btns">
              <button 
                title="Good reply"
                class="icon"
                class:selected={message.feedback.rate == 1} 
                on:click={thumbsUpClick}
              ><ThumbsUp/></button>
              <button 
                title="Bad reply"
                class="icon thumbsdown"
                class:selected={message.feedback.rate == -1} 
                on:click={thumbsDownClick}
              ><ThumbsDown/></button>
            </div>
          {/if}
          {#if $showTime}
            <span>{ new Date(timestamp).toLocaleTimeString("en-US") }</span>
          {/if}
        </div>
        
      </div>
      {#if message.feedback.rate == -1}
        <div class="rate">
          <label>Help me improve. Why did you rate the message this way?
            <select bind:value={message.feedback.reason} on:change={changeFeedback}>
              <option></option>
              <option>The message is incorrect</option>
              <option>The message is incomplete</option>
              <option>I cannot understand the message</option>
              <option>The message was not solicited</option>
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
    {/if}
  </div>
  
</div>

<style>
  button {
    cursor: pointer;
  }

  .icon {
    background: none!important;
    border: none;
    padding: 0!important;
    
    display: flex;
       
    align-items:center;
    justify-content:center;
    min-width: 25px;
  }

  .icon:focus {
    border-bottom: 1px dotted black;
  }

  .icon:hover {
    cursor: pointer;
  }
  
  .icon.hideuserreply {
    display: none;
  }

  .icon.selected :global(svg) {
    fill: green;
  }

  .thumbsdown.selected :global(svg) {
    fill: red;
  }

  .side {
    display: flex;
    flex-direction: row;
  }

  .side > div {
    height: 25px;
    min-width: 25px;
    text-align: center;
    display: flex;
       
    align-items:center;
    justify-content:center;
    
  }

  .profile{
    height:25px;
    width:25px;
    position:relative;
    overflow:hidden;
    
  }

  .bot .profile, .error .profile {
    border-right: 1px solid black;
  }

  .user .profile {
    border-left: 1px solid black;
  }
  
  .profile-inner {
    background-color: white;
    
    border-radius:50%;
    height:20px;
    width:20px;
    overflow:hidden;

    position:absolute;
    left:50%;
    top:50%;
    -webkit-transform:translateX(-50%) translateY(-50%);
    transform:translateX(-50%) translateY(-50%);
  }

  .bottom {
    height: 25px;
    border-top: 1px solid black;
    display: flex;
    justify-content: space-between;
    flex-direction: row;
  }

  .user .bottom, .user .side {
    flex-direction: row-reverse;
  }

  .timestamp {
    font-size: 0.8em;
    padding: 0.3em;
    display: flex;
  }

  .timestamp span {
    align-self: flex-end;
  }

  .main {
    padding: 0.4em;
  }

  .outer {
    padding: 0 10px;
    width: inherit;
  }

  .inner {
    border-radius: 5px;
    border: 1px solid gray;
    margin-bottom: 0.8em;
    
    white-space: pre-line;
  }

  .user .inner, .reply-user {
    background-color: #D0FDFF;
  }

  .user .profile-inner {
    border: 15px solid #D0FDFF;
  }

  .bot .inner, .reply-bot {
    background-color: #F2F2F2;
  }

  .bot .profile-inner{
    border: 15px solid #F2F2F2;
  }

  .error .inner, .reply-error {
    background-color: lightpink;
  }

  .error .profile-inner{
    border: 15px solid lightpink;
  }

  .user .inner {
    margin-left: 4em;
    border-radius: 0.5rem 0.5rem 0 0.5rem;
    flex-direction: row-reverse;
  }

  .bot .inner {
    margin-right: 4em;
    background-color: #F2F2F2;
    border-radius: 0.5rem 0.5rem 0.5rem 0;
  }

  .error .inner {
    margin-right: 4em;
    background-color: lightpink;
    border-radius: 0.5rem 0.5rem 0.5rem 0;
  }

  .hidden {
    border-style: dotted;
    border-width: 2px;
    border-color: red;
  }

  .build {
    border-style: dotted;
    border-width: 2px;
    border-color: blue;
  }

  .tobuild {
    border-style: dotted;
    border-width: 2px;
    border-color: green;
  }

  .timestamp-user {
    text-align: right;
  }

  .reply {
    margin: 2px;
    padding: 5px;
    filter: brightness(90%);
    border-radius: 0.5rem;
  }

  .reply:hover {
    cursor: pointer;
  }

  .disable-click {
    pointer-events: none;
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

  .feedback-btns {
    display: flex;
    flex-direction: row;
  }

</style>
