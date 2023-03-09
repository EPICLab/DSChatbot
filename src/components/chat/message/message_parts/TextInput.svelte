<script type="ts">
  import type { IChatInstance } from "../../../../chatinstance";
  import type { IChatMessage, IMessagePart } from "../../../../common/chatbotInterfaces";
  import ChatInput from "../../ChatInput.svelte";

  export let chatInstance: IChatInstance;
  export let messagePart: IMessagePart;
  export let message: IChatMessage;
</script>

<div class="text">
  <ChatInput value="" replyto={message.id} subclass="subtext" placeholder={messagePart.text} {chatInstance}/>
</div>