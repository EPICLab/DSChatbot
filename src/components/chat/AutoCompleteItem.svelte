<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { IAutoCompleteItem } from "../../common/chatbotInterfaces";
  import { onKeyPress } from '../../common/utils';
  import { panelWidget } from '../../stores';
  import Eye from '../icons/eye.svelte';
  export let item: IAutoCompleteItem;
  export let highlightIndex: number;
  export let position: number;
  const dispatch = createEventDispatcher();

  function onClick(e: Event) {
    dispatch('select', { item: item });
  }
 
  function clickURL(e: Event) {
    e.preventDefault()
    panelWidget.load_url(
      item.url as string,
      item.key as string,
    )
  }

</script>

<style>
  .autocomplete-list-item {
    padding: 5px 15px;
    color: #333;
    cursor: pointer;
    line-height: 1;
  }

  .autocomplete-list-item.selected, .autocomplete-list-item:hover {
    background-color: #2e69e2;
    color: #fff;
  }
</style>

<div
  class="autocomplete-list-item"
  class:selected={position === highlightIndex}
  on:click={onClick}
  on:keypress={(e) => onKeyPress(onClick, e)}
>
  {item.key}
  {#if item.url}
    <span 
      on:click={clickURL}
      on:keypress={(e) => onKeyPress(clickURL, e)}
    ><Eye/></span>
  {/if}
</div>