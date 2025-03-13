import asyncio
from itertools import chain
from milkdown.app.models.model_relation_tuples import ParagraphModel, EntityModel, RelationModel, RelationTuples, RelationTuplesModel, SentenceModel
from milkdown.app.services.extract_task.llm_registrar import llm_registrar
from milkdown.app.util import gene_id, get_entity_mapping_filp
from milkdown.common.util import save_json
from milkdown.service.minio.base import save_paragraph_to_bucket


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
    entity_models: dict[str, EntityModel] = []
    
    alias_mapping: dict[str, str] = get_entity_mapping_filp(entity_mapping)
    
    def generate_entitiy(entity_name: str):
        # 默认原始数据中的都是别名
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
        return subject_alias_model, entity_models
    
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
    
    return relation_tuples_models


async def extract_relation_and_save(paragraph: str):
    capt_model = llm_registrar.get("knowledge_relation_exrtactor")
    alig_model = llm_registrar.get("entity_aligner")

    # 提取全部关系三元组与实体
    relations: list[RelationTuples] = await capt_model.run(paragraph=paragraph)
    entities: list[str] = list(chain.from_iterable(
        [relation.subject, relation.object] 
        for relation in relations
    ))

    # 提取实体对齐的映射
    entity_mapping: dict[str, list[str]] = await alig_model.run(
        paragraph=paragraph, 
        entities=entities
    )
    
    # 将文本存入minio
    paragraph_model = save_paragraph_to_bucket(paragraph=paragraph)
    
    # 实体对齐，整合比封装关系
    relation_models, entity_models = paragraph_relation_align_and_package(
        relations=relations,
        entity_mapping=entity_mapping,
        paragraph_model=paragraph_model
    )
    # pass
    # save_json()
    
    # 存储到数据库
    
    # 存储到neo4j

# text = "Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24\u201310 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the \"golden anniversary\" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as \"Super Bowl L\"), so that the logo could prominently feature the Arabic numerals 50."0
text = "超级碗50是一场美式橄榄球比赛，旨在确定2015赛季美国国家橄榄球联盟（NFL）的冠军。美国橄榄球联盟（AFC）冠军丹佛野马队于201310年24日击败美国国家橄榄球联盟（NFC）冠军卡罗莱纳黑豹队，赢得了他们的第三个超级碗冠军。比赛于2016年2月7日在加利福尼亚州圣克拉拉旧金山湾区的李维斯体育场举行。由于这是第50届超级碗，联盟通过各种以黄金为主题的举措强调了“黄金纪念日”，并暂时中止了用罗马数字命名每场超级碗比赛的传统（根据罗马数字，比赛将被称为“超级碗L”），这样标志就可以突出地显示阿拉伯数字50。"
asyncio.run(
    extract_relation_and_save(text)
)