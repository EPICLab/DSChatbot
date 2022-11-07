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

export interface IChatMessage {
  id: string;
  text: string | IOptionItem[];
  type: IMessageType;
  timestamp: number;
  prevent: boolean;
  force: boolean;
  hidden: boolean;
  reply: string | null;
}

export interface IAutoCompleteItem {
  type: string;
  key: string;
  value: string;
  url: string | null;
}

export interface IServerConfig {
  restrict: string | null;
}