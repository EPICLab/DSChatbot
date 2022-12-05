<script type="ts">
  import type { IChatMessage, IMessagePart, IOptionItem } from "../../../../common/anachatInterfaces";
  import { extractOptions, messageTarget } from "../../../../common/messages";
  import { chatHistory, anaAutoLoading, anaSideModel } from "../../../../stores";

  export let messagePart: IMessagePart;
  export let message: IChatMessage;
  let type: 'ul' | 'ol';

  const click = (element: IOptionItem) => (e: any): void => {
    chatHistory.addNew({
      id: crypto.randomUUID(),
      text: element.label,
      type: 'user',
      timestamp: +new Date(),
      reply: message.id,
      ...messageTarget('bot')
    })
    if ($anaAutoLoading) {
      $anaSideModel?.sendSupermode({ loading: $chatHistory.length });
    }
    e.target.blur()
  }
  let items: IOptionItem[]

  $: type = (messagePart.type === 'ul' || messagePart.type === 'ful')? 'ul' : 'ol';
  $: items = extractOptions(messagePart.text, type)

</script>

<style>
  button {
    flex: 1 0 100%;
    border: none;
    border-radius: 0!important;
    padding: 0 0 0 5px!important;
    text-align: left;
    font-size: 1em!important;
  }

  .button:first-child {
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
  }

  .button:last-child {
    border-bottom-left-radius: 3px;
    border-bottom-right-radius: 3px;
  }

  .button:not(:first-child) {
    border-top: 1px solid black;
  }
  
  button:hover {
    background-color: #D0FDFF;
    cursor: pointer;
  }

  button:focus {
    text-decoration: underline dotted;
  }

  .inner {
    display: flex;
    flex-wrap: wrap;
    padding-right: 5px;
    border: 1px solid #333;
    margin: 2px;
    border-radius: 3px;
  }
</style>

<div class="inner">
  {#each items as element}
    <button class="button" on:click={click(element)} title={element.key}>
      {element.label}
    </button>
  {/each}
</div>