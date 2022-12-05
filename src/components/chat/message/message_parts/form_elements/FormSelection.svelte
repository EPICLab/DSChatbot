<script type="ts">
  import type { IFormElementItem } from "../../../../../common/messages";

  export let element: IFormElementItem;
  let definition = element.rest;

  console.log(definition)
  let options: string[] = [];
  if (definition != null) {
    let split = definition.split('#:')
    console.log(split)

    for (let item of split) {
      if (item[0] == '*') {
        element.value = item.substring(1);
        options.push(element.value)
      } else {
        options.push(item)
      }
    }
  }
  
</script>

<style>
  select {
    width: 100%;
    flex: 2;
  }
</style>

<select bind:value={element.value}>
  {#each options as option}
    <option value={option}>{option}</option>
  {/each}
</select>
