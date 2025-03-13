import re
import nltk

from typing import Literal
import uuid
from milkdown.app.models.model_relation_tuples import RelationTuples
from milkdown.common.config import settings
from milkdown.common.util import get_local_time
from langdetect import detect
from nltk.tokenize import sent_tokenize
from milkdown.common.logging import logger



def zh_cut_sentence(paragraph: str) -> list[str]:
    paragraph = re.sub('([。！？\?])([^”’])', r"\1\n\2", paragraph)  # 单字符断句符
    paragraph = re.sub('(\.{6})([^”’])', r"\1\n\2", paragraph)  # 英文省略号
    paragraph = re.sub('(\…{2})([^”’])', r"\1\n\2", paragraph)  # 中文省略号
    paragraph = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', paragraph)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    paragraph = paragraph.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    return paragraph.split("\n")


def download_nltk_resources() -> None:
    logger.info(f"Integrity verification of nltk resources.")
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        logger.info(f"Download punkt for nltk.")
        nltk.download('punkt')

    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        logger.info(f"Download punkt_tab for nltk.")
        nltk.download('punkt_tab')

    logger.info(f"Verification completed.")


def sentence_separate(paragraph: str) -> list[str]:
    lang = detect(paragraph)
    if lang == 'zh-cn' or lang == 'zh-tw':
        return zh_cut_sentence(paragraph)
    else:
        return sent_tokenize(paragraph)


def get_entity_mapping_filp(entity_mapping: dict[str, list[str]]) -> dict[str, str]:
    result = {
        alias: name 
        for name, aliases in entity_mapping.items() 
        for alias in aliases
    }
    return result


def gene_id(type: Literal["entity", "relation", "sentence", "paragraph"]) -> str:
    result = f"{type}-{uuid.uuid4().hex[8:]}"
    return result
