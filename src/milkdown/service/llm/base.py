import os
import re
from functools import partial
from typing import Any, Optional, Union

from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletionUserMessageParam

from milkdown.common.config import settings
from milkdown.common.util import load_yaml


class OpenAIBase:
    __model_tag__ = "openai"
    _subclasses = []

    def __init__(
        self,
        base_url: str,
        api_key: str,
        prompt_path: str,
        max_retries: int = 3,
        **kwargs,
    ) -> None:
        assert os.path.isfile(prompt_path)
        
        self.prompt_configs = load_yaml(prompt_path)
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = self.prompt_configs.get("model", "gpt-3.5-turbo-ca")
        self.prompt = self.prompt_configs

        # self.client = OpenAI(
        #     base_url=settings.GPT_BASE_URL, api_key=settings.GPT_API_KEY, timeout=20
        # )
        self.async_client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            max_retries=max_retries,
            timeout=20,
            **kwargs,
        )
        self._load_config()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        OpenAIBase._subclasses.append(cls)

    @classmethod
    def subclasses(cls):
        return cls._subclasses

    def _load_config(self):
        prompt_version = self.prompt_configs.get("version", "v1")
        prompts: dict = self.prompt_configs.get("prompts", {})
        
        self.is_activate: bool = self.prompt_configs.get("activate", False)
        self.prompt: str = prompts.get(prompt_version, "")
        

    def _set_prompt(self, input: dict, prompt: str | None = None) -> str:
        def replacer(match, params: dict):
            var_name = match.group(1)
            return params.get(var_name, match.group(0))

        def standardization(params: Union[dict, str]) -> dict:
            params = {"data": params} if isinstance(input, str) else input
            return {k: str(v) for k, v in params.items()}

        params = standardization(input)
        pattern = re.compile(r"\$\{(\w+)\}")
        prompt = prompt if prompt else self.prompt
        return pattern.sub(partial(replacer, params=params), prompt)

    # def _inference(self, content: str, model: Optional[str] = None, **kwargs) -> str:
    #     model = model or self.default_model

    #     messages = [ChatCompletionUserMessageParam(content=content, role="user")]
    #     completion = self.client.chat.completions.create(
    #         messages=messages, model=model, **kwargs  # type: ignore
    #     )
    #     response = completion.choices[0].message.content
    #     return response or "None"

    async def _async_inference(self, content: Any, model: Optional[str] = None, **kwargs) -> str:
        assert isinstance(content, str) or isinstance(content, list), f"Illegal LLM input type: {type(content)}"

        model = model or self.default_model
        if isinstance(content, str):
            messages = [ChatCompletionUserMessageParam(content=content, role="user")]
        if isinstance(content, list):
            messages=content

        completion = await self.async_client.chat.completions.create(messages=messages, model=model, temperature=0.4, **kwargs)

        response = completion.choices[-1].message.content
        return response or "None"
    
    async def run(
        self, 
        **kwargs
    ) -> Any:
        pass