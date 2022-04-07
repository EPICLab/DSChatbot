export interface IAnaChatStatus {
  connectedOnce: boolean;
  connectedNow: boolean;
  serverSide: boolean;
  hasKernel: boolean;
}

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

export interface IChatMessage {
  text: string | IOptionItem[];
  type: 'user' | 'bot' | 'error' | 'options' | 'cell';
  timestamp: number;
}
