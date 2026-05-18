import json
import re
from typing import Optional

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from app.config.openai import OpenAiConfig
from app.modules.openAi.data_models import Answer
from app.modules.openAi.functions import create_answer_function
from app.utils.log_util import LogUtil


class OpenAiProvider:
    """
    This class provides an interface to the OpenAI API.
    """

    def __init__(self):
        self._client: Optional[OpenAI] = None

    def client(self) -> OpenAI:
        """Get the existing OpenAI client or create a new one if it does not exist.

        Returns:
            OpenAI: The OpenAI API client.
        """
        if self._client is None:
            try:
                self._client = OpenAI(api_key=OpenAiConfig.API_KEY)
            except Exception as e:
                logger = LogUtil.get_logger()
                logger.error(
                    "Exception in OpenAiProvider.client(): %s", e, extra={"code": 3018}
                )
        return self._client

    def chat_completion(
        self, messages: list, func: dict | None = None, model: str | None = None
    ) -> str | dict | None:
        """
        Requests a chat completion from the OpenAI API based on the provided messages and optional model.

        :param messages: Structured messages for OpenAI.
        :param func: A dictionary representing a function to be applied to the chat completion, defaults to None.
        :param model: The model to use for completing the messages,
        defaults to the value of the `chat_completion_model` setting in the `openai_settings` module.
        :return: The response from the OpenAI API, or `None` if the response was not successful.
        """
        model = model if model is not None else OpenAiConfig.MODEL
        response = None
        logger = LogUtil.get_logger()
        client = self.client()
        try:
            if func is not None:
                response = client.chat.completions.create(
                    model=model, messages=messages, tools=[func], tool_choice=func
                )
            else:
                response = client.chat.completions.create(
                    model=model, messages=messages
                )
        except Exception as e:
            logger.error(
                "Exception in OpenAiProvider.chat_completion(): %s",
                e,
                extra={"code": 5733},
            )

        if not isinstance(response, ChatCompletion):
            logger.warning(
                "warning in OpenAiProvider.chat_completion(): response is not a ChatCompletion object",
                extra={"code": 6034, "response": str(response)},
            )
            return None
        choices = response.choices
        if not choices:
            logger.warning(
                "Warning in OpenAiProvider.chat_completion(): choices is not a list",
                extra={"code": 6634, "response": str(response)},
            )
            return None
        if func:
            result = json.loads(choices[0].message.tool_calls[0].function.arguments)
        else:
            result = (
                choices[0].message.content
                if choices[0].message and choices[0].message.content
                else None
            )
        return result

    def answer(
        self,
        entity: str,
        question: str,
        justify: bool = False,
        answer_json_type: str = "string",
        optional_answer: bool = False,
    ) -> Optional[Answer]:
        function = create_answer_function(
            justify=justify,
            answer_json_type=answer_json_type,
            optional_answer=optional_answer,
        )
        prompt_string = f"**Referring to**: {entity}\n\n**Question**: {question}"
        prompt = [{"role": "system", "content": prompt_string}]
        response = self.chat_completion(prompt, func=function)
        if response is not None:
            return Answer(
                answer=response.get("answer"),
                justification=response.get("justification"),
            )
        return None

    def translate_text_to_english_exact(self, text: str) -> str | None:
        """
        Translate text to English while preserving exact meaning and terminology.
        """
        if not text or not text.strip():
            return None
        answer = self.answer(
            entity=text,
            question=(
                "Translate this text to English with exact meaning preservation. "
                "Do not summarize. Do not infer missing details. "
                "Keep technical and professional terminology accurate. "
                "Return only the translated English text."
            ),
            answer_json_type="string",
        )
        if answer is None or answer.answer is None:
            return None
        translated = str(answer.answer).strip()
        return translated if translated else None