import os
import ast
import asyncio

from typing import Any, Optional
from itertools import chain

from milkdown.app.models.model_relation_tuples import RelationTuples
from milkdown.app.util import sentence_separate
from milkdown.common.logging import logger
from milkdown.service.llm.base import OpenAIBase
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam


class EntityExtractor(OpenAIBase):
    __model_tag__ = "entity_extractor"

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

    @staticmethod
    def _clean_dirty_data(data: dict) -> dict:
        try:
            data["subject"] = str(data["subject"]).strip()
            data["object"] = str(data["object"]).strip()
            data["relation"] = str(data["relation"]).strip()
        except Exception as err:
            logger.error(f"{err}. Failed to clean certain relation: {data}")

        return data

    async def _async_inference(
        self, 
        content: Any, 
        model: Optional[str] = None, 
        **kwargs  # type: ignore
    ) -> list:
        assert isinstance(content, dict)
        
        result: list[str] = []
        retry = 0
        messgae = [
            ChatCompletionAssistantMessageParam(
                content="You are an assistant that only outputs valid List.", 
                role="assistant"
            ),
            ChatCompletionUserMessageParam(
                content=self._set_prompt(input=content),
                role="user"
            )
        ]

        while len(result) == 0 and retry <= self.retry:
            if retry > 0:
                logger.warning(f"Retry[{retry}/{self.retry}] content: {content}")
            retry += 1
            output = await super()._async_inference(content=messgae, model=model)
            try:
                result: list[str] = ast.literal_eval(output)
                break
            except Exception as err:
                logger.error(f"{err}. Failed to evaluate output: {output}")
        return result

    async def run(
        self, 
        sentence: str, 
        model: Optional[str] = None, 
        **kwargs
    ) -> list[RelationTuples]:
        # logger.info(f"Loading prompt for input: {str(content)}")
        
        # contents: list[tuple] = [(index, sentence) for index, sentence in enumerate(sentences)]

        # tasks = [
        #     self._async_inference(
        #         content=content, 
        #         model=model, 
        #         index=index, 
        #         **kwargs
        #     )
        #     for index, content in contents
        # ]
        input = {"text": sentence}
        # outptus = await asyncio.gather(*tasks)
        # results = list(chain.from_iterable(outptus))
        result = await self._async_inference(content=input, model=model, **kwargs)
        logger.info(f"Capture entities: {result}")
        return result # [EntityModel.model_validate(r) for r in result]
