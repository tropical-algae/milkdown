import ast
import asyncio
from itertools import chain
import os
from typing import Any, Optional

from milkdown.common.logging import logger
from milkdown.service.llm.base import OpenAIBase
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam


class EntityAligner(OpenAIBase):
    __model_tag__ = "entity_aligner"
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        prompt_path: str,
        max_retries: int = 3,
        retry: int = 3,
        **kwargs,
    ) -> None:
        super().__init__(
            base_url=base_url, 
            api_key=api_key, 
            prompt_path=prompt_path, 
            max_retries=max_retries, 
            **kwargs
        )
        self.retry = retry

    async def _async_inference(self, content: Any, model: Optional[str] = None, **kwargs) -> dict[str, list]:
        result: dict = {}
        retry = 0
        while len(result) == 0 and retry <= self.retry:
            if retry > 0:
                logger.warning(f"Retry[{retry}/{self.retry}] content: {content}")
            retry += 1
            output = await super()._async_inference(content=content, model=model, **kwargs)
            try:
                result: dict = ast.literal_eval(output)
                break
            except Exception as err:
                logger.error(f"{err}. Failed to evaluate output: {output}")
        return result
    
    @staticmethod
    def _filter_duplicates(data: dict[str, list]) -> dict[str, list]:
        return {k: list(set(v)) for k, v in data.items()}

    async def run(
        self, 
        paragraph: str, 
        entities: list[str], 
        model: Optional[str] = None, 
        **kwargs
    ) -> str:

        message: list = [
            ChatCompletionAssistantMessageParam(
                content="You are an assistant that only outputs valid JSON.", 
                role="assistant"
            ),
            ChatCompletionUserMessageParam(
                content=self._set_prompt(
                    input={"text": paragraph, "entities": str(entities)}
                ),
                role="user"
            )
        ]
        
        result = await self._async_inference(content=message, model=model, **kwargs)
        result = self._filter_duplicates(result)

        logger.info(f"Capture relations: {result}")
        return result
