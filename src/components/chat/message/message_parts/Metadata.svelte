<script type="ts">
  import type { IChatInstance } from "../../../../chatinstance";
    import type { IMessagePart } from "../../../../common/chatbotInterfaces";
    import { wizardMode } from "../../../../stores";
  
    export let chatInstance: IChatInstance;
    export let messagePart: IMessagePart;
    const { showMetadata } = chatInstance.config;
  </script>
  
  {#if $wizardMode && $showMetadata}
    <div>Metadata: {messagePart.text}</div>
  {/if}

  <style>
    div {
        color: blue;
    }
  </style>