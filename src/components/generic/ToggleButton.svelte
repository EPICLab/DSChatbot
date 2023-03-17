<script type="ts">
  export let checked: boolean = false;
  export let title: string = "";
</script>

<label class:checked={checked} {title}>
  <input type=checkbox bind:checked={checked}>
  <slot/>
</label>

<style>
  label {
    display: inline-block;
    cursor: pointer;
    -webkit-user-select: none;
    -moz-user-select: none;
    user-select: none;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    background-color: #eeeeee;
    border-color: #eeeeee;

    margin: 0.25rem 0.125rem;
  }

  .checked {
    filter: brightness(70%);
    border-color: #bdbdbd;
  }

  input {
    display: none;
  }
</style>