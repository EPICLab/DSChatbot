<script type="ts">
  import type { IChatMessage, IMessagePart } from "../../../../common/anachatInterfaces";
  import { messageTarget, type IFormElementItem } from "../../../../common/messages";
  import { chatHistory } from "../../../../stores";
  import FormCheck from "./form_elements/FormCheck.svelte";
  import FormSelection from "./form_elements/FormSelection.svelte";
  import FormText from "./form_elements/FormText.svelte";

  export let messagePart: IMessagePart;
  export let message: IChatMessage;
  let items: IFormElementItem[]
  
  function extractFormElements(text: string): IFormElementItem[] {
    let options: IFormElementItem[] = [];
    if (!text) {
      return options;
    }
    text = text.trim();
    if (text[0] == '-' || text[0] == '!') {
      text = text.substring(1).trim()
    }
    let lines = text.split("\n-");
    options = lines.map((line, index) => {
      let newText: string = line.trim()
      let split = newText.split(/#:(.*)/s, 2)
      let label = null
      let rest = null
      let type = split[0].trim()
      if (split[1]) {
        split = split[1].split(/#:(.*)/s, 2)
        label = split[0]
        rest = split[1]
      }
      return {
        'id': index,
        'type': type,
        'label': label || type,
        'rest': rest || null,
        'value': ''
      }
    })
    return options;
  }

  const submit = (e: any): void => {
    let newText = "";
    for (let element of items) {
      if (element.type == 'submit') {
        continue
      }
      newText += element.label + " = " + element.value + "\n"
    }
    chatHistory.addNew({
      id: crypto.randomUUID(),
      text: newText,
      type: 'user',
      timestamp: +new Date(),
      reply: message.id,
      feedback: {
        rate: 0,
        reason: "",
        otherreason: ""
      },
      ...messageTarget('bot')
    })
    e.target.blur()
  }

 

  $: items = extractFormElements(messagePart.text)

</script>

<style>
  button {
    border: 1px solid black;
    padding: 0 5px!important;
    text-align: left;
    font-size: 1em!important;
  }

  button:hover {
    background-color: #D0FDFF;
    cursor: pointer;
  }

  button:focus {
    text-decoration: underline dotted;
  }

  .row {
    display: flex;
    justify-content: flex-end;
  }

  .row > .label {
    flex: 1;
  }
</style>

<!-- svelte-ignore a11y-label-has-associated-control -->

<form class="inner">
  {#each items as element (element.id)}
    <div>
      {#if element.type == 'submit'}
      <span class="row">
        <button class="button" on:click|preventDefault={submit}>
          {element.label}
        </button>
      </span>
      {:else if element.type == 'text'}
        <label class="row"><span class="label">{element.label}</span><FormText {element}/></label>
      {:else if element.type == 'selection'}
        <label class="row"><span class="label">{element.label}</span><FormSelection {element}/></label>
      {:else if element.type == 'check'}
        <label><FormCheck {element}/> {element.label} </label>
      {:else}
        {element.label}
      {/if}
    </div>
  {/each}
</form>