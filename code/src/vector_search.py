"""Generic MongoDB Atlas vector search helper.

The shape of the documents is intentionally not assumed here — callers pass
in their own ``filter_dict`` so this module stays domain-agnostic.
"""
from pymongo.collection import Collection

from .openai_helpers import get_embedding
from .document_utils import json_to_yaml


def vector_search(
    *,
    query_document: dict,
    collection: Collection,
    openai_client,
    vector_index: str,
    embedding_field: str,
    filter_dict: dict,
    num_results: int,
    candidate_multiplier: int = 10,
):
    """Run an Atlas ``$vectorSearch`` over ``collection``.

    The query document is serialised to YAML, embedded with OpenAI, and the
    resulting vector is matched against ``embedding_field`` under the index
    ``vector_index``. A ``score`` field is added to each result.
    """
    embedding, _tokens = get_embedding(json_to_yaml(query_document),
                                       openai_client)

    pipeline = [
        {"$vectorSearch": {
            "index": vector_index,
            "filter": filter_dict,
            "path": embedding_field,
            "queryVector": embedding,
            "numCandidates": num_results * candidate_multiplier,
            "limit": num_results,
        }},
        {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
    ]
    return collection.aggregate(pipeline=pipeline)


def metadata_search(
    *,
    collection: Collection,
    filter_dict: dict,
    unset_fields: list[str] | None = None,
):
    """Plain ``$match`` lookup with optional ``$unset`` of bulky fields.

    Used to retrieve neighbours by structured attributes (numeric ranges,
    categorical equality, etc.) when an embedding match is not desired.
    """
    pipeline: list[dict] = [{"$match": filter_dict}]
    if unset_fields:
        pipeline.append({"$unset": unset_fields})
    return collection.aggregate(pipeline)
