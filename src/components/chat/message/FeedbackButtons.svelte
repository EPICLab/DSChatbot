<script type="ts">
  import ThumbsUp from "../../icons/fa-thumbs-up-solid.svelte";
  import ThumbsDown from "../../icons/fa-thumbs-down-solid.svelte";
  import type { IChatMessage } from "../../../common/chatbotInterfaces";
  import type { IChatInstance } from "../../../chatinstance";
  import IconButton from "../../generic/IconButton.svelte";


  export let chatInstance: IChatInstance;
  export let message: IChatMessage;

  function thumbsUpClick(event: any) {
    message.feedback.rate = message.feedback.rate === 1? 0 : 1;
    chatInstance.submitSyncMessage({
      id: message.id,
      feedback: { rate: message.feedback.rate }
    })
  }

  function thumbsDownClick(event: any) {
    message.feedback.rate = message.feedback.rate === -1? 0 : -1;
    chatInstance.submitSyncMessage({
      id: message.id,
      feedback: { rate: message.feedback.rate }
    })
  }

</script>

<div class="feedback-btns">
  <IconButton 
    title="Good reply"
    selected={message.feedback.rate == 1} 
    on:click={thumbsUpClick}
  ><ThumbsUp/></IconButton>
  <IconButton 
    title="Bad reply"
    selected={message.feedback.rate == -1}
    selectedColor="red"
    on:click={thumbsDownClick}
  ><ThumbsDown/></IconButton>
</div>

<style>
  .feedback-btns {
    display: flex;
    flex-direction: row;
  }
</style>