<script type="ts">
  import type { IChatMessage, IMessagePart } from "../../../../common/anachatInterfaces";
  import ChatInput from "../../ChatInput.svelte";

  export let messagePart: IMessagePart;
  export let message: IChatMessage;
</script>

<div class="text">
  <ChatInput value="" replyto={message.id} subclass="subtext" placeholder={messagePart.text}/>
</div>