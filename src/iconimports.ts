import { LabIcon } from '@jupyterlab/ui-components';

import anaChatSvgstr from '../style/img/anachat.svg';
import kernelonSvgstr from '../style/img/kernelon.svg';
import kerneloffSvgstr from '../style/img/kerneloff.svg';
import disconnectedSvgstr from '../style/img/disconnected.svg';
import neverconnectedSvgstr from '../style/img/neverconnected.svg';

export const anaChatIcon = new LabIcon({
  name: 'anachat:icon',
  svgstr: anaChatSvgstr
});
export const kernelonIcon = new LabIcon({
  name: 'julynter:kernelon',
  svgstr: kernelonSvgstr
});
export const kerneloffIcon = new LabIcon({
  name: 'julynter:kerneloff',
  svgstr: kerneloffSvgstr
});
export const disconnectedIcon = new LabIcon({
  name: 'julynter:disconnected',
  svgstr: disconnectedSvgstr
});
export const neverconnectedIcon = new LabIcon({
  name: 'julynter:neverconnected',
  svgstr: neverconnectedSvgstr
});
