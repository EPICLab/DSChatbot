<script type="ts">
  import type { IMessagePart } from "../../../../common/chatbotInterfaces";
  import { marked } from 'marked';
  import { onMount } from "svelte";
  import CodeWidget from "../../../generic/CodeWidget.svelte";

  export let messagePart: IMessagePart;
  export let scrollBottom: () => void;
  let codeItems: {[ id:string]: string}= {};

  function escape(html: string) {
    /*
      Function partially obtained from marked: https://github.com/markedjs/marked/blob/8c7bca87029e1a346232e87ed8f63283069f0c64/src/helpers.js#LL16C8-L28C2
      LICENSE: MIT. Copyright (c) 2018+, MarkedJS (https://github.com/markedjs/) Copyright (c) 2011-2018, Christopher Jeffrey (https://github.com/chjj/)
    */
    const escapeTest = /[&<>"']/;
    const escapeReplacements = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    };
    const getEscapeReplacement = (ch: keyof typeof escapeReplacements) => escapeReplacements[ch];
    if (escapeTest.test(html)) {
      return html.replace(new RegExp(escapeTest.source, 'g'), getEscapeReplacement as any);
    }
    return html;
  }

  const renderer = {
    code(code:string, infostring: string, escaped: boolean): string {
      code = code.replace(/\n$/, '') + '\n';
      let id = `newtown-markdown-code-${crypto.randomUUID()}`;
      codeItems[id] = code.trim();
      return `<pre id="${id}"><code>`
          + (escaped ? code : escape(code))
          + '</code></pre>\n';

    }
  }

  marked.use({ renderer });


  onMount(async () => {
    for (const [cid, code] of Object.entries(codeItems)) {
      let element =  document.getElementById(cid);
      if (element && element.parentNode) {
        const newElement = document.createElement('div');
        element.parentNode.replaceChild(newElement, element);
        element.innerHTML = "";
        new CodeWidget({
          target: newElement,
          props: {
            code, 
            scrollBottom,
          }
        })
      }
    }
  });

</script>

<div>{@html marked.parse(messagePart.text.trim())}</div>

<style>
  div {
    white-space: normal;
  }

  div :global(pre) {
    margin: 0;
  }
</style>