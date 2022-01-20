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

export interface IChatMessage {
  text: string;
  type: 'user' | 'bot' | 'error';
  timestamp: number;
}
