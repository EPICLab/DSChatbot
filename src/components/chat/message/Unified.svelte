<script type="ts">
  import type { IChatMessage, IMessagePart } from "../../../common/anachatInterfaces";
  import Default from "./Default.svelte";
  import Options from "./parts/Options.svelte";
  import Text from "./parts/Text.svelte";
  import Code from "./parts/Code.svelte";
  import Hypertext from "./parts/Hypertext.svelte";
  import TextInput from "./parts/TextInput.svelte";
  import FullOptions from "./parts/FullOptions.svelte";
  import { splitUnifiedMessage } from "../../../common/messages";

  export let message: IChatMessage;
  export let loading: boolean;
  export let preview: boolean;
  export let scrollBottom: () => void;

  let items: IMessagePart[] = splitUnifiedMessage(message.text);
</script>

<Default {message} {loading} {preview}>
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
    {:else}
      <Text {messagePart}/>
    {/if}
  {/each}
</Default>
