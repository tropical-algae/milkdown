

from milkdown.app.models.model_relation_tuples import ParagraphModel
from milkdown.app.util import gene_id


def save_paragraph_to_bucket(paragraph: str) -> ParagraphModel:
    # TODO Connect Minio and save str as document
    return ParagraphModel(
        id=gene_id("paragraph"),
        content=paragraph,
        url=""
    )


def load_paragraph_from_bucket(id: str) -> ParagraphModel:
    # TODO Connect Minio and save str as document
    return ParagraphModel(
        id=gene_id("paragraph"),
        content="",
        url=""
    )
