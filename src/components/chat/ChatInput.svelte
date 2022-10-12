<script lang="ts">
  // Based on simple-svelte-autocomplete: https://github.com/pstanoev/simple-svelte-autocomplete/graphs/contributors

  import AutoCompleteItem from "./AutoCompleteItem.svelte";
  import Message from "./message/Message.svelte";
  import { onMount, tick } from "svelte";
  
  import { chatHistory, anaSideModel, subjectItems, anaSuperMode, anaQueryEnabled, anaAutoLoading } from "../../stores";
  import type { IAutoCompleteItem, IChatMessage, IMessageType, IOptionItem } from "../../common/anachatInterfaces";

  let superModeType: IMessageType = 'bot';
  let superModeErrorMessage: string = "";
  let superModeOptionId = 0;
  let superModePreviewMessage: IChatMessage[] = [];
  let superModeHide: boolean = false;

  async function onSuperModeSend() {
    let timestamp = +new Date()
    superModePreviewMessage.forEach((message: IChatMessage) => {
      message.timestamp = timestamp;
      chatHistory.addNew(message);
    })
    superModePreviewMessage = [];
    if ($anaAutoLoading) {
      $anaSideModel?.sendSupermode({ loading: false });
    }
    await tick();
  }

  function onClickHereIsTheCode() {
    if (!$anaSuperMode) return;
    superModeType = 'bot';
    let message = createMessage("Copy the following code to the notebook:");
    if (message !== null) {
      superModePreviewMessage = [...superModePreviewMessage, message];
      superModeType = 'cell';
    }
    textarea.focus();
  }

  function onClickContinue() {
    if (!$anaSuperMode) return;
    superModeType = 'options';
    value = '! Continue'
    textarea.focus();
  }

  function removePreview(index: number) {
    superModePreviewMessage.splice(index, 1);
    superModePreviewMessage = superModePreviewMessage;
  }

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
      prevent: false,
      timestamp: +new Date(),
      force: false,
      hidden: false,
    })
    clear();
  }

  function createMessage(text: string): IChatMessage | null {
    let result: string | IOptionItem[];
    superModeErrorMessage = "";
    text = text.trim();
    if (text === '') {
      return null;
    }

    if ($anaSuperMode && superModeType === 'options'){
      if (text[0] !== '-' && text[0] !== '!') {
        superModeErrorMessage = 'You must start the options by "-"';
        return null;
      }
      let options: IOptionItem[] = [];
      let lines = text.substring(1).trim().split("\n-");
      if (lines.length == 1 && text[0] !== '!') {
        superModeErrorMessage = 'If you want to show a button with a single option, start the message with "!"';
        return null;
      }
      options = lines.map((line) => {
        let newText = line.trim();
        return {
          'key': `SU-${superModeOptionId++}: ${newText}`,
          'label': newText
        }
      })
      result = options;
    } else {
      result = text;
    }
    return {
      text: result,
      type: $anaSuperMode ? superModeType : 'user',
      prevent: $anaSuperMode,
      hidden: $anaSuperMode && superModeHide,
      force: $anaSuperMode && superModeHide,
      timestamp: +new Date()
    }
  }

  async function enter(e: any) {
    e.preventDefault();
    if (highlightIndex == -1) {
      let newMessage = createMessage(value);
      if (newMessage !== null) {
        if ($anaSuperMode) {
          superModePreviewMessage = [...superModePreviewMessage, newMessage];          
        } else {
          chatHistory.addNew(newMessage);
          if ($anaAutoLoading) {
            $anaSideModel?.sendSupermode({ loading: $chatHistory.length });
          }
        }
        clear();
      }
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
    if ($anaSuperMode && (e.altKey)) {
      if (key === "a") {
        superModeType = "bot"
      } else if (key === "o") {
        superModeType = "options"
      } else if (key === "c") {
        superModeType = "cell"
      } else if (key === "u") {
        superModeType = "user"
      } else if (key === "e") {
        superModeType = "error"
      } else if (key === "h") {
        superModeHide = !superModeHide;
      }
    }

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
      if ((e.ctrlKey === true) && $anaSuperMode) {
        await onSuperModeSend();
      }
    }
  }
  function onDocumentClick(e: any) {
    if (e.composedPath().some((path: HTMLElement) => path.classList && path.classList.contains(uniqueId))) {
      highlight()
    } else {
      close()
    }
  }
  

  $: showList = opened && !$anaSuperMode && ((items && items.length > 0) || (filteredTextLength > 0 && loading && $anaQueryEnabled));
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

  .error {
    color: red;
  }

  .supermodetypes {
    display: flex;
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

{#if $anaSuperMode}
  <label>
    <input type=checkbox bind:checked={superModeHide} value="hide">
    Send hidden message to chatbot
  </label>
  <div class="supermodetypes">
    <label>
      <input type=radio bind:group={superModeType} name="messageType" value="bot">
      Ana
    </label>
    <label>
      <input type=radio bind:group={superModeType} name="messageType" value="options">
      Options
    </label>
    <label>
      <input type=radio bind:group={superModeType} name="messageType" value="cell">
      Code
    </label>
    <label>
      <input type=radio bind:group={superModeType} name="messageType" value="user">
      User
    </label>
    <label>
      <input type=radio bind:group={superModeType} name="messageType" value="error">
      Error
    </label>
    <button on:click|preventDefault={onClickHereIsTheCode}>Code</button>
    <button on:click|preventDefault={onClickContinue}>Continue</button>
  </div>
  {#if superModeErrorMessage}
  <div class="error">
    {superModeErrorMessage}
  </div>
  {/if}


  <button on:click|preventDefault={onSuperModeSend}>Send Messages (ctrl + enter)</button>
  {#each superModePreviewMessage as message, i}
    <Message {message} remove={() => removePreview(i)}/>
  {/each}
{/if}

<svelte:window on:click={onDocumentClick} />