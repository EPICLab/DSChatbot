<script type="ts">
  import type { IMessagePart } from "../../../../common/chatbotInterfaces";

  export let messagePart: IMessagePart;
</script>

<div>{messagePart.text}</div>