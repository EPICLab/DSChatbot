<script lang="ts">
  import { tick } from "svelte";
  import type { IChatInstance } from "../../chatinstance";
  import ChatInput from "./ChatInput.svelte";

  export let chatInstance: IChatInstance;
  export let textarea: HTMLElement;
  export let value: string = "";
  export let placeholder: string = "Talk to Newton here...";
  export let subclass: string = "";
  export let alternativeKeyDown: ((e: any) => Promise<boolean>) | null = null;
  export let alternativeEnter: ((e: any) => Promise<boolean>) | null = null;
  export let alternativeInput: ((e: any) => Promise<boolean>) | null = null;
  export async function clear() {
    value = "";
    await tick();
  }
</script>

<style>
  .text {
    background-color: white;
    position: sticky;
    bottom: 0;
    border-top: 1px solid gray;
    padding: 0.4em;
  }
</style>

<div class="text">
  <slot name="before"/>
  <ChatInput
    {chatInstance}
    {subclass}
    {placeholder}
    bind:textarea
    bind:value
    on:focus
    on:click
    {alternativeKeyDown}
    {alternativeEnter}
    {alternativeInput}
    {clear}
  ><slot name="chat"/></ChatInput>
  <slot name="after"/>
</div>