<script lang="ts">
  // Based on simple-svelte-autocomplete: https://github.com/pstanoev/simple-svelte-autocomplete/graphs/contributors

  import AutoCompleteItem from "./AutoCompleteItem.svelte";
  import { onMount, tick } from "svelte";
  
  import { chatHistory, anaSideModel, subjectItems } from "../../stores";
  import type { IAutoCompleteItem } from "../../common/anachatInterfaces";

  export let value: string = "";
  export let text: string|undefined = undefined;
  export let minCharactersToSearch = 1;
  let textarea: HTMLElement;
  let items: IAutoCompleteItem[] = [];
  let loading = false 
  let filteredTextLength = 0;
  let lastRequestId = 0;
  let delay = 200;
  let highlightIndex = -1;
  let opened = false;
  let list: HTMLElement;
  let inputDelayTimeout: NodeJS.Timeout;
  let listHeight: number = 0;

  const uniqueId = "sautocomplete-" + Math.floor(Math.random() * 1000)

  const resize = (): void => {
    textarea.style.height = 'auto';
    textarea.style.height = Math.max(textarea.scrollHeight, 35) + 'px';
  }

  onMount(() => {
    resize();
  })
  
  async function search() {
    let textFiltered = (text === undefined) ? "" : text.replace(/[&/\\#,+()$~%.'":*?<>{}]/g, " ").trim().toLowerCase()
    if (minCharactersToSearch > 1 && textFiltered.length < minCharactersToSearch) {
      textFiltered = ""
    }
    filteredTextLength = textFiltered.length
    // external search which provides items
    lastRequestId = lastRequestId + 1
    const currentRequestId = lastRequestId
    loading = true
    $anaSideModel?.sendSubjectQuery(currentRequestId, textFiltered);
  }
  function processInput() {
    search().then()
  }
  function open() {
    // check if the search text has more than the min chars required
    if (notEnoughSearchText()) {
      return
    }
    opened = true
  }
  
  function close() {
    opened = false
    loading = false
    highlightIndex = -1;
  }
  function notEnoughSearchText() {
    return (
      minCharactersToSearch > 0 &&
      filteredTextLength < minCharactersToSearch &&
      // When no searchFunction is defined, the menu should always open when the input is focused
      (filteredTextLength > 0)
    )
  }
  function closeIfMinCharsToSearchReached() {
    if (notEnoughSearchText()) {
      close()
      return true
    }
    return false
  }
  function resetListToAllItemsAndOpen() {
    if (!items) {
      search();
    }
    open();
  }
  async function clear() {
    value = text = "";
    items = [];
    close();
    await tick();
    resize();
  }
  async function selectItem(event: any) {
    chatHistory.addNew({
      text: '!subject ' + event.detail.item.key,
      type: 'user',
      timestamp: +new Date()
    })
    clear();
  }
  async function enter(e: any) {
    e.preventDefault();
    if (highlightIndex == -1) {
      chatHistory.addNew({
        text: value,
        type: 'user',
        timestamp: +new Date()
      })
      clear();
    } else {
      selectItem({detail: { item: items[highlightIndex] }})
    }
    
  }
  function up() {
    open()
    if (highlightIndex < items.length - 1) {
      highlightIndex++
    }
    highlight()
  }
  function down() {
    open()
    if (highlightIndex > -1) {
      highlightIndex--
    }
    highlight()
  }
  function highlight() {
    const query = ".selected"
    const el = list && list.querySelector(query) as unknown as any;
    if (el) {
      if (typeof el.scrollIntoViewIfNeeded === "function") {
        el.scrollIntoViewIfNeeded()
      } else if (typeof el.scrollIntoView === "function") {
        el.scrollIntoView()
      }
    }
  }
  function onEsc(e: any) {
    e.stopPropagation()
    if (opened) {
      textarea.focus()
      close()
    }
  }

  function onInput(e: any) {
    resize();
    text = e.target.value;
    if (inputDelayTimeout) {
      clearTimeout(inputDelayTimeout)
    }
    inputDelayTimeout = setTimeout(processInput, delay)
  }
  function onBlur() {
    //close();
  }
  async function onKeyDown(e: any) {
    let key = e.key
    if (key === "Tab" && opened) {
      close();
    } else if (key === "ArrowDown") {
      down();
    } else if (key === "ArrowUp") {
      up();
    } else if (key === "Escape") {
      onEsc(e);
    } else if ((key === "Enter") && (e.shiftKey === false)) {
      await enter(e);
    }
  }
  function onDocumentClick(e: any) {
    if (e.composedPath().some((path: HTMLElement) => path.classList && path.classList.contains(uniqueId))) {
      highlight()
    } else {
      close()
    }
  }
  

  $: showList = opened && ((items && items.length > 0) || filteredTextLength > 0);
  $: ({ responseId, sitems } = $subjectItems);
  $: {
    if ($responseId == lastRequestId) {
      items = $sitems;
      loading = false;
      if (!closeIfMinCharsToSearchReached()) {
        open()
      }
      highlightIndex = -1;
    } else {
      items = [];
    }
  };
  $: {
    if (list) {
      list.style.top = `-${listHeight}px`
    }
  }
</script>

<style>
  .text {
    background-color: white;
    position: sticky;
    bottom: 0;
    border-top: 1px solid gray;
    padding: 0.4em;
    padding-right: 1em;
  }

  .autocomplete {
    min-width: 200px;
    max-width: 100%;
    position: relative;
    vertical-align: top;
  }

  .autocomplete * {
    box-sizing: border-box;
  }

  textarea {
    width: 100%;

    font: inherit;
    height: 100%;
    padding: 5px 11px;
  }

  .autocomplete-list {
    display: flex; flex-direction: column-reverse;
    background: #fff;
    position: absolute;
    width: 100%;
    overflow-y: auto;
    z-index: 1000;
    padding: 10px 0;
    top: 0px;
    border: 1px solid #999;
    max-height: calc(15 * (1rem + 10px) + 15px);
    user-select: none;
  }

  .autocomplete-list:empty {
    padding: 0;
  }

  .autocomplete-list-item-no-results {
    padding: 5px 15px;
    color: #999;
    line-height: 1;
  }
  .autocomplete-list-item-loading {
    padding: 5px 15px;
    line-height: 1;
  }
  .autocomplete-list.hidden {
    visibility: hidden;
    display: none;
  }

</style>

<div class="text">
  <div class="autocomplete select is-fullwidth {uniqueId}">
    <textarea
      bind:this={textarea}
      bind:value
      placeholder="Talk to Ana here..."
      on:input={onInput}
      on:focus={resetListToAllItemsAndOpen}
      on:blur={onBlur}
      on:keydown={onKeyDown}
      on:click={resetListToAllItemsAndOpen}
    ></textarea>
    <div
      class="autocomplete-list {showList ? '' : 'hidden'} is-fullwidth"
      bind:this={list}
      bind:clientHeight={listHeight}
    >
      {#if items && items.length > 0}
        {#each items as listItem, i}
          {#if listItem}
            <AutoCompleteItem 
              item={listItem}
              position={i}
              bind:highlightIndex
              on:select={selectItem}
            />
          {/if}
        {/each}
      {:else if loading}
        <div class="autocomplete-list-item-loading">
          Loading...
        </div>
      {:else}
        <div class="autocomplete-list-item-no-results">
          No results...
        </div>
      {/if}
    </div>
  </div>
</div>

<svelte:window on:click={onDocumentClick} />