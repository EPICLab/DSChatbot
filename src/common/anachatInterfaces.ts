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