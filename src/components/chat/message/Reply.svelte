<script type="ts">
  import type { IChatInstance } from "../../../chatinstance";
  import type { IChatMessage } from "../../../common/chatbotInterfaces";
  import MessageParts from "./MessageParts.svelte";

  export let chatInstance: IChatInstance;
  export let reply: IChatMessage;
  export let scrollBottom: () => void;
  export let chat: HTMLElement | null = null;

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

    if (chat) {
      const element: HTMLElement = chat.getElementsByClassName(`message-${reply.id}`)[0] as HTMLElement;
      blink(element);
      chat.scrollTop = Math.max(0, element.offsetTop - 30);
    }
  }

</script>

<div 
  class="reply {reply.type}" 
  title="Click to go to message"
  role="button"
  aria-pressed="false"
  on:click={scroll}
  on:keypress={scroll}
>
  <div class="disable-click">
    <MessageParts {chatInstance} message={reply} preview={false} {scrollBottom}/>
  </div>
</div>

<style>
  .reply {
    margin: 2px;
    padding: 5px;
    filter: brightness(90%);
    border-radius: 0.5rem;
  }

  .reply:hover {
    cursor: pointer;
  }
  
  .user {
    background-color: var(--newton-message-user-color);
  }

  .bot {
    background-color: var(--newton-message-bot-color);
  }
  
  .error {
    background-color: var(--newton-message-error-color);
  }

  .disable-click {
    pointer-events: none;
  }
</style>