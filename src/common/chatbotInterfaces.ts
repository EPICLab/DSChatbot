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
  WizardModeInput
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
  | 'code' | 'direct-code' | 'input' | 'metadata' | 'markdown';

export interface IMessagePart {
  type: IMessagePartType;
  text: string;
  source: string;
}

export interface IConfigVar<T> extends Writable<T> {
  load: (value: any) => void;
  initialized: boolean;
}

export type ILoaderForm = { [formkey: string]: [string, any] } 
