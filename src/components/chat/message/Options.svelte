<script type="ts">
  import type { IChatMessage, IOptionItem } from "../../../common/anachatInterfaces";
  import Default from "./Default.svelte";
  import { chatHistory } from "../../../stores";
  import ChatInput from "../ChatInput.svelte";
  export let message: IChatMessage;
  
  let width: number;
  let textarea: HTMLElement|null = null;

  const click = (element: IOptionItem) => (): void => {
    if ($chatHistory[$chatHistory.length - 1] == message) {
      chatHistory.addNew({
        id: crypto.randomUUID(),
        text: element.label,
        type: 'user',
        prevent: false,
        timestamp: +new Date(),
        force: false,
        hidden: false,
        reply: message.id
      })
    } else {
      chatHistory.addNew({
        id: crypto.randomUUID(),
        text: '!choose ' + element.key,
        type: 'user',
        prevent: false,
        timestamp: +new Date(),
        force: false,
        hidden: false,
        reply: message.id
      })
    }
  }

  const items: IOptionItem[] = message.text as IOptionItem[];
</script>

<style>
  div.button {
    flex: 1 0 100%;
    padding-left: 5px;
  }

  .button:first-child {
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
  }

  .button:last-child {
    border-bottom-left-radius: 3px;
    border-bottom-right-radius: 3px;
  }

  .button:not(:first-child) {
    border-top: 1px solid black;
  }
  
  div.button:hover {
    background-color: #D0FDFF;
    cursor: pointer;
  }

  .inner {
    display: flex;
    flex-wrap: wrap;
    padding-right: 5px;
    border: 1px solid #333;
    margin: 2px;
    border-radius: 3px;
  }

  .text {
    padding-right: 3px;
    padding-left: 2px;
  }

  .text :global(.subtext) {
    box-sizing: border-box;
    position: relative;
    vertical-align: top;
  }

  .text :global(textarea) {
    border: 1px solid #777;
  }

</style>

<Default {message} bind:width>
  <div> Suggestions (clickable): </div>
  <div class="inner">
    {#each items as element}
      <div class="button" on:click={click(element)} title={element.key}>
        {element.label}
      </div>
    {/each}
  </div>
  <div class="text">
    <ChatInput value="" replyto={message.id} bind:textarea={textarea} subclass="subtext" placeholder="Ask a different question"/>
  </div>
</Default>