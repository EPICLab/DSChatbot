<script lang="ts">

export let key: string;
export let type: string;
export let config: any;
export let value: any;

let component: HTMLElement;
let unique = crypto.randomUUID();

function loadFile() {
  const files = (component as HTMLInputElement).files;
  if (files == null) {
    return;
  }
  const file = files[0];
  if (file == null) {
    return;
  }
  const reader = new FileReader();
  reader.addEventListener("load", function () {
    value = reader.result;
  });
  reader.readAsText(file);
}

</script>


{#if type == "text"}
  <label>{config.label || key}: <input bind:this={component} type=text bind:value={value}></label>
{:else if type == "datalist"}
  <label>{config.label || key}: <input bind:this={component} list={unique} bind:value={value}>
  <datalist id={unique}>
    {#each config.options as option}
      <option>{option}</option>
    {/each}
  </datalist>
</label>
{:else if type == "range"}
  <label>{config.label || key}: <input bind:this={component} type=range step={config.step} min={config.min} max={config.max} bind:value={value}>
    <span> {value}</span></label>
{:else if type == "textarea"}
  <label><div>{config.label || key}: </div>
  <textarea rows={config.rows} bind:this={component} bind:value={value}></textarea></label>
{:else if type == "file"}
  <label>{config.label || key}: <input bind:this={component} type=file on:change={loadFile}></label>
{:else}
  <label>{config.label || key}: <input bind:this={component} type=text bind:value={value}></label>
{/if}

<style>
  input, textarea {
    max-width: 100%;
    width: 100%;
    box-sizing: border-box; 
  }

  label {
    display: flex;
    box-sizing: border-box;
  }
</style>