<script lang="ts">
  import type { IChatMessage, IMessageType } from "../../common/anachatInterfaces";
  import { chatHistory, anaSideModel, anaAutoLoading, replying, superModePreviewMessage } from "../../stores";
  import Message from "./message/Message.svelte";
  import { tick } from "svelte";
  import { BOT_EDITOR_TYPES, BOT_TARGETS, BOT_TYPES, messageTarget, type IEditorTypeItem, type IMessageTarget } from "../../common/messages";
  import BottomChat from "./BottomChat.svelte";

  let value: string = ""
  let textarea: HTMLElement
  let bottomChat: BottomChat

  let superModeType: IMessageType = 'bot'
  let superModeTarget: IMessageTarget = 'user'

  function createMessage(text: string): IChatMessage | null {
    text = text.trim()
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
      BOT_EDITOR_TYPES.forEach((editorTypeItem) => {
        if (editorTypeItem.key === key) {
          onClickEditorItem(editorTypeItem)
        }
      })
      BOT_TARGETS.forEach((targetItem) => {
        if (targetItem.key === key) {
          superModeTarget = targetItem.target
          textarea.focus()
        }
      })
      BOT_TYPES.forEach((typeItem) => {
        if (typeItem.key === key) {
          superModeType = typeItem.type
          textarea.focus()
        }
      })
    }
    if ((document.activeElement == textarea) && (key === "Enter") && e.ctrlKey) {
      await onSuperModeSend()
    }
  }

  function onClickEditorItem(editorItem: IEditorTypeItem) {
    if (value.length > 0) {
      value += '\n'
    }
    value += editorItem.text
    textarea.focus()
  }

  async function onSuperModeSend() {
    let timestamp = +new Date()
    $superModePreviewMessage.forEach((message: IChatMessage) => {
      message.timestamp = timestamp
      message.reply = $replying
      chatHistory.addNew(message)
    })
    $superModePreviewMessage = []
    if ($anaAutoLoading) {
      $anaSideModel?.sendSupermode({ loading: false })
    }
    await tick();
  }

  async function alternativeEnter(e: any) {
    e.preventDefault();
    let message = createMessage(value)
    if (message !== null) {
      $superModePreviewMessage = [...$superModePreviewMessage, message]
      bottomChat.clear()
    }
    return true
  }

</script>


<style>
  .supermodetypes {
    display: flex;
  }

  button {
    font-size: 1em;
  }
</style>

<BottomChat 
  bind:textarea
  bind:value
  {alternativeEnter}
  bind:this={bottomChat}>

  <div slot="before">
    {#each BOT_EDITOR_TYPES as editorTypeItem}
      <button
        title="Key: {editorTypeItem.key}"
        on:click|preventDefault={(e) => onClickEditorItem(editorTypeItem)}
      >{editorTypeItem.label}</button>
    {/each}
  </div>
</BottomChat>

<div class="supermodetypes">
  {#each BOT_TARGETS as targetItem}
    <label title="Key: {targetItem.key}">
      <input type=radio bind:group={superModeTarget} name="messageTarget" value={targetItem.target}>
      {targetItem.label}
    </label>
  {/each}
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