import { KernelProcess, MessageDisplay, type IChatMessage, type IMessageType, type IOptionItem, type ITargetDefinition } from "./anachatInterfaces";

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
      kernelDisplay: MessageDisplay.SupermodeInput
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
}

export const BOT_TARGETS: ITargetItem[] = [
  {target: 'user', label: 'User', key: 't'},
  {target: 'kernel', label: 'Kernel', key: 'k'},
  {target: 'build', label: 'Build', key: 'b'},
]

export interface ITypeItem {
  type: IMessageType;
  label: string;
  key: string;
}

export const BOT_TYPES: ITypeItem[] = [
  {type: 'bot', label: 'Newton', key: 'n'},
  {type: 'ordered', label: 'Ordered', key: 'o'},
  {type: 'options', label: 'Items', key: 'i'},
  {type: 'cell', label: 'Code', key: 'c'},
  {type: 'user', label: 'User', key: 'u'},
  {type: 'error', label: 'Error', key: 'e'}
]

export function extractOptions(text: string, type: IMessageType): IOptionItem[] {
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
    if (type == 'ordered') {
      newText = (index + 1) + '. ' + newText;
    }
    return {
      'key': key,
      'label': newText
    }
  })
  return options;
}
