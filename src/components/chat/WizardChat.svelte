<script lang="ts">
  import type { IChatMessage, IMessageType } from "../../common/chatbotInterfaces";
  import { replying, wizardPreviewMessage, wizardValue } from "../../stores";
  import Message from "./message/Message.svelte";
  import { tick } from "svelte";
  import { BOT_EDITOR_TYPES, BOT_TARGETS, BOT_TYPES, messageTarget, type IEditorTypeItem, type IMessageTarget } from "../../common/messages";
  import BottomChat from "./BottomChat.svelte";
  import type { IChatInstance } from "../../chatinstance";

  export let chatInstance: IChatInstance;

  let { enableAutoLoading } = chatInstance.config;

  let uniqueNameWithingComponent = crypto.randomUUID();

  let textarea: HTMLElement
  let bottomChat: BottomChat

  let wizardModeType: IMessageType = 'bot'
  let wizardModeTarget: IMessageTarget = 'user'

  function createMessage(text: string): IChatMessage | null {
    text = text.trim()
    if (text === '') {
      return null;
    }
    return {
      id: crypto.randomUUID(),
      text: text,
      type: wizardModeType,
      timestamp: +new Date(),
      reply: $replying,
      feedback: {
        rate: 0,
        reason: "",
        otherreason: ""
      },
      loading: false,
      ...messageTarget(wizardModeTarget)
    }
  }

  async function handleKeydown(e: any) {
    let key = e.key;
    if (e.altKey) {
      BOT_EDITOR_TYPES.forEach((editorTypeItem) => {
        if (editorTypeItem.key === key) {
          onClickEditorItem(editorTypeItem)
        }
      })
      BOT_TARGETS.forEach((targetItem) => {
        if (targetItem.key === key) {
          wizardModeTarget = targetItem.target
          textarea.focus()
        }
      })
      BOT_TYPES.forEach((typeItem) => {
        if (typeItem.key === key) {
          wizardModeType = typeItem.type
          textarea.focus()
        }
      })
    }
    if ((document.activeElement == textarea) && (key === "Enter") && e.ctrlKey) {
      await onWizardModeSend()
    }
  }

  function onClickEditorItem(editorItem: IEditorTypeItem) {
    if ($wizardValue.length > 0) {
      $wizardValue += '\n'
    }
    $wizardValue += editorItem.text
    textarea.focus()
  }

  async function onWizardModeSend() {
    let timestamp = +new Date()
    $wizardPreviewMessage.forEach((message: IChatMessage) => {
      message.timestamp = timestamp
      message.reply = $replying
      chatInstance.addNew(message)
    })
    $wizardPreviewMessage = []
    if ($enableAutoLoading && $replying !== null) {
      chatInstance.removeLoading($replying);
    }
    await tick();
  }

  async function alternativeEnter(e: any) {
    e.preventDefault();
    let message = createMessage($wizardValue)
    if (message !== null) {
      $wizardPreviewMessage = [...$wizardPreviewMessage, message]
      if (bottomChat != undefined) {
        bottomChat.clear()
      }
    }
    return true
  }

</script>


<style>
  .wizardmodetypes {
    display: flex;
  }

  button {
    font-size: 1em;
  }
</style>

<BottomChat 
  bind:textarea
  bind:value={$wizardValue}
  {alternativeEnter}
  bind:this={bottomChat}
  {chatInstance}
>

  <div slot="before">
    {#each BOT_EDITOR_TYPES as editorTypeItem}
      <button
        title="Key: {editorTypeItem.key}"
        on:click|preventDefault={(e) => onClickEditorItem(editorTypeItem)}
      >{editorTypeItem.label}</button>
    {/each}
  </div>
</BottomChat>

<div class="wizardmodetypes">
  {#each BOT_TARGETS as targetItem}
    <label title="Key: {targetItem.key}">
      <input type=radio bind:group={wizardModeTarget} name="messageTarget-{uniqueNameWithingComponent}" value={targetItem.target}>
      {targetItem.label}
    </label>
  {/each}
</div>
<div class="wizardmodetypes">
  {#each BOT_TYPES as typeItem}
    <label title="Key: {typeItem.key}">
      <input type=radio bind:group={wizardModeType} name="messageType-{uniqueNameWithingComponent}" value={typeItem.type}>
      {typeItem.label}
    </label>
  {/each}
</div>


<button on:click|preventDefault={onWizardModeSend}>Send Messages (ctrl + enter)</button>
{#each $wizardPreviewMessage as message, index (message.id)}
  <Message {chatInstance} bind:message={message} {index} preview={true}/>
{/each}

<svelte:window on:keydown={handleKeydown}/>