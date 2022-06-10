<script type="ts">
  import type { IChatMessage } from "../../../common/anachatInterfaces";
  export let message: IChatMessage;
  export let width = 100;
</script>

<style>
  .outer {
    padding: 0 10px;
    width: inherit;
  }

  .inner {
    border-radius: 5px;
    border: 1px solid gray;
    margin-bottom: 0.8em;
    padding: 0.4em;
    white-space: pre-line;
  }

  .user {
    margin-left: 4em;
    background-color: #D0FDFF;
    border-radius: 0.5rem 0.5rem 0 0.5rem;
  }

  .bot {
    margin-right: 4em;
    background-color: #F2F2F2;
    border-radius: 0.5rem 0.5rem 0.5rem 0;
  }


  .error {
    margin-right: 4em;
    background-color: lightpink;
    border-radius: 0.5rem 0.5rem 0.5rem 0;
  }

  .options {
    margin-right: 4em;
    background-color: #F2F2F2;
    border-radius: 0.5rem 0.5rem 0.5rem 0;
    display: flex;
    flex-wrap: wrap;
  }
</style>

<div class="outer">
  <div class="inner {message.type}" bind:clientWidth={width}>
    <slot>{message.text}</slot>
  </div>
</div>