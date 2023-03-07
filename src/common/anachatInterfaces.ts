import type { Writable } from "svelte/store";

export type Subset<K> = {
  [attr in keyof K]?: K[attr] extends object
      ? Subset<K[attr]>
      : K[attr] extends object | null
      ? Subset<K[attr]> | null
      : K[attr] extends object | null | undefined
      ? Subset<K[attr]> | null | undefined
      : K[attr];
};

export interface IKernelMatcher {
  language: string | null;
  initScript: string | null;
  evalue: string | null;
}

export const GenericMatcher: IKernelMatcher = {
  language: null,
  initScript: null,
  evalue: null
};

export interface IOptionItem {
  key: string;
  label: string;
}

export type IMessageType = 'user' | 'bot' | 'error';

export enum MessageDisplay {
  Default = 0,
  Hidden,
  SupermodeInput
}

export enum KernelProcess {
  Prevent = 0,
  Process,
  Force
}

export interface IFeedback {
  rate: number;
  reason: string;
  otherreason: string;
}

export interface ITargetDefinition {
  display: MessageDisplay;
  kernelProcess: KernelProcess;
  kernelDisplay: MessageDisplay;
}

export interface IChatMessage extends ITargetDefinition {
  id: string;
  text: string;
  type: IMessageType;
  timestamp: number;
  reply: string | null;
  feedback: IFeedback;
  loading: boolean;

  new?: boolean;
}

export interface IAutoCompleteItem {
  type: string;
  key: string;
  value: string;
  url: string | null;
}

export interface IServerConfig {
  restrict: string[];
}

export type IMessagePartType =
  'text' | 'html' 
  | 'web-panel' | 'text-panel' | 'html-panel'
  | 'ul' | 'ol' | 'ful' | 'fol' | 'form'
  | 'code' | 'direct-code' | 'input';

export interface IMessagePart {
  type: IMessagePartType;
  text: string;
}

export interface IConfigVar<T> extends Writable<T> {
  load: (value: any) => void;
  initialized: boolean;
}

export interface IChatInstanceConfig {
  processInKernel: IConfigVar<boolean>;
  enableAutoComplete: IConfigVar<boolean>;
  enableAutoLoading: IConfigVar<boolean>;
  loading: IConfigVar<boolean>;

  showReplied: IConfigVar<boolean>;
  showIndex: IConfigVar<boolean>;
  showTime: IConfigVar<boolean>;
  showBuildMessages: IConfigVar<boolean>;
  showKernelMessages: IConfigVar<boolean>;
}

export interface IChatInstance extends Writable<IChatMessage[]> {
  push: (newMessage: IChatMessage) => void;
  addNew: (newMessage: IChatMessage) => void;
  load: (data: IChatMessage[]) => void;
  updateMessage: (message: IChatMessage) => void;
  submitSyncMessage: (message: Pick<IChatMessage, 'id'> & Subset<IChatMessage>) => void;
  removeLoading: (messageId: string) => void;
  reset: () => void;
  findById: (messageId: string | null) => IChatMessage | null;
  sendAutoComplete: (requestId: number, query: string) => void;

  configMap: { [id: string]: IConfigVar<any>};
  config: IChatInstanceConfig;
  autoCompleteResponseId: Writable<number>;
  autoCompleteItems: Writable<IAutoCompleteItem[]>;
}
