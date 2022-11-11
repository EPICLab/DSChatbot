

<script type="ts">
  import { MessageDisplay, type IChatMessage } from '../../../common/anachatInterfaces';
  import { anaSuperMode, replying } from '../../../stores';
  import Eye from '../../icons/eye.svelte';
  import Reply from '../../icons/reply.svelte';

  import Cell from './Cell.svelte';
  import Default from './Default.svelte';
  import Options from './Options.svelte';
  import UserCode from './UserCode.svelte';

  export let message: IChatMessage;
  export let scrollBottom: () => void = () => {};
  export let remove: (() => void) | null = null;
  export let loading = false;
  export let index: number | null = null;
  export let chat: HTMLElement | null = null;

  function select(e: any) {
    if ($replying == message.id) {
      $replying = null;
    } else {
      $replying = message.id;
    }
  }

  function scroll(e: any) {
    if (chat && message.reply) {
      const element: HTMLElement = chat.getElementsByClassName(`message-${message.reply}`)[0] as HTMLElement;
      element.onanimationend = () => {
        element.classList.remove("blink-message");
      }
      element.classList.add("blink-message")
      chat.scrollTop = Math.max(0, element.offsetTop - 30);
    }
  }

  $: selected = $replying == message.id;
</script>

<style>

 @keyframes blinking {
    0% {
      background-color: lightgreen;
    }
    100% {
      background-color: white;
    }
  }

  :global(.blink-message) { animation: blinking 2s 1; }
  

  span {
    height: 0px;
    position: relative;
    top: 5px;
    z-index: 1000;
  }

  span:hover {
    cursor: pointer;
  }

  .icons {
    height: 0px;
    position: relative;
    top: 5px;
    z-index: 1000;
    width: 13px;
    float: right;
  }

  .icons.user {
    float: none;
    margin-left: 15px;
  }

  .icon:hover {
    cursor: pointer;
  }
  
  .icon.hideuserreply {
    display: none;
  }

  .icon.selected :global(svg) {
    fill: green;
  }

</style>


<div class="message-{message.id}"> 
  {#if remove}
  <span on:click={remove}>❌</span>
  {:else}
  <div class="icons {message.type}">

    {#if chat && message.reply}
      <div title="View replied message" class="icon" on:click={scroll}><Eye/></div>
    {/if}

    <div 
      title={selected? "Replying to" : "Reply to"}
      class="icon"
      class:selected={selected} 
      class:hideuserreply={!$anaSuperMode && message.type == 'user'}
      on:click={select}
    ><Reply/></div>


  </div>
  {/if}

  {#if message.display === MessageDisplay.Default || $anaSuperMode}
    {#if message.type === 'options'}
      <Options {message}/>
    {:else if message.type === 'cell'}
      <Cell {message} {scrollBottom}/>
    {:else if message.type === 'usercode' || message.type === 'botcode'}
      <UserCode {message} {scrollBottom}/>
    {:else}
      <Default {message} {loading} {index}/>
    {/if}
  {/if}
</div>
