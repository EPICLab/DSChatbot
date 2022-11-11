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

export type IMessageType = 'user' | 'bot' | 'error' | 'options' | 'cell' | 'usercode' | 'botcode';

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

export interface ITargetDefinition {
  display: MessageDisplay;
  kernelProcess: KernelProcess;
  kernelDisplay: MessageDisplay;
}

export interface IChatMessage extends ITargetDefinition {
  id: string;
  text: string | IOptionItem[];
  type: IMessageType;
  timestamp: number;
  reply: string | null;
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