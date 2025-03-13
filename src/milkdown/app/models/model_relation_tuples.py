from pydantic import BaseModel


class RelationTuples(BaseModel):
    subject: str
    relation: str
    object: str
    sentence: str
    sentence_index: int


class EntityModel(BaseModel):
    id: str
    name: str
    entity_type: str = ""
    alias: list["EntityModel"] = []


class RelationModel(BaseModel):
    id: str
    name: str


class SentenceModel(BaseModel):
    id: str
    paragraph_id: str
    content: str
    index: int


class RelationTuplesModel(BaseModel):
    subject: EntityModel
    relation: RelationModel
    object: EntityModel
    sentence: SentenceModel
    

class ParagraphModel(BaseModel):
    id: str
    content: str
    url: str
