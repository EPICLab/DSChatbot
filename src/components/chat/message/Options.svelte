<script type="ts">
  import type { IChatMessage, IOptionItem } from "../../../common/anachatInterfaces";
  import Default from "./Default.svelte";
  import { chatHistory } from "../../../stores";
  export let message: IChatMessage;
  let width: number;


  const click = (element: IOptionItem) => (): void => {
    if ($chatHistory[$chatHistory.length - 1] == message) {
      chatHistory.addNew({
        text: element.label,
        type: 'user',
        prevent: false,
        timestamp: +new Date(),
        force: false,
        hidden: false,
      })
    } else {
      chatHistory.addNew({
        text: '!choose ' + element.key,
        type: 'user',
        prevent: false,
        timestamp: +new Date(),
        force: false,
        hidden: false,
      })
    }
  }

  const items: IOptionItem[] = message.text as IOptionItem[];
</script>

<style>
  div {
    display: table-cell;
    border: 1px solid grey;
    padding: 5px;
    margin: 2px;
    max-width: 42%;
    flex: 1 0 45%;
  }
  
  div:hover {
    background-color: #D0FDFF;
    cursor: pointer;
  }
</style>

<Default {message} bind:width>
  {#each items as element}
    <div on:click={click(element)} title={element.key} style:max-width={((width - 45)/2) + 'px'}>
      {element.label}
    </div>
  {/each}
</Default>