<script type="ts">
  import { MessageDisplay, type IChatMessage, type IMessagePart } from "../../../common/anachatInterfaces";
  import { anaTimes } from "../../../stores";
  import Options from "./parts/Options.svelte";
  import Text from "./parts/Text.svelte";
  import Code from "./parts/Code.svelte";
  import Hypertext from "./parts/Hypertext.svelte";
  import TextInput from "./parts/TextInput.svelte";
  import FullOptions from "./parts/FullOptions.svelte";
  import Panel from "./parts/Panel.svelte";
  import Form from "./parts/Form.svelte";
  import { splitUnifiedMessage } from "../../../common/messages";

  export let message: IChatMessage
  export let loading: boolean = false
  export let preview: boolean = false
  export let scrollBottom: () => void
  export let width = 100

  let timestamp = message.timestamp;
  if (!Number.isInteger(timestamp)) {
    timestamp = timestamp * 1000;
  }

  let items: IMessagePart[] = splitUnifiedMessage(message.text);
</script>

<style>
  .outer {
    padding: 0 10px;
    width: inherit;
  }

  .inner {
    border-radius: 5px;
    border: 1px solid gray;
    margin-bottom: 0.8em;
    padding: 0.4em;
    white-space: pre-line;
  }

  .user {
    margin-left: 4em;
    background-color: #D0FDFF;
    border-radius: 0.5rem 0.5rem 0 0.5rem;
  }

  .bot {
    margin-right: 4em;
    background-color: #F2F2F2;
    border-radius: 0.5rem 0.5rem 0.5rem 0;
  }

  .error {
    margin-right: 4em;
    background-color: lightpink;
    border-radius: 0.5rem 0.5rem 0.5rem 0;
  }

  .hidden {
    border-style: dotted;
    border-width: 2px;
    border-color: red;
  }

  .build {
    border-style: dotted;
    border-width: 2px;
    border-color: blue;
  }

  .tobuild {
    border-style: dotted;
    border-width: 2px;
    border-color: green;
  }

  .timestamp-user {
    text-align: right;
  }

</style>

<div class="outer">
  {#if $anaTimes && !preview}
    <div class="timestamp-{message.type}"> 
      { new Date(timestamp).toLocaleTimeString("en-US") }
      {#if loading}
        <span>⌛️</span>
      {/if}
    </div>
  {/if}
  <div 
    class:hidden={message.display == MessageDisplay.Hidden} 
    class:build={message.display == MessageDisplay.SupermodeInput} 
    class:tobuild={message.kernelDisplay == MessageDisplay.SupermodeInput} 
    class="inner {message.type}" bind:clientWidth={width}
  >
    {#each items as messagePart}
      {#if messagePart.type == 'ul' || messagePart.type == 'ol'}
        <Options {messagePart} {message}/>
      {:else if messagePart.type == 'ful' || messagePart.type == 'fol'}
        <FullOptions {messagePart} {message}/>
      {:else if messagePart.type == 'code'}
        <Code {messagePart} {scrollBottom}/>
      {:else if messagePart.type == 'direct-code'}
        <Code {messagePart} {scrollBottom} direct={true}/>
      {:else if messagePart.type == 'html'}
        <Hypertext {messagePart}/>
      {:else if messagePart.type == 'input'}
        <TextInput {messagePart} {message}/>
      {:else if messagePart.type == 'web-panel'}
        <Panel {messagePart} {message} {preview} type='url'/>
      {:else if messagePart.type == 'text-panel'}
        <Panel {messagePart} {message} {preview} type='text'/>
      {:else if messagePart.type == 'html-panel'}
        <Panel {messagePart} {message} {preview} type='html'/>
      {:else if messagePart.type == 'form'}
        <Form {messagePart} {message}/>
      {:else}
        <Text {messagePart}/>
      {/if}
    {/each}
  </div>
</div>