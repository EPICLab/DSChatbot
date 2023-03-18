<script type="ts">
  export let title: string;
  export let selected: boolean | null = null;
  export let hide: boolean = false;
  export let selectedColor: string = "green";
  export let defaultColor: string = "#616161";
</script>

<button 
  {title}
  class:selected={selected}
  class:hide={hide}
  on:click
  style="--selected-color: {selectedColor}; --default-color: {defaultColor};"
><slot/></button>

<style>
  button {
    background: none!important;
    border: none;
    padding: 0!important;
    
    display: flex;
    fill: var(--default-color);

    align-items:center;
    justify-content:center;
    min-width: 25px;
  }

  button:focus {
    border-bottom: 1px dotted black;
  }

  button:hover {
    cursor: pointer;
  }

  button.hide {
    display: none;
  }

  button.selected :global(svg) {
    fill: var(--selected-color);
  }

  button :global(svg) {
    height: 1em;
  }
</style>

