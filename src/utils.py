from langchain_core.documents import Document
from typing import List


def format_sources(source_docs: List[Document]) -> str:
    if not source_docs:
        return "_No sources found._"

    formatted = []
    for i, doc in enumerate(source_docs, start=1):
        page = doc.metadata.get("page", "N/A")
        chunk_id = doc.metadata.get("chunk_id", "N/A")
        snippet = doc.page_content.strip().replace("\n", " ")
        if len(snippet) > 300:
            snippet = snippet[:300] + "..."

        formatted.append(
            f"**Source {i}** — Page `{page}` | Chunk `{chunk_id}`\n\n> {snippet}"
        )

    return "\n\n---\n\n".join(formatted)