<script lang="ts">
  import type { IChatMessage, IMessageType } from "../../common/anachatInterfaces";
  import { chatHistory, anaSideModel, anaAutoLoading, replying, superModePreviewMessage } from "../../stores";
  import Message from "./message/Message.svelte";
  import { tick } from "svelte";
  import { BOT_TARGETS, BOT_TYPES, messageTarget, type IMessageTarget } from "../../common/messages";

  export let textarea: HTMLElement;
  export let value: string;

  let superModeType: IMessageType = 'bot';
  let superModeTarget: IMessageTarget = 'user';

  function createMessage(text: string): IChatMessage | null {
    text = text.trim();
    if (text === '') {
      return null;
    }
    return {
      id: crypto.randomUUID(),
      text: text,
      type: superModeType,
      timestamp: +new Date(),
      reply: $replying,
      ...messageTarget(superModeTarget)
    }
  }

  async function handleKeydown(e: any) {
    let key = e.key;
    if (e.altKey) {
      BOT_TARGETS.forEach((targetItem) => {
        if (targetItem.key === key) {
          superModeTarget = targetItem.target;
          textarea.focus();
        }
      })
      BOT_TYPES.forEach((typeItem) => {
        if (typeItem.key === key) {
          superModeType = typeItem.type;
          textarea.focus();
        }
      })
    }
    if ((document.activeElement == textarea) && (key === "Enter") && e.ctrlKey) {
      await onSuperModeSend();
    }
  }

  function onClickHereIsTheCode() {
    superModeType = 'bot';
    let message = createMessage("Copy the following code to the notebook:");
    if (message !== null) {
      $superModePreviewMessage = [...$superModePreviewMessage, message];
      superModeType = 'cell';
    }
    textarea.focus();
  }

  function onClickContinue() {
    superModeType = 'ordered';
    value = '- Continue'
    textarea.focus();
  }

  

  async function onSuperModeSend() {
    let timestamp = +new Date()
    $superModePreviewMessage.forEach((message: IChatMessage) => {
      message.timestamp = timestamp;
      message.reply = $replying;
      chatHistory.addNew(message);
    })
    $superModePreviewMessage = [];
    if ($anaAutoLoading) {
      $anaSideModel?.sendSupermode({ loading: false });
    }
    await tick();
  }

  export function enterMessage(text: string): boolean {
    let message = createMessage(text);
    if (message !== null) {
      $superModePreviewMessage = [...$superModePreviewMessage, message];
      return true;
    }
    return false;
  }


</script>


<style>
  .supermodetypes {
    display: flex;
  }
</style>

<div class="supermodetypes">
  {#each BOT_TARGETS as targetItem}
    <label title="Key: {targetItem.key}">
      <input type=radio bind:group={superModeTarget} name="messageTarget" value={targetItem.target}>
      {targetItem.label}
    </label>
  {/each}
  <button on:click|preventDefault={onClickHereIsTheCode}>Code</button>
  <button on:click|preventDefault={onClickContinue}>Continue</button>
</div>
<div class="supermodetypes">
  {#each BOT_TYPES as typeItem}
    <label title="Key: {typeItem.key}">
      <input type=radio bind:group={superModeType} name="messageType" value={typeItem.type}>
      {typeItem.label}
    </label>
  {/each}
</div>


<button on:click|preventDefault={onSuperModeSend}>Send Messages (ctrl + enter)</button>
{#each $superModePreviewMessage as message, index}
  <Message bind:message={message} {index} preview={true}/>
{/each}


<svelte:window on:keydown={handleKeydown}/>