<script type="ts">
  import type { IMessagePart } from "../../../../common/anachatInterfaces";

  export let messagePart: IMessagePart;
</script>

<div>{@html messagePart.text}</div>