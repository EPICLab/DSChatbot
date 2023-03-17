<script type="ts">
    export let group: any;
    export let name: string;
    export let value: any;
    export let title: string;
    export let cls: string | null = null;

    $: checked = group == value;
  </script>
  
  <label class={cls} class:checked={checked} {title}>
    <input type=radio bind:group={group} {name} {value}>
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