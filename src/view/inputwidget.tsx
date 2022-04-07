import { ReactWidget } from '@jupyterlab/apputils';
import React from 'react';

export class InputWidget extends ReactWidget {
  private sendText: (text: string) => void;

  constructor(sendText: (text: string) => void) {
    super();
    this.sendText = sendText;
    this.addClass('anachat-chatbox');
  }

  protected render(): JSX.Element {
    return <ResizableTextarea sendText={this.sendText} />;
  }
}

interface ITextAreaProps {
  sendText: (text: string) => void;
}

interface ITextArea {
  value: string;
}

class ResizableTextarea extends React.Component<ITextAreaProps, ITextArea> {
  textarea: HTMLTextAreaElement | null;

  constructor(props: any) {
    super(props);
    this.textarea = null;
    this.state = {
      value: ''
    };
  }

  resize(): void {
    if (this.textarea) {
      this.textarea.style.height = '0px';
      const scrollHeight = this.textarea.scrollHeight;
      this.textarea.style.height = scrollHeight + 'px';
    }
  }

  handleChange = (event: any) => {
    this.resize();
    this.setState({
      value: event.target.value
    });
  };

  onEnterPress = (event: any) => {
    if (event.keyCode === 13 && event.shiftKey === false) {
      event.preventDefault();
      this.props.sendText(this.state.value);
      this.setState({ value: '' });
      if (this.textarea) {
        this.textarea.value = '';
      }
    }
  };

  componentDidMount() {
    this.resize();
  }

  render() {
    return (
      <textarea
        ref={c => (this.textarea = c)}
        placeholder={'Talk to Ana here...'}
        className={'textarea'}
        onChange={this.handleChange}
        onKeyDown={this.onEnterPress}
      />
    );
  }
}