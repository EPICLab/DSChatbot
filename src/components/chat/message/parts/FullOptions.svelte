<script type="ts">
  import type { IChatMessage, IMessagePart } from "../../../../common/anachatInterfaces";
  import Options from "./Options.svelte";
  import Text from "./Text.svelte";
  import TextInput from "./TextInput.svelte";

  export let messagePart: IMessagePart;
  export let message: IChatMessage;
</script>

<Text messagePart={{type: 'text', text: 'Suggestions (clickable):'}}/>
<Options {messagePart} {message}/>
<TextInput messagePart={{type: 'input', text:'Ask a different question'}} {message}/>
