import { KernelProcess, MessageDisplay, type IChatMessage, type IMessagePart, type IMessagePartType, type IMessageType, type IOptionItem, type ITargetDefinition } from "./anachatInterfaces";

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
  {target: 'user', label: 'User', key: 's'},
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
  {type: 'user', label: 'User', key: 'u'},
  {type: 'error', label: 'Error', key: 'e'},
]

export interface IEditorTypeItem {
  label: string;
  text: string;
  key: string;
}

export const BOT_EDITOR_TYPES: IEditorTypeItem[] = [
  {label: 'Text/A', text:'####text#:\n', key: 'a'},
  {label: 'Ordered/O', text:'####fol#:\n', key: 'o'},
  {label: 'Options/I', text:'####ful#:\n', key: 'i'},
  {label: 'Continue/Y', text:'####fol#:\n- Continue', key: 'y'},
  {label: 'Code/C', text:'####text#:\nCopy the following code to the notebook:\n####code#:\n', key: 'c'},
  {label: 'Just Code/F', text:'####code#:\n', key: 'f'}
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
        text: septype[0].trim()
      })
    } else {
      let type = TYPE_DEFS[septype[0].trim().toLowerCase()] || 'text';
      items.push({
        type: type,
        text: septype[1].trim()
      })
    }
  }
  return items;
}
