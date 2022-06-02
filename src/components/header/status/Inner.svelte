<script lang="ts">
  import Error from "./Error.svelte";
  export let title: string;
</script>

<style>
  .outer {
    float: right;
  }
  .icon {
    float: left;
    height: 12px;
    width: 12px;
    margin-right: 8px;
    align-items: center;
    display: flex;
  }
</style>

<div {title} class="outer">
  <Error/>
  <div class="icon">
      <slot></slot>
  </div>
</div>