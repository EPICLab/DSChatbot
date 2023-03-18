<script type="ts">
  import type { IMessagePart } from "../../../../common/chatbotInterfaces";
  import CodeWidget from '../../../generic/CodeWidget.svelte';

  export let messagePart: IMessagePart;
  export let scrollBottom: () => void;
  export let direct: boolean = false;
</script>

<CodeWidget code={messagePart.text} {scrollBottom} {direct}/>