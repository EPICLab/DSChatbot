<script type="ts">
  import type { IMessagePart } from "../../../../common/chatbotInterfaces";
  import { marked } from 'marked';

  export let messagePart: IMessagePart;
</script>

<div>{@html marked.parse(messagePart.text.trim())}</div>

<style>
  div {
    white-space: normal;
  }
</style>