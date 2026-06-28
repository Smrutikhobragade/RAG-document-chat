from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


PROMPT_TEMPLATE = """
You are an expert assistant that answers questions using the document context below.

Instructions:
- Search thoroughly through ALL the context provided.
- If the answer is partially in the context, give what you can find.
- Only say "I couldn't find this" if there is truly ZERO relevant information.
- Be detailed and thorough in your answers.
- Use bullet points for multi-part answers.

Context:
{context}

Question: {question}

Answer:
"""


def build_rag_chain(vectorstore: FAISS, top_k: int = 3):
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
    )

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )

    retriever = vectorstore.as_retriever(
        search_type="mmr",           # ← change from "similarity" to "mmr"
        search_kwargs={
            "k": 6,
            "fetch_k": 12,           # ← fetch more, then pick best diverse ones
            "lambda_mult": 0.7
            }
            )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return {"chain": chain, "retriever": retriever}


def ask_question(chain_dict: dict, question: str) -> dict:
    chain = chain_dict["chain"]
    retriever = chain_dict["retriever"]

    answer = chain.invoke(question)
    source_docs = retriever.invoke(question)

    return {
        "answer": answer,
        "source_documents": source_docs
    }