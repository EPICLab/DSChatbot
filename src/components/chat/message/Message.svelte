

<script type="ts">
  import { MessageDisplay, type IChatMessage, type IMessageType } from '../../../common/anachatInterfaces';
  import { anaSuperMode, replying, superModePreviewMessage, chatHistory, anaSideModel, anaShowKernelMessages, anaShowBuildMessages, superModeValue } from '../../../stores';
  import { ContextMenu } from '@lumino/widgets';
  import { CommandRegistry } from '@lumino/commands';
  import { BOT_TARGETS, BOT_TYPES, checkTarget, cloneMessage, messageTarget } from "../../../common/messages";

  import Eye from '../../icons/eye.svelte';
  import Reply from '../../icons/reply.svelte';

  import { RankedMenu } from '@jupyterlab/ui-components';
  import MessageBalloon from './MessageBalloon.svelte';

  export let message: IChatMessage;
  export let scrollBottom: () => void = () => {};
  export let loading = false;
  export let index: number;
  export let chat: HTMLElement | null = null;
  export let preview: boolean = false;
  let display: boolean = false;
  $: {
    display = message.display === MessageDisplay.Default || $anaSuperMode
    if ((message.display === MessageDisplay.SupermodeInput || message.kernelDisplay === MessageDisplay.SupermodeInput) && !$anaShowBuildMessages) {
      display = false;
    } else if (message.display === MessageDisplay.Hidden && !$anaShowKernelMessages) {
      display = false;
    }
    if (preview) {
      display = true;
    }
  }

  let div: HTMLElement | null = null;

  function select(e: any) {
    if ($replying == message.id) {
      $replying = null;
    } else {
      $replying = message.id;
    }
  }

  function blink(element: HTMLElement | null) {
    if (element) {
      element.onanimationend = () => {
        element.classList.remove("blink-message")
      }
      element.classList.add("blink-message")
    }
  }

  function scroll(e: any) {
    if (chat && message.reply) {
      const element: HTMLElement = chat.getElementsByClassName(`message-${message.reply}`)[0] as HTMLElement;
      blink(element);
      chat.scrollTop = Math.max(0, element.offsetTop - 30);
    }
  }

  function onRightClick(event: any) {
    if ($anaSuperMode) {
      blink(div);
      const commands = new CommandRegistry();
      const contextMenu = new ContextMenu({ commands });
      commands.addCommand('add-reply', {
        label: 'Add to reply',
        execute: () => {
          let newMessage = cloneMessage(message, messageTarget('user'))
          $superModePreviewMessage = [...$superModePreviewMessage, newMessage];
        }
      });
      contextMenu.addItem({
        command: 'add-reply',
        selector: '*',
      });
      commands.addCommand('load-input', {
        label: 'Load to input',
        execute: () => {
          $superModeValue = message.text;
        }
      });
      contextMenu.addItem({
        command: 'load-input',
        selector: '*',
      });
      commands.addCommand('build', {
        label: 'Send to kernel (build)',
        execute: () => {
          let newMessage = cloneMessage(message, {
            reply: $replying,
            ...messageTarget('build')
          })
          chatHistory.addNew(newMessage);
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
              $superModePreviewMessage.splice(target, 0, $superModePreviewMessage[index])
              $superModePreviewMessage.splice(index + 1, 1)
              $superModePreviewMessage = $superModePreviewMessage
            }
          });
          contextMenu.addItem({
            command: 'move-up',
            selector: '*',
          });
        }

        if (index < $superModePreviewMessage.length - 1) {
          commands.addCommand('move-down', {
            label: '⬇️ Move Down',
            execute: () => {
              const target = index + 1
              $superModePreviewMessage.splice(target + 1, 0, $superModePreviewMessage[index])
              $superModePreviewMessage.splice(index, 1)
              $superModePreviewMessage = $superModePreviewMessage
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
            $superModePreviewMessage.splice(index, 1)
            $superModePreviewMessage = $superModePreviewMessage
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
          if (loading) {
            $anaSideModel?.sendSupermode({ remove_loading: message.id });
            loading = false;
          } else {
            $anaSideModel?.sendSupermode({ loading: index });
          }
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

  $: selected = $replying == message.id;
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

  button {
    background: none!important;
    border: none;
    padding: 0!important;
    cursor: pointer;
  }

  button:focus {
    border-bottom: 1px dotted black;
  }

  .icons {
    height: 0px;
    position: relative;
    top: 5px;
    z-index: 0;
    width: 15px;
    float: right;
  }

  .icons.user {
    float: none;
    margin-left: 15px;
  }

  .icon:hover {
    cursor: pointer;
  }
  
  .icon.hideuserreply {
    display: none;
  }

  .icon.selected :global(svg) {
    fill: green;
  }

</style>


<div bind:this={div} class="message-{message.id}" on:contextmenu={onRightClick}> 
  
  {#if display}
    {#if !preview}
      <div class="icons {message.type}">

        {#if chat && message.reply}
          <button title="View replied message" class="icon" on:click={scroll}><Eye/></button>
        {/if}

        <button 
          title={selected? "Replying to" : "Reply to"}
          class="icon"
          class:selected={selected} 
          class:hideuserreply={!$anaSuperMode && message.type == 'user'}
          on:click={select}
        ><Reply/></button>
      </div>
    {/if}
    <MessageBalloon {message} {loading} {preview} {scrollBottom}/>
  {/if}
</div>
