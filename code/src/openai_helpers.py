"""Thin OpenAI wrappers used by the price-quotation pipeline."""
import openai
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-large"


def load_openai_client(api_key: str) -> OpenAI:
    if not api_key:
        raise ValueError("OPENAI_KEY is missing — set it in your .env file")
    return OpenAI(api_key=api_key)


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_embedding(text: str, client: openai.OpenAI,
                  model: str = DEFAULT_EMBEDDING_MODEL):
    """Return (embedding_vector, total_tokens) for the given text."""
    response = client.embeddings.create(input=str(text), model=model)
    return response.data[0].embedding, response.usage.total_tokens
