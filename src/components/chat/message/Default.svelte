<script type="ts">
  import type { IChatMessage } from "../../../common/anachatInterfaces";
  export let message: IChatMessage;
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
    background-color: lightgray;
  }

  .bot {
    margin-right: 4em;
    background-color: lightblue;
  }

  .error {
    margin-right: 4em;
    background-color: lightpink;
  }

  .options {
    margin-right: 4em;
    background-color: lightblue;
    display: flex;
    flex-wrap: wrap;
  }
</style>

<div class="outer">
  <div class="inner {message.type}">
    <slot>{message.text}</slot>
  </div>
</div>