import asyncio
from itertools import chain
from milkdown.app.models.model_relation_tuples import ParagraphModel, EntityModel, RelationModel, RelationTuples, RelationTuplesModel, SentenceModel
from milkdown.app.services.extract_task.llm_registrar import llm_registrar
from milkdown.app.util import gene_id, get_entity_mapping_filp, sentence_separate
from milkdown.common.util import save_json
from milkdown.service.llm.base import OpenAIBase
from milkdown.service.minio.base import save_paragraph_to_bucket
from milkdown.common.logging import logger


def paragraph_relation_align_and_package(
    relations: list[RelationTuples],
    entity_mapping: dict[str, list[str]],
    paragraph_model: ParagraphModel
) -> tuple[list[RelationTuplesModel], dict[str, EntityModel]]:
    """合并对齐结果，（对齐实体作为别名，同时赋与id并封装

    Args:
        relations (list[RelationTuples]): _description_
        entity_mapping (dict[str, list[str]]): _description_
    """
    relation_tuples_models: list[RelationTuplesModel] = []
    entity_models: dict[str, EntityModel] = {}
    
    alias_mapping: dict[str, str] = get_entity_mapping_filp(entity_mapping)
    
    def generate_entitiy(entity_name: str):
        # 默认假设传入的的都是别名
        subject_alias = entity_name
        subject_alias_model = entity_models.get(
            subject_alias,
            EntityModel(
                id=gene_id("entity"),
                name=subject_alias
            )
        )
        entity_models[subject_alias] = subject_alias_model
        # 如果存在原名，则提取并作为对象
        subject_name = alias_mapping.get(subject_alias, subject_alias)
        if subject_name != subject_alias:
            subject_model = entity_models.get(
                subject_name, 
                EntityModel(
                    id=gene_id("entity"),
                    name=subject_name
                )
            )
            # 将别名加入原名的列表中
            subject_model.alias.append(subject_alias_model)
            entity_models[subject_name] = subject_model
            return subject_model
        return subject_alias_model
    
    for relation in relations:
        subject = generate_entitiy(relation.subject)
        rela = RelationModel(id=gene_id("relation"), name=relation.relation)
        object = generate_entitiy(relation.object)
        sentence = SentenceModel(
            id=gene_id("sentence"), 
            paragraph_id=paragraph_model.id,
            content=relation.sentence,
            index=relation.sentence_index
        )
        
        relation_tuples_models.append(
            RelationTuplesModel(
                subject=subject,
                relation=rela,
                object=object,
                sentence=sentence
            )
        )
    
    return relation_tuples_models, entity_models


async def extract_sentence_relation_tuple(
    sentence: str, 
    sentence_index: int,
    relation_types: list[str],
    extra_entity_model: OpenAIBase, 
    extra_relation_model: OpenAIBase
) -> list[RelationTuples]:
    
    entities: list[str] = await extra_entity_model.run(
        sentence=sentence
    )
    relations: list[RelationTuples] = await extra_relation_model.run(
        sentence=sentence,
        entities=entities,
        relation_types=relation_types,
    )

    for r in relations:
        r.sentence = sentence
        r.sentence_index = sentence_index
    
    return relations


def collect_entities(relations: list[RelationTuples]) -> list[str]:
    result: set = set()
    for relation in relations:
        result.add(relation.subject)
        result.add(relation.object)

    return list(result)


async def extract_paragraph_relation_tuple(paragraph: str, relation_types: list[str] | None = None):
    extra_relation_model = llm_registrar.get("knowledge_relation_exrtactor")
    extra_entity_model = llm_registrar.get("entity_extractor")
    # alig_entity_model = llm_registrar.get("entity_aligner")

    sentences: list[str] = sentence_separate(paragraph)
    extra_relation_tasks = [
        extract_sentence_relation_tuple(
            sentence=sentence, 
            sentence_index=index, 
            relation_types=relation_types,
            extra_entity_model=extra_entity_model, 
            extra_relation_model=extra_relation_model
        )
        for index, sentence in enumerate(sentences)
    ]
    extra_relation_results: list[list] = await asyncio.gather(*extra_relation_tasks)
    relations: list[RelationTuples] = list(chain.from_iterable(extra_relation_results))
    entities: list[str] = collect_entities(relations=relations)
    # results = [self._clean_dirty_data(result) for result in results]

    # logger.info(f"Capture relations: {outptus}")
    #  [RelationTuples.model_validate(result) for result in results]
    # # 提取全部关系三元组与实体
    # relations: list[RelationTuples] = await extra_relation_model.run(paragraph=paragraph)
    # entities: list[str] = list(chain.from_iterable(
    #     [relation.subject, relation.object] 
    #     for relation in relations
    # ))

    # # 提取实体对齐的映射
    # entity_mapping: dict[str, list[str]] = await alig_entity_model.run(
    #     paragraph=paragraph, 
    #     entities=entities
    # )
    
    # # 将文本存入minio
    # paragraph_model = save_paragraph_to_bucket(paragraph=paragraph)
    
    # # 实体对齐，整合比封装关系
    # relation_models, entity_models = paragraph_relation_align_and_package(
    #     relations=relations,
    #     entity_mapping=entity_mapping,
    #     paragraph_model=paragraph_model
    # )
    
    return relations

    # save_json()
    
    # 存储到数据库
    
    # 存储到neo4j

# text = "Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24\u201310 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the \"golden anniversary\" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as \"Super Bowl L\"), so that the logo could prominently feature the Arabic numerals 50."0
text = "爱德华·尼科·埃尔南迪斯（1986-），是一位身高只有70公分哥伦比亚男子，体重10公斤，只比随身行李高一些，2010年获吉尼斯世界纪录正式认证，成为全球当今最矮的成年男人"
# asyncio.run(
#     extract_paragraph_relation_tuple(text)
# )