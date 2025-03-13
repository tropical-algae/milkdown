import os
import ast
import asyncio

from typing import Optional
from itertools import chain

from milkdown.app.models.model_relation_tuples import RelationTuples
from milkdown.app.util import sentence_separate
from milkdown.common.logging import logger
from milkdown.service.llm.base import OpenAIBase
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam


class KnowlRelationExtractor(OpenAIBase):
    __model_tag__ = "knowledge_relation_exrtactor"

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
        content: str | list, 
        model: Optional[str] = None, 
        **kwargs
    ) -> list:
        results: list = []
        retry = 0
        messgae = [
            ChatCompletionAssistantMessageParam(
                content="You are an assistant that only outputs valid List.", 
                role="assistant"
            ),
            ChatCompletionUserMessageParam(
                content=self._set_prompt(input={"text": content}),
                role="user"
            )
        ]

        while len(results) == 0 and retry <= self.retry:
            if retry > 0:
                logger.warning(f"Retry[{retry}/{self.retry}] content: {content}")
            retry += 1
            output = await super()._async_inference(content=messgae, model=model)
            try:
                results: list = ast.literal_eval(output)
                for result in results:
                    result["sentence"] = content
                    result["sentence_index"] = kwargs.get("index", -1)
                break
            except Exception as err:
                logger.error(f"{err}. Failed to evaluate output: {output}")
        return results

    async def run(
        self, 
        paragraph: str, 
        model: Optional[str] = None, 
        **kwargs
    ) -> list[RelationTuples]:

        # logger.info(f"Loading prompt for input: {str(content)}")
        sentences: list[str] = sentence_separate(paragraph)
        contents: list[tuple] = [(index, sentence) for index, sentence in enumerate(sentences)]

        tasks = [
            self._async_inference(
                content=content, 
                model=model, 
                index=index, 
                **kwargs
            )
            for index, content in contents
        ]
        outptus = await asyncio.gather(*tasks)
        results = list(chain.from_iterable(outptus))
        results = [self._clean_dirty_data(result) for result in results]

        logger.info(f"Capture relations: {outptus}")
        return [RelationTuples.model_validate(result) for result in results]
