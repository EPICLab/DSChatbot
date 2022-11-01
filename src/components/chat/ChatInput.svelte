<script lang="ts">
  import type { IChatMessage, IOptionItem } from "../../common/anachatInterfaces";
  import { chatHistory, anaAutoLoading, anaSideModel } from "../../stores";
  import { onMount, tick } from "svelte";

  export let subclass = "";
  export let value: string = "";
  export let textarea: HTMLElement|null = null;
  export let placeholder = "";
  export let alternativeKeyDown: ((e: any) => Promise<boolean>) | null = null;
  export let alternativeEnter: ((e: any) => Promise<boolean>) | null = null;
  export let alternativeInput: ((e: any) => Promise<boolean>) | null = null;

  export function resize(): void {
    if (!textarea) return;
    textarea.style.height = 'auto';
    textarea.style.height = Math.max(textarea.scrollHeight, 35) + 'px';
  }
  export async function clear() {
    value = "";
    await tick();
    resize();
  }

  onMount(() => {
    resize();
  })

  function createMessage(text: string): IChatMessage | null {
    let result: string | IOptionItem[];
    text = text.trim();
    if (text === '') {
      return null;
    }
    result = text;
    
    return {
      text: result,
      type: 'user',
      prevent: false,
      hidden: false,
      force: false,
      timestamp: +new Date()
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
      resize();
    }
  }

</script>

<style>
  textarea {
    width: 100%;

    font: inherit;
    height: 100%;
    padding: 5px 11px;
  }
</style>


<div class={subclass}>
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
