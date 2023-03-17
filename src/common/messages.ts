import { get } from "svelte/store";
import type { IChatInstance } from "../chatinstance";
import { wizardPreviewMessage, wizardValue } from "../stores";
import { KernelProcess, MessageDisplay, type IChatMessage, type IMessagePart, type IMessagePartType, type IMessageType, type IOptionItem, type ITargetDefinition } from "./chatbotInterfaces";

const TYPE_DEFS: { [key: string]: IMessagePartType } = {
  't': 'text',
  'text': 'text',
  'h': 'html',
  'html': 'html',
  'u': 'ul',
  'ul': 'ul',
  'unordered': 'ul',
  'o': 'ol',
  'ol': 'ol',
  'ordered': 'ol',
  'fu': 'ful',
  'ful': 'ful',
  'full-unordered': 'ful',
  'fo': 'fol',
  'fol': 'fol',
  'full-ordered': 'fol',
  'c': 'code',
  'code': 'code',
  'dc': 'direct-code',
  'direct-code': 'direct-code',
  'i': 'input',
  'input': 'input',
  'w': 'web-panel',
  'web': 'web-panel',
  'web-panel': 'web-panel',
  'html-panel': 'html-panel',
  'text-panel': 'text-panel',
  'f': 'form',
  'form': 'form',
  'md': 'markdown',
  'markdown': 'markdown',
  'meta': 'metadata',
  'metadata': 'metadata'
}

export function cloneMessage(message: IChatMessage, other?: Partial<IChatMessage>) {
  let newMessage = { ...message, ...other }
  newMessage.id = crypto.randomUUID(),
  newMessage.timestamp = +new Date()
  return newMessage
}

export type IMessageTarget = 'bot' | 'user' | 'kernel' | 'build';


export function messageTarget(target: IMessageTarget): ITargetDefinition {
  if (target == 'user') {
    return {
      display: MessageDisplay.Default,
      kernelProcess: KernelProcess.Prevent,
      kernelDisplay: MessageDisplay.Default
    }
  } else if (target == 'kernel') {
    return { 
      display: MessageDisplay.Hidden,
      kernelProcess: KernelProcess.Force,
      kernelDisplay: MessageDisplay.Default
    }
  } else if (target == 'build') {
    return { 
      display: MessageDisplay.Hidden,
      kernelProcess: KernelProcess.Force,
      kernelDisplay: MessageDisplay.WizardModeInput
    }
  } 
  // else if (target == 'bot') {
  return {
    display: MessageDisplay.Default,
    kernelProcess: KernelProcess.Process,
    kernelDisplay: MessageDisplay.Default
  }
}

export function checkTarget(message: ITargetDefinition): IMessageTarget {
  if (message.kernelProcess == KernelProcess.Process) {
    return 'bot';
  } else if (message.display == MessageDisplay.Default) {
    return 'user';
  } else if (message.kernelDisplay == MessageDisplay.Default) {
    return 'kernel';
  }
  return 'build'
}

export interface ITargetItem {
  target: IMessageTarget;
  label: string;
  key: string;
  style: string;
}

export const BOT_TARGETS: ITargetItem[] = [
  {target: 'user', label: 'User', key: 's', style: 'newton-message-target-user'},
  {target: 'kernel', label: 'Kernel', key: 'k', style: 'newton-message-target-hidden'},
  {target: 'build', label: 'Build', key: 'b', style: 'newton-message-target-tobuild'},
]

export interface ITypeItem {
  type: IMessageType;
  label: string;
  key: string;
  style: string;
}

export const BOT_TYPES: ITypeItem[] = [
  {type: 'bot', label: 'Newton', key: 'n', style: 'newton-message-type-bot'},
  {type: 'user', label: 'User', key: 'u', style: 'newton-message-type-user'},
  {type: 'error', label: 'Error', key: 'e', style: 'newton-message-type-error'},
]

export function extractOptions(text: string, type: 'ul' | 'ol'): IOptionItem[] {
  let optionId = 0;
  let options: IOptionItem[] = [];
  if (!text) {
    return options;
  }
  text = text.trim();
  if (text[0] == '-' || text[0] == '!') {
    text = text.substring(1).trim()
  }
  let lines = text.split("\n-");
  options = lines.map((line, index) => {
    let newText = line.trim() 
    let key = `OP-${optionId++}: ${newText}`
    const fields = newText.split("::bot::")
    if (fields.length == 2) {
      key = fields[0].trim()
      newText = fields[1].trim()
    } 
    if (type == 'ol') {
      newText = (index + 1) + '. ' + newText;
    }
    return {
      'key': key,
      'label': newText
    }
  })
  return options;
}

export function splitUnifiedMessage(text: string): IMessagePart[] {
  let items: IMessagePart[] = [];

  for (let partText of text.split('####')) {
    let trim = partText.trim()
    if (trim.length == 0) {
      continue;
    }
    let septype: string[] = trim.split(/#:(.*)/s, 2)
    if (septype.length == 1) {
      items.push({
        type: 'text',
        text: septype[0].trim(),
        source: partText
      })
    } else {
      let type = TYPE_DEFS[septype[0].trim().toLowerCase()] || 'text';
      items.push({
        type: type,
        text: septype[1].trim(),
        source: partText
      })
    }
  }
  return items;
}

async function digestText(text: string) {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const hash = await crypto.subtle.digest('SHA-1', data);
  return btoa(String.fromCharCode(...new Uint8Array(hash)));
}

async function createMetadata(chatInstance: IChatInstance, message: IChatMessage) {
  let items: IMessagePart[] = splitUnifiedMessage(message.text);
  items = items.filter(function (part) {
    if (part.type == "metadata") {
      try {
        const data = JSON.parse(part.text);
        return data.type != 'reuse';
      } catch(e) {
      }
    }
    return true;
  });
  let text = items.map((item) => item.source).join("####");
  if (items[0].type != 'text') {
    text = "####" + text;
  }

  const metadata = {
    'type': 'reuse',
    'instance': chatInstance.chatName,
    'id': message.id,
    'hash': await digestText(text.trim()),
  };
  return text + `\n####metadata#:\n${JSON.stringify(metadata)}`
  
}

async function cloneMessageWithMetadata(chatInstance: IChatInstance, message: IChatMessage, preview: boolean) {
  let newMessage = cloneMessage(message, messageTarget('user'))
  if (!preview) {
    newMessage.text = await createMetadata(chatInstance, message);
  }
  return newMessage;
}

export async function sendMessageToBuild(chatInstance: IChatInstance, message: IChatMessage, preview: boolean) {
  let newMessage = await cloneMessageWithMetadata(chatInstance, message, preview);
  wizardPreviewMessage.set([...get(wizardPreviewMessage), newMessage]);
}

export async function sendMessageToUser(chatInstance: IChatInstance, message: IChatMessage, preview: boolean) {
  let newMessage = await cloneMessageWithMetadata(chatInstance, message, preview);
  chatInstance.addNew(newMessage);
}


export async function sendMessageToWizardInput(chatInstance: IChatInstance, message: IChatMessage, preview: boolean) {
  wizardValue.set(await createMetadata(chatInstance, message))
}

export interface IFormElementItem {
  id: number
  type: string
  label: string 
  rest: string | null
  value: string
}
