"""Generic document cleaning and conversion utilities.

These helpers strip noisy fields (system IDs, embeddings, empty values) from
JSON documents before they are sent to an LLM, and convert documents to YAML
which is denser and therefore cheaper to tokenize.
"""
import yaml
from pypdf import PdfReader

DEFAULT_FIELDS_TO_REMOVE = [
    "_id", "createdAt", "updatedAt", "author", "authorName", "authorProfile",
    "vector_embedding", "score",
]


def clean_dict(doc: dict, remove_fields: bool = False,
               extra_fields_to_remove: list[str] | None = None,
               keep_fields: list[str] | None = None) -> dict:
    """Recursively drop empty values from a dict.

    When ``remove_fields`` is True the keys listed in
    ``DEFAULT_FIELDS_TO_REMOVE`` (extended with ``extra_fields_to_remove``)
    are stripped from the top level, except for any keys listed in
    ``keep_fields``.
    """
    keep_fields = keep_fields or []

    if remove_fields:
        fields = list(DEFAULT_FIELDS_TO_REMOVE)
        if extra_fields_to_remove:
            fields.extend(extra_fields_to_remove)
        for field in fields:
            if field in keep_fields:
                continue
            doc.pop(field, None)

    def _drop_empty(node):
        if isinstance(node, dict):
            return {k: _drop_empty(v) for k, v in node.items()
                    if v is not None and v != 0 and v != "" and v != []}
        if isinstance(node, list):
            return [_drop_empty(v) for v in node]
        return node

    return _drop_empty(doc)


def json_to_yaml(doc: dict, remove_fields: bool = False) -> str:
    return yaml.dump(clean_dict(doc, remove_fields=remove_fields))


def read_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def find_between(text: str, left: str, right: str) -> str:
    """Return the substring of ``text`` enclosed by ``left`` and ``right``."""
    lstart = text.find(left)
    if lstart == -1:
        raise ValueError("left marker not found")
    lstart += len(left)
    rstart = text.find(right, lstart)
    if rstart == -1:
        raise ValueError("right marker not found")
    return text[lstart:rstart]
