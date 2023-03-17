

<script type="ts">
  import { MessageDisplay, type IChatMessage, type IMessageType } from '../../../common/chatbotInterfaces';
  import { wizardMode, replying, wizardPreviewMessage } from '../../../stores';
  import { ContextMenu } from '@lumino/widgets';
  import { CommandRegistry } from '@lumino/commands';
  import { BOT_TARGETS, BOT_TYPES, checkTarget, cloneMessage, messageTarget, sendMessageToBuild, sendMessageToUser, sendMessageToWizardInput } from "../../../common/messages";

  import { RankedMenu } from '@jupyterlab/ui-components';
  import MessageParts from "./MessageParts.svelte";
  import MessageBottom from "./MessageBottom.svelte";
  import Reply from "./Reply.svelte";
  import type { IChatInstance } from '../../../chatinstance';

  export let chatInstance: IChatInstance;
  export let message: IChatMessage;
  export let scrollBottom: () => void = () => {};
  export let index: number;
  export let chat: HTMLElement | null = null;
  export let preview: boolean = false;

  let {showBuildMessages, showKernelMessages, showReplied, directSendToUser } = chatInstance.config;

  let display: boolean = false;
  let reply: IChatMessage | null | undefined = null;

  function onRightClick(event: any) {
    if ($wizardMode) {
      const commands = new CommandRegistry();
      const contextMenu = new ContextMenu({ commands });
      commands.addCommand('add-reply', {
        label: 'Add to reply',
        execute: async () => {
          await sendMessageToBuild(chatInstance, message, preview);
        }
      });
      contextMenu.addItem({
        command: 'add-reply',
        selector: '*',
      });
      commands.addCommand('load-input', {
        label: 'Load to input',
        execute: async () => {
          await sendMessageToWizardInput(chatInstance, message, preview);
        }
      });
      contextMenu.addItem({
        command: 'load-input',
        selector: '*',
      });
      
      if ($directSendToUser) {
        commands.addCommand('send-user', {
          label: 'Send to user',
          execute: async () => {
            await sendMessageToUser(chatInstance, message, preview);
          }
        });
        contextMenu.addItem({
          command: 'send-user',
          selector: '*',
        });
      }
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

  function setReplyVisibility(visible: boolean) {
    reply = visible ? chatInstance.findById(message.reply) : null;
  }

  $: {
    display = message.display === MessageDisplay.Default || $wizardMode
    if ((message.display === MessageDisplay.WizardModeInput || message.kernelDisplay === MessageDisplay.WizardModeInput) && !$showBuildMessages) {
      display = false;
    } else if (message.display === MessageDisplay.Hidden && !$showKernelMessages) {
      display = false;
    }
    if (preview) {
      display = true;
    }
  }
  $: if ($wizardMode && !preview) setReplyVisibility($showReplied);
 
</script>


<div class="message-{message.id}" on:contextmenu={onRightClick}> 
  {#if display}
    <div class="outer {message.type}">
      <div 
        class:newton-message-target-hidden={message.display == MessageDisplay.Hidden} 
        class:newton-message-target-build={message.display == MessageDisplay.WizardModeInput} 
        class:newton-message-target-tobuild={message.kernelDisplay == MessageDisplay.WizardModeInput} 
        class="inner"
      >
        <div class="main">
          {#if reply}
            <Reply {chatInstance} {reply} {chat} {scrollBottom}/>
          {/if}
          <MessageParts {chatInstance} {message} {preview} {scrollBottom}/>
        </div>
        {#if !preview}
          <MessageBottom {chatInstance} {message} {index} viewReplied={!!reply} on:toggleViewReplied={(event) => setReplyVisibility(event.detail.viewReplied)}/>
        {/if}
      </div>
    </div>
  {/if}
</div>


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

  .outer {
    padding: 0 10px;
    width: inherit;
  }

  .inner {
    border-radius: 5px;
    border: 1px solid gray;
    margin-bottom: 0.8em;
    
    white-space: pre-line;
  }

  .user .inner {
    background-color: var(--newton-message-user-color);
  }

  .bot .inner {
    background-color: var(--newton-message-bot-color);
  }

  .error .inner {
    background-color: var(--newton-message-error-color);
  }

  .user .inner {
    margin-left: 4em;
    border-radius: 0.5rem 0.5rem 0 0.5rem;
    background-color: var(--newton-message-user-color);
    flex-direction: row-reverse;
  }

  .bot .inner {
    margin-right: 4em;
    background-color: var(--newton-message-bot-color);
    border-radius: 0.5rem 0.5rem 0.5rem 0;
  }

  .error .inner {
    margin-right: 4em;
    background-color: var(--newton-message-error-color);
    border-radius: 0.5rem 0.5rem 0.5rem 0;
  }

  .main {
    padding: 0.4em;
  }
</style>