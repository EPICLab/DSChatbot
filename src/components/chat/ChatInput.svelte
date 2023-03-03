<script lang="ts">
  import type { IChatMessage, IOptionItem } from "../../common/anachatInterfaces";
  import { chatHistory, anaAutoLoading, anaSideModel, replying } from "../../stores";
  import { tick } from "svelte";
  import { messageTarget } from "../../common/messages";

  export let subclass = "";
  export let value: string = "";
  export let textarea: HTMLElement|null = null;
  export let placeholder = "";
  export let alternativeKeyDown: ((e: any) => Promise<boolean>) | null = null;
  export let alternativeEnter: ((e: any) => Promise<boolean>) | null = null;
  export let alternativeInput: ((e: any) => Promise<boolean>) | null = null;
  export let replyto: string | null = null;

	export let minRows: number = 1;
	export let maxRows: number | null = null;
	
	$: minHeight = `${1 + minRows * 1.2}em`;
	$: maxHeight = maxRows ? `${1 + maxRows * 1.2}em` : `auto`;

  export async function clear() {
    value = "";
    await tick();
  }

  function createMessage(text: string): IChatMessage | null {
    let result: string | IOptionItem[];
    text = text.trim();
    if (text === '') {
      return null;
    }
    result = text;
    
    return {
      id: crypto.randomUUID(),
      text: result,
      type: 'user',
      timestamp: +new Date(),
      reply: replyto || $replying,
      feedback: {
        rate: 0,
        reason: "",
        otherreason: ""
      },
      ...messageTarget('bot')
    }
  }

  async function enter(e: any) {
    if (alternativeEnter === null || !await alternativeEnter(e)) {
      e.preventDefault();
      let newMessage = createMessage(value);
      if (newMessage !== null) {
        chatHistory.addNew(newMessage);
        if ($anaAutoLoading) {
          $anaSideModel?.sendSupermode({ loading: $chatHistory.length });
        }
        clear();
      }
    }
  }

  async function onKeyDown(e: any) {
    let key = e.key
    if (alternativeKeyDown === null || !await alternativeKeyDown(e)) {
      if (key === "Enter" && (e.shiftKey === false)) {
        await enter(e);
      }
    }
  }

  async function onInput(e: any) {
    if (alternativeInput === null || !await alternativeInput(e)) {
    }
  }

</script>

<style>
  div {
		position: relative;
	}

  pre {
    margin: 0;
  }

  pre, textarea {
		font-family: inherit;
		padding: 0.5em;
		box-sizing: border-box;
		border: 1px solid #eee;
		line-height: 1.2;
		overflow: hidden;
    padding: 5px 11px;
	}

  textarea:focus {
    border: 1px solid #333;
  }

  textarea {
		position: absolute;
		width: 100%;
		height: 100%;
		top: 0;
		resize: none;
	}
</style>


<div class={subclass}>
  <pre
		aria-hidden="true"
		style="min-height: {minHeight}; max-height: {maxHeight}"
	>{value + '\n'}</pre>
  <textarea
    bind:this={textarea}
    bind:value={value}
    placeholder={placeholder}
    on:input={onInput}
    on:focus
    on:blur
    on:keydown={onKeyDown}
    on:click
  ></textarea>
  <slot/>
</div>
