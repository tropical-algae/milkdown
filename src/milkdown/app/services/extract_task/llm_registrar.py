import os
from milkdown.service.llm.base import OpenAIBase
from milkdown.common.config import settings

class LLMRegistrar:
    def __init__(self, prompt_root: str):
        self.prompt_root = prompt_root
        self.model_services: dict[str, OpenAIBase] = {}
        self._load_model_services()

    def _load_model_services(self) -> None:
        model_services = OpenAIBase.__subclasses__()
        for model_service in model_services:
            tag = model_service.__model_tag__
            prompt_path = os.path.join(self.prompt_root, f"{tag}.yaml")
            self.model_services[tag] = model_service(
                base_url=settings.GPT_BASE_URL,
                api_key=settings.GPT_API_KEY,
                prompt_path=prompt_path,
            )
    
    def get(self, model_tag: str) -> OpenAIBase | None:
        return self.model_services.get(model_tag, None)

llm_registrar = LLMRegistrar(prompt_root=settings.LOCAL_PROMPT_ROOT)