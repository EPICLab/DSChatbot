"""Defines gpt bot"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ..comm.message import MessageContext 

if TYPE_CHECKING:
    from ..comm.chat_instance import ChatInstance


class GPTBot:
    """GPT bot that connects to Open AI"""

    def __init__(self):
        self.prompt = "You are a chatbot that can help programming.\n\nQ: {}\nA:"
        self.api_key = ""
        self.model_config = {}

    @classmethod
    def config(cls):
        """Defines configuration inputs for bot"""
        return {
            "prompt": ('str', "You are a chatbot that can help programming.\n\nQ: {}\nA:"),
            "model": ('str', "text-davinci-003"),
            "temperature": ('str', '0.7'), # float 0 1
            "max_tokens": ('str', '256'), # int: 1 4000
            "top_p": ('str', '1'), # float 0 1
            "frequency_penalty": ('str', '0'), # flaot 0 2
            "presence_penalty": ('str', '0'), # float 0 2
            "best_of": ('str', '1'), # int 1 20
            "api_key": ("str", "")
        }
    
    def _set_config(self, original, data, key, convert=str):
        """Sets config"""
        self.model_config[key] = convert(data.get(key, original[key]))

    def start(self, instance: ChatInstance, data: dict):
        """Initializes bot"""
        original = self.config()
        self.prompt = data.get("prompt", self.prompt)
        self.api_key = data.get("api_key", "")
        self._set_config(original, data, 'model', str)
        self._set_config(original, data, 'temperature', float)
        self._set_config(original, data, 'max_tokens', int)
        self._set_config(original, data, 'top_p', float)
        self._set_config(original, data, 'frequency_penalty', float)
        self._set_config(original, data, 'presence_penalty', float)
        self._set_config(original, data, 'best_of', int)

        instance.history.append(MessageContext.create_message(
            ("I am a GPT bot"),
            "bot"
        ))
        instance.config["enable_autocomplete"] = False

    def refresh(self, instance: ChatInstance):
        """Refresh chatbot"""
        # pylint: disable=no-self-use
        instance.sync_chat("refresh")

    def process_message(self, context: MessageContext) -> None:
        """Processes user messages"""
        # pylint: disable=unused-argument
        import openai
        openai.api_key = self.api_key
        response = openai.Completion.create(
          prompt=self.prompt.format(context.text),
          **self.model_config
        )
        context.reply(response["choices"][0]["text"])
        return self

    def process_autocomplete(self, instance: ChatInstance, request_id: int, query: str):
        """Processes user autocomplete query"""
        # pylint: disable=unused-argument
        # pylint: disable=no-self-use
        instance.send({
            "operation": "autocomplete-response",
            "responseId": request_id,
            "items": [],
        })
