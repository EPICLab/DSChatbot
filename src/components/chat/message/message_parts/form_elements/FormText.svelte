<script type="ts">
  import type { IFormElementItem } from "../../../../../common/messages";

  export let element: IFormElementItem;
  let definition = element.rest;

  let placeholder = "";
  if (definition != null) {
    let split = definition.split('#:')
    for (let item of split) {
      if (item[0] == '*') {
        element.value = item.substring(1);
      } else {
        placeholder = item;
      }
    }
  }
  
</script>

<style>
  input {
    width: 100%;
    flex: 2;
  }
</style>

<input bind:value={element.value} {placeholder}/>
