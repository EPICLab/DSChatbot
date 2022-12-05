<script type="ts">
  import type { IFormElementItem } from "../../../../../common/messages";

  export let element: IFormElementItem;
  let definition = element.rest;
  let checked: boolean = false;

  if (definition != null) {
    let split = definition.split('#:')
    for (let item of split) {
      if (item[0] == '*') {
        checked = item.substring(1).trim() == 'yes'
      }
    }
  }

  $: element.value = checked ? 'yes' : 'no'
  
</script>

<input type=checkbox bind:checked/>
