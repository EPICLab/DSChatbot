<script lang="ts">
  import { onMount, tick } from "svelte";
  import { chatHistory } from "../../stores";

  export let value: string = "";
  let textarea: HTMLElement;

  const resize = (): void => {
    textarea.style.height = 'auto';
    textarea.style.height = Math.max(textarea.scrollHeight, 35) + 'px';
  }

  const onEnterPress = async (event: any) => {
    if (event.keyCode === 13 && event.shiftKey === false) {
      event.preventDefault();
      chatHistory.addNew({
        text: value,
        type: 'user',
        timestamp: +new Date()
      })
      value = "";
      await tick();
      resize();
    }
  };

  onMount(() => {
    resize();
  })

</script>

<style>
  div {
    background-color: white;
    position: sticky;
    bottom: 0;
    border-top: 1px solid gray;
    padding: 0.4em;
    padding-right: 1em;
  }

  textarea {
    width: 100%;
  }
</style>

<div>
  <textarea
    bind:this={textarea}
    bind:value
    placeholder="Talk to Ana here..."
    on:input={resize}
    on:keydown={onEnterPress}
  ></textarea>
</div>