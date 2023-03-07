

<script type="ts">
  import { MessageDisplay, type IChatInstance, type IChatMessage, type IMessageType } from '../../../common/chatbotInterfaces';
  import { wizardMode, replying, wizardPreviewMessage, wizardValue } from '../../../stores';
  import { ContextMenu } from '@lumino/widgets';
  import { CommandRegistry } from '@lumino/commands';
  import { BOT_TARGETS, BOT_TYPES, checkTarget, cloneMessage, messageTarget } from "../../../common/messages";

  import { RankedMenu } from '@jupyterlab/ui-components';
  import MessageBalloon from './MessageBalloon.svelte';

  export let chatInstance: IChatInstance;
  export let message: IChatMessage;
  export let scrollBottom: () => void = () => {};
  export let index: number;
  export let chat: HTMLElement | null = null;
  export let preview: boolean = false;

  let {showIndex, showBuildMessages, showKernelMessages} = chatInstance.config;

  let display: boolean = false;
  $: {
    display = message.display === MessageDisplay.Default || $wizardMode
    if ((message.display === MessageDisplay.SupermodeInput || message.kernelDisplay === MessageDisplay.SupermodeInput) && !$showBuildMessages) {
      display = false;
    } else if (message.display === MessageDisplay.Hidden && !$showKernelMessages) {
      display = false;
    }
    if (preview) {
      display = true;
    }
  }

  let div: HTMLElement | null = null;

  function onRightClick(event: any) {
    if ($wizardMode) {
      const commands = new CommandRegistry();
      const contextMenu = new ContextMenu({ commands });
      commands.addCommand('add-reply', {
        label: 'Add to reply',
        execute: () => {
          let newMessage = cloneMessage(message, messageTarget('user'))
          $wizardPreviewMessage = [...$wizardPreviewMessage, newMessage];
        }
      });
      contextMenu.addItem({
        command: 'add-reply',
        selector: '*',
      });
      commands.addCommand('load-input', {
        label: 'Load to input',
        execute: () => {
          $wizardValue = message.text;
        }
      });
      contextMenu.addItem({
        command: 'load-input',
        selector: '*',
      });
      commands.addCommand('copy-clipboard', {
        label: 'Copy to clipboard',
        execute: () => {
          navigator.clipboard.writeText(message.text);
        }
      });
      contextMenu.addItem({
        command: 'copy-clipboard',
        selector: '*',
      });
      commands.addCommand('build', {
        label: 'Send to kernel (build)',
        execute: () => {
          let newMessage = cloneMessage(message, {
            reply: $replying,
            ...messageTarget('build')
          })
          chatInstance.addNew(newMessage);
        }
      });
      contextMenu.addItem({
        command: 'build',
        selector: '*',
      });

      if (preview) {
        const targetMenu = new RankedMenu({ commands: commands });
        targetMenu.id = 'jp-target-menu';
        targetMenu.title.label = 'Change target';
        BOT_TARGETS.forEach((targetItem) => {
          if (checkTarget(message) === targetItem.target) {
            return;
          }
          const key = `target-${targetItem.target}`
          commands.addCommand(key, {
            label: targetItem.label,
            execute: () => { message = { ...message, ...messageTarget(targetItem.target) } }
          });
          targetMenu.addItem({
            command: key,
          });
        })
        contextMenu.addItem({
          selector: '*',
          type: 'submenu',
          submenu: targetMenu
        });

        const typeMenu = new RankedMenu({ commands: commands });
        typeMenu.id = 'jp-type-menu';
        typeMenu.title.label = 'Change type';
        BOT_TYPES.forEach((typeItem) => {
          if (message.type === typeItem.type) {
            return;
          }
          const key = `type-${typeItem.type}`
          commands.addCommand(key, {
            label: typeItem.label,
            execute: () => { message.type = typeItem.type as IMessageType }
          });
          typeMenu.addItem({
            command: key,
          });
        })
        contextMenu.addItem({
          selector: '*',
          type: 'submenu',
          submenu: typeMenu
        });

        if (index > 0) {
          commands.addCommand('move-up', {
            label: '⬆️ Move Up',
            execute: () => {
              const target = index - 1
              $wizardPreviewMessage.splice(target, 0, $wizardPreviewMessage[index])
              $wizardPreviewMessage.splice(index + 1, 1)
              $wizardPreviewMessage = $wizardPreviewMessage
            }
          });
          contextMenu.addItem({
            command: 'move-up',
            selector: '*',
          });
        }

        if (index < $wizardPreviewMessage.length - 1) {
          commands.addCommand('move-down', {
            label: '⬇️ Move Down',
            execute: () => {
              const target = index + 1
              $wizardPreviewMessage.splice(target + 1, 0, $wizardPreviewMessage[index])
              $wizardPreviewMessage.splice(index, 1)
              $wizardPreviewMessage = $wizardPreviewMessage
            }
          });
          contextMenu.addItem({
            command: 'move-down',
            selector: '*',
          });
        }
        
        commands.addCommand('remove', {
          label: '❌ Remove',
          execute: () => {
            $wizardPreviewMessage.splice(index, 1)
            $wizardPreviewMessage = $wizardPreviewMessage
          }
        });
        contextMenu.addItem({
          command: 'remove',
          selector: '*',
        });

      } else {
        commands.addCommand('loading', {
        label: 'Toggle loading',
        execute: () => {
          message.loading = !message.loading;
          chatInstance.submitSyncMessage({
            id: message.id,
            loading: message.loading
          });
        }
      });
      contextMenu.addItem({
        command: 'loading',
        selector: '*',
      });
      }

      contextMenu.open(event as any);
      event.preventDefault();
      event.stopPropagation();
    }
  }
 
</script>

<style>

 @keyframes blinking {
    0% {
      background-color: lightgreen;
    }
    100% {
      background-color: white;
    }
  }

  :global(.blink-message) { animation: blinking 2s 1; }
</style>


<div bind:this={div} class="message-{message.id}" on:contextmenu={onRightClick}> 
  {#if display}
    {#if $showIndex}
      {index}
    {/if}
    <MessageBalloon {chatInstance} {message} {preview} {scrollBottom} {chat}/>
  {/if}
</div>
