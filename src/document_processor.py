import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def process_uploaded_file(uploaded_file, chunk_size: int = 512) -> FAISS:
    suffix = ".pdf" if uploaded_file.type == "application/pdf" else ".txt"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            loader = PyPDFLoader(tmp_path)
        else:
            loader = TextLoader(tmp_path, encoding="utf-8")

        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=200,        # ← increase overlap significantly
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
            )
        chunks = splitter.split_documents(documents)

        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i

        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        vectorstore = FAISS.from_documents(chunks, embeddings)

    finally:
        os.unlink(tmp_path)

    return vectorstore