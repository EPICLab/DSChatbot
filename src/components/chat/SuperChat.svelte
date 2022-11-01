<script lang="ts">
  import type { IChatMessage, IMessageType, IOptionItem } from "../../common/anachatInterfaces";
  import { chatHistory, anaSideModel, anaAutoLoading, anaSuperMode } from "../../stores";
  import Message from "./message/Message.svelte";
  import { tick } from "svelte";

  export let textarea: HTMLElement;
  export let value: string;

  let superModeType: IMessageType | 'ordered' = 'bot';
  let superModeErrorMessage: string = "";
  let superModeOptionId = 0;
  let superModeHide: boolean = false;
  let superModePreviewMessage: IChatMessage[] = [];

  function createMessage(text: string): IChatMessage | null {
    let result: string | IOptionItem[];
    superModeErrorMessage = "";
    text = text.trim();
    if (text === '') {
      return null;
    }

    if ($anaSuperMode && (superModeType === 'options' || superModeType === 'ordered')){
      if (text[0] !== '-' && text[0] !== '!') {
        superModeErrorMessage = 'You must start the options by "-"';
        return null;
      }
      let options: IOptionItem[] = [];
      let lines = text.substring(1).trim().split("\n-");
      options = lines.map((line, index) => {
        let newText = line.trim();
        if (superModeType == 'ordered') {
          newText = (index + 1) + '. ' + newText;
        }
        return {
          'key': `SU-${superModeOptionId++}: ${newText}`,
          'label': newText
        }
      })
      result = options;
    } else {
      result = text;
    }
    
    let mestype: IMessageType = (superModeType === 'ordered') ? 'options' : superModeType;

    return {
      text: result,
      type: mestype,
      prevent: true,
      hidden: superModeHide,
      force: superModeHide,
      timestamp: +new Date()
    }
  }

  async function handleKeydown(e: any) {
    let key = e.key;
    if (e.altKey) {
      if (key === "a") {
        superModeType = "bot"
        textarea.focus();
      } else if (key === "o") {
        superModeType = "ordered"
        textarea.focus();
      } else if (key === "i") {
        superModeType = "options"
        textarea.focus();
      } else if (key === "c") {
        superModeType = "cell"
        textarea.focus();
      } else if (key === "u") {
        superModeType = "user"
        textarea.focus();
      } else if (key === "e") {
        superModeType = "error"
        textarea.focus();
      } else if (key === "h") {
        superModeHide = !superModeHide;
        textarea.focus();
      }
    }
    if ((document.activeElement == textarea) && (key === "Enter") && e.ctrlKey) {
      await onSuperModeSend();
    }
  }

  function onClickHereIsTheCode() {
    superModeType = 'bot';
    let message = createMessage("Copy the following code to the notebook:");
    if (message !== null) {
      superModePreviewMessage = [...superModePreviewMessage, message];
      superModeType = 'cell';
    }
    textarea.focus();
  }

  function onClickContinue() {
    superModeType = 'ordered';
    value = '- Continue'
    textarea.focus();
  }

  function removePreview(index: number) {
    superModePreviewMessage.splice(index, 1);
    superModePreviewMessage = superModePreviewMessage;
  }

  async function onSuperModeSend() {
    let timestamp = +new Date()
    superModePreviewMessage.forEach((message: IChatMessage) => {
      message.timestamp = timestamp;
      chatHistory.addNew(message);
    })
    superModePreviewMessage = [];
    if ($anaAutoLoading) {
      $anaSideModel?.sendSupermode({ loading: false });
    }
    await tick();
  }

  export function enterMessage(text: string): boolean {
    let message = createMessage(text);
    if (message !== null) {
      superModePreviewMessage = [...superModePreviewMessage, message];
      return true;
    }
    return false;
  }


</script>


<style>

  .error {
    color: red;
  }

  .supermodetypes {
    display: flex;
  }

</style>

<label>
  <input type=checkbox bind:checked={superModeHide} value="hide">
  Send hidden message to chatbot
</label>
<div class="supermodetypes">
  <label>
    <input type=radio bind:group={superModeType} name="messageType" value="bot">
    Ana
  </label>
  <label>
    <input type=radio bind:group={superModeType} name="messageType" value="ordered">
    Ordered
  </label>
  <label>
    <input type=radio bind:group={superModeType} name="messageType" value="options">
    Items
  </label>
  <label>
    <input type=radio bind:group={superModeType} name="messageType" value="cell">
    Code
  </label>
  <label>
    <input type=radio bind:group={superModeType} name="messageType" value="user">
    User
  </label>
  <label>
    <input type=radio bind:group={superModeType} name="messageType" value="error">
    Error
  </label>
  <button on:click|preventDefault={onClickHereIsTheCode}>Code</button>
  <button on:click|preventDefault={onClickContinue}>Continue</button>
</div>
{#if superModeErrorMessage}
<div class="error">
  {superModeErrorMessage}
</div>
{/if}


<button on:click|preventDefault={onSuperModeSend}>Send Messages (ctrl + enter)</button>
{#each superModePreviewMessage as message, i}
  <Message {message} remove={() => removePreview(i)}/>
{/each}


<svelte:window on:keydown={handleKeydown}/>