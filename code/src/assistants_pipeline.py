"""Four-step OpenAI Assistants pipeline for margin/markup estimation.

The pipeline is intentionally generic. It does not encode any specific
business field names — callers attach their own JSON documents and the
assistant is asked to discover the relevant variables itself.

Steps:
    1. Upload the query document and N similar documents as files.
    2. Ask the assistant for a qualitative analysis of the variables that
       discriminate accepted vs. rejected offers.
    3. Ask the assistant for a structured comparison table.
    4. Ask the assistant for a numeric markup suggestion plus a riskier
       alternative.
    5. Ask the assistant to return ONLY the final number.
"""
import io
import typing

import openai


def _upload(doc: dict, client: openai.OpenAI, name_hint: str = "") -> typing.Any:
    buf = io.BytesIO(bytes(str(doc), "utf8"))
    buf.name = f"{name_hint}{doc.get('_id', 'document')}.json"
    return client.files.create(file=io.BufferedReader(buf), purpose="assistants")


def _chunks(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def _run(thread, assistant_id, client) -> str:
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant_id
    )
    messages = list(client.beta.threads.messages.list(
        thread_id=thread.id, run_id=run.id))
    if not messages:
        return ""
    msg = messages[0].content[0].text
    citations = []
    for idx, ann in enumerate(msg.annotations):
        msg.value = msg.value.replace(ann.text, f"[{idx}]")
        if file_citation := getattr(ann, "file_citation", None):
            cited = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{idx}] {cited.filename}")
    return msg.value + ("\n" + "\n".join(citations) if citations else "")


def run_assistant_pipeline(
    *,
    client: openai.OpenAI,
    assistant_id: str,
    query_document: dict,
    similar_documents: typing.Mapping[str, list[dict]],
    files_per_message: int = 10,
):
    """Yield ``(step, message)`` tuples as the assistant works through the
    pipeline. ``similar_documents`` is a mapping from a free-form bucket
    name (for the caller's bookkeeping) to a list of documents.
    """
    query_file = _upload(query_document, client, name_hint="query_")
    similar_files = []
    for bucket, docs in similar_documents.items():
        for doc in docs:
            similar_files.append(_upload(doc, client))

    thread = client.beta.threads.create(messages=[
        {
            "role": "user",
            "content": (
                "This JSON contains information about a new potential order "
                "from a client. We will prepare a quotation for the client. "
                "Analyse this file to suggest the markup percentage that "
                "should be applied on top of production cost."
            ),
            "attachments": [{"file_id": query_file.id,
                             "tools": [{"type": "file_search"}]}],
        },
        *[{
            "role": "user",
            "content": (
                "These JSON files contain historical biddings that are "
                "similar to the new request. Analyse them to understand "
                "which parameters drive the markup percentage."
            ),
            "attachments": [{"file_id": f.id, "tools": [{"type": "file_search"}]}
                            for f in batch],
        } for batch in _chunks(similar_files, files_per_message)],
        {
            "role": "user",
            "content": (
                "Briefly explain which variables you would use to "
                "differentiate between accepted (confirmed:True) and "
                "declined (confirmed:False) biddings. Output the answer in "
                "HTML."
            ),
        },
    ])

    yield 1, _run(thread, assistant_id, client)

    client.beta.threads.messages.create(thread.id, role="user", content=(
        f"Using only the starting file {query_file.id} and the similar "
        "biddings, list the JSON fields most useful for telling accepted and "
        "declined bids apart. Output a table with one row per similar "
        "bidding."
    ))
    yield 2, _run(thread, assistant_id, client)

    client.beta.threads.messages.create(thread.id, role="user", content=(
        f"Now use the table you generated. Considering prices and historical "
        f"markup percentages, suggest a markup percentage for the starting "
        f"bidding in {query_file.id}. Briefly justify your reasoning, then "
        "also propose a riskier alternative percentage that might still be "
        "accepted but is more likely to be declined."
    ))
    yield 3, _run(thread, assistant_id, client)

    client.beta.threads.messages.create(thread.id, role="user", content=(
        "For your next response, output ONLY the markup percentage from "
        "the previous step. Output only the number without the percent sign."
    ))
    yield 4, _run(thread, assistant_id, client)
