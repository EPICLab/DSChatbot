<script type="ts">
  import type { IChatMessage, IMessagePart } from "../../../../common/chatbotInterfaces";
  import { panelWidget } from "../../../../stores";

  export let message: IChatMessage
  export let messagePart: IMessagePart
  export let preview: boolean
  export let type: 'url' | 'html' | 'text'
  let title: string = 'Info'
  let content: string = messagePart.text
  let desc: string = messagePart.text

  let split = messagePart.text.split(/#:(.*)/s, 2)
  if (split.length == 2) {
    desc = title = split[0]
    content = split[1]
  }

  if (message.new && !preview) {
    message.new = false
    panelWidget.load_panel(content, title, type)
  }

  function onClick(e: any) {
    panelWidget.load_panel(content, title, type)
  }
</script>

<style>
  div {
    word-break: break-all;
  }

  button {
    cursor: pointer;
    border: none;
  }
</style>

<div><button on:click={onClick}>📖</button>{desc}</div>