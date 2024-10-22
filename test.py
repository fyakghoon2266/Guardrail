# Create a vector store with a sample text
from langchain_core.vectorstores import VectorStore

from langchain_openai import AzureOpenAIEmbeddings

embeddings = AzureOpenAIEmbeddings(
                azure_endpoint='http://114.32.211.59:8000',
                azure_deployment='dataeco-text-embedding-ada-002-1',
                api_version='2024-02-01',
                api_key='Bearer example_token',
                dimensions=None,
                chunk_size = 1
            )

text = "可以跟我說說看國泰世華銀行嗎?"

text2 = "LangGraph is a library for building stateful, multi-actor applications with LLMs"


# single_vector = embeddings.embed_query(text)

# embeddings.embed_documents([text, text2])

print(embeddings.embed_query(text))