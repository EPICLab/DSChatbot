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
  let article = items.length == 1? "the" : 'an';
</script>

<style>
  div.button {
    display: table-cell;
    border: 2px solid #333;
    padding: 5px;
    margin: 2px;
    max-width: 42%;
    flex: 1 0 45%;
    border-radius: 7px;
    text-align: center;
  }
  
  div.button:hover {
    background-color: #D0FDFF;
    cursor: pointer;
  }

  .inner {
    display: flex;
    flex-wrap: wrap;
  }
</style>

<Default {message} bind:width>
  <div> Click in {article} option: </div>
  <div class="inner">
    {#each items as element}
      <div class="button" on:click={click(element)} title={element.key} style:max-width={((width - 45)/2) + 'px'}>
        {element.label}
      </div>
    {/each}
  </div>
</Default>