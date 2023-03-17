<script lang="ts">
  import type { IChatMessage, IMessageType } from "../../common/chatbotInterfaces";
  import { replying, wizardPreviewMessage, wizardValue } from "../../stores";
  import Message from "./message/Message.svelte";
  import { SvelteComponent, tick } from "svelte";
  import { BOT_TARGETS, BOT_TYPES, messageTarget, type IMessageTarget } from "../../common/messages";
  import BottomChat from "./BottomChat.svelte";
  import type { IChatInstance } from "../../chatinstance";
  import Title from "../icons/title.svelte";
  import List from "../icons/fa-list.svelte";
  import ListOl from "../icons/fa-list-ol.svelte";
  import LongArrowRight from "../icons/fa-long-arrow-right.svelte";
  import Code from "../icons/fa-code.svelte";
  import Markdown from "../icons/fa-markdown.svelte";
  import IconButton from "../generic/IconButton.svelte";
  import RadioButton from "../generic/RadioButton.svelte";

  interface IEditorTypeItem {
    label: string;
    text: string;
    key: string | null;
    icon: typeof SvelteComponent | null;
  }

  const BOT_EDITOR_TYPES: IEditorTypeItem[] = [
    {label: 'Text', text:'####text#:\n', key: 'a', icon: Title},
    {label: 'Markdown', text:'####markdown#:\n', key: 'm', icon: Markdown},
    {label: 'Ordered list', text:'####fol#:\n', key: 'o', icon: ListOl},
    {label: 'Simple Ordered list', text:'####ol#:\n', key: null, icon: null},
    {label: 'Unordered list', text:'####ful#:\n', key: 'i', icon: List},
    {label: 'Simple Unordered list', text:'####ul#:\n', key: null, icon: null},
    {label: 'Continue', text:'####fol#:\n- Continue', key: 'y', icon: LongArrowRight},
    {label: 'Code', text:'####text#:\nCopy the following code to the notebook:\n####code#:\n', key: 'c', icon: Code},
    {label: 'Simple Code', text:'####code#:\n', key: null, icon: null},
    {label: 'Direct Code', text:'####direct-code#:\n', key: null, icon: null},
    {label: 'Web Panel', text:'####web-panel#:\n', key: null, icon: null},
    {label: 'HMTL Panel', text:'####html-panel#:\n', key: null, icon: null},
    {label: 'Text Panel', text:'####text-panel#:\n', key: null, icon: null},
    {label: 'Form', text:'####form#:\n-selection#:<Column Name>#:<Opt1>#:<Opt2>\n-submit#:Continue\n', key: 'f', icon: null},
    {label: 'Metadata', text:'####metadata#:\n{"type": "wizard", "value": "<value>"}\n', key: null, icon: null},
  ]


  export let chatInstance: IChatInstance;

  let { enableAutoLoading } = chatInstance.config;

  let uniqueNameWithingComponent = crypto.randomUUID();

  let textarea: HTMLElement
  let bottomChat: BottomChat

  let wizardModeType: IMessageType = 'bot'
  let wizardModeTarget: IMessageTarget = 'user'
  let messageTypeHelperValue: IEditorTypeItem = BOT_EDITOR_TYPES[0];

  

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
    if (e.altKey && key !== null) {
      BOT_EDITOR_TYPES.forEach((editorTypeItem) => {
        if (editorTypeItem.key === key) {
          onClickEditorItem(e, editorTypeItem)
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

  function onClickEditorItem(event:any, editorItem: IEditorTypeItem) {
    event.preventDefault();
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

<BottomChat 
  bind:textarea
  bind:value={$wizardValue}
  {alternativeEnter}
  bind:this={bottomChat}
  {chatInstance}
>

  <div slot="before" class="before">
    {#each BOT_EDITOR_TYPES as editorTypeItem (editorTypeItem.key)}
      {#if editorTypeItem.icon}
        <IconButton
          title="{editorTypeItem.label} ({editorTypeItem.key})"
          on:click={(e) => onClickEditorItem(e, editorTypeItem)}
        ><svelte:component this={editorTypeItem.icon}/></IconButton>
      {/if}
    {/each}
    <select bind:value={messageTypeHelperValue}>
      {#each BOT_EDITOR_TYPES as editorTypeItem (editorTypeItem.key)}
        <option value={editorTypeItem}>
          {editorTypeItem.label} {#if editorTypeItem.key}({editorTypeItem.key}){/if}
        </option>
      {/each}
    </select>
    <button title="Add selected mode" on:click|preventDefault={(e) => onClickEditorItem(e, messageTypeHelperValue)}>Add</button>
  </div>
</BottomChat>


<div class="wizardmodetypes">
  {#each BOT_TARGETS as targetItem (targetItem.key)}
    <RadioButton
      title="Key: {targetItem.key}" 
      bind:group={wizardModeTarget}
      name="messageTarget-{uniqueNameWithingComponent}"
      value={targetItem.target}
      cls={targetItem.style}
    >{targetItem.label}</RadioButton> 

  {/each}
  <div class="separator"></div>
  {#each BOT_TYPES as typeItem (typeItem.key)}
    <RadioButton
      title="Key: {typeItem.key}" 
      bind:group={wizardModeType}
      name="messageType-{uniqueNameWithingComponent}"
      value={typeItem.type}
      cls={typeItem.style}
      >{typeItem.label}</RadioButton>
  {/each}
</div>


<button on:click|preventDefault={onWizardModeSend}>Send Messages (ctrl + enter)</button>
{#each $wizardPreviewMessage as message, index (message.id)}
  <Message {chatInstance} bind:message={message} {index} preview={true}/>
{/each}

<svelte:window on:keydown={handleKeydown}/>

<style>
  .wizardmodetypes {
    display: flex;
  }

  button {
    font-size: 1em;
  }

  .before {
    display: flex;
  }

  .separator {
    width: 2px;
    height: 90%;
    background-color: #bdbdbd;
    margin: 0 5px;
  }
</style>
