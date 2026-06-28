from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from src.document_processor import process_uploaded_file
from src.rag_chain import build_rag_chain, ask_question
from src.utils import format_sources

st.set_page_config(
    page_title="DocChat – Chat with Your Documents",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f0f1a !important;
    border-right: 1px solid #1e1e3a;
}

[data-testid="stSidebar"] * {
    color: #c8c8e0 !important;
}

/* ── Logo / Brand ── */
.brand-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 24px 0;
    border-bottom: 1px solid #1e1e3a;
    margin-bottom: 24px;
}

.brand-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}

.brand-name {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff !important;
    letter-spacing: -0.5px;
}

.brand-tag {
    font-size: 11px;
    color: #6366f1 !important;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── Upload Zone ── */
[data-testid="stFileUploader"] {
    background: #13131f;
    border: 1.5px dashed #2a2a4a;
    border-radius: 14px;
    padding: 8px;
    transition: border-color 0.2s;
}

[data-testid="stFileUploader"]:hover {
    border-color: #6366f1;
}

/* ── Sliders ── */
[data-testid="stSlider"] > div > div > div {
    background: #6366f1 !important;
}

/* ── Hero Section ── */
.hero-section {
    text-align: center;
    padding: 60px 20px 40px;
    max-width: 680px;
    margin: 0 auto;
}

.hero-badge {
    display: inline-block;
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.3);
    color: #818cf8;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 100px;
    margin-bottom: 24px;
}

.hero-title {
    font-size: 52px;
    font-weight: 700;
    letter-spacing: -2px;
    line-height: 1.1;
    color: #ffffff;
    margin-bottom: 16px;
}

.hero-title span {
    background: linear-gradient(135deg, #6366f1, #a78bfa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: 17px;
    color: #6b7280;
    line-height: 1.6;
    margin-bottom: 40px;
}

/* ── Feature Pills ── */
.features-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 48px;
}

.feat-pill {
    background: #13131f;
    border: 1px solid #1e1e3a;
    border-radius: 100px;
    padding: 8px 16px;
    font-size: 13px;
    color: #9ca3af;
    display: flex;
    align-items: center;
    gap: 6px;
}

.feat-pill .icon { font-size: 15px; }

/* ── Doc Ready Banner ── */
.doc-ready-banner {
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1));
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 14px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 24px;
}

.doc-ready-dot {
    width: 10px;
    height: 10px;
    background: #22c55e;
    border-radius: 50%;
    box-shadow: 0 0 8px #22c55e;
    flex-shrink: 0;
}

.doc-ready-text { font-size: 14px; color: #a5b4fc; }
.doc-ready-name { font-weight: 600; color: #ffffff; font-size: 15px; }

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    background: #13131f !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 16px !important;
    margin-bottom: 12px !important;
    padding: 16px !important;
    color: #ffffff !important;
}

[data-testid="stChatMessage"] p {
    color: #e8e8f0 !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
}

[data-testid="stChatMessage"] * {
    color: #e8e8f0 !important;
}
            
/* ── Chat Input ── */
[data-testid="stChatInput"] {
    background: #13131f !important;
    border: 1.5px solid #2a2a4a !important;
    border-radius: 14px !important;
    color: #e8e8f0 !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

/* ── Expander (Sources) ── */
[data-testid="stExpander"] {
    background: #0f0f1a !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 10px !important;
}

/* ── Success / Info ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: #6366f1 !important;
}

/* ── Stats Row ── */
.stats-row {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
}

.stat-card {
    flex: 1;
    background: #13131f;
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    padding: 14px 18px;
    text-align: center;
}

.stat-value {
    font-size: 22px;
    font-weight: 700;
    color: #818cf8;
    font-family: 'JetBrains Mono', monospace;
}

.stat-label {
    font-size: 11px;
    color: #4b5563;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 2px;
}

/* ── Section Label ── */
.section-label {
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #4b5563;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 10px;
    margin-top: 24px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a4a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #6366f1; }

/* ── Clear button ── */
.stButton button {
    background: #13131f !important;
    border: 1px solid #2a2a4a !important;
    color: #9ca3af !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
    transition: all 0.2s !important;
}

.stButton button:hover {
    border-color: #6366f1 !important;
    color: #818cf8 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None
if "doc_name" not in st.session_state:
    st.session_state.doc_name = None
if "msg_count" not in st.session_state:
    st.session_state.msg_count = 0


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-header">
        <div class="brand-icon">🧠</div>
        <div>
            <div class="brand-name">DocChat</div>
            <div class="brand-tag">RAG · Powered</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">📂 Document</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload PDF or TXT",
        type=["pdf", "txt"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="section-label">⚙️ Settings</div>', unsafe_allow_html=True)
    chunk_size = st.slider("Chunk Size", 256, 1024, 1024, step=128,
                           help="Larger = more context per answer")
    top_k = st.slider("Sources to Retrieve", 1, 8, 5,
                      help="How many chunks to search per query")

    st.markdown('<div class="section-label">🗑️ Session</div>', unsafe_allow_html=True)
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.msg_count = 0
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px; color:#4b5563; font-family:'JetBrains Mono',monospace; line-height:1.8;">
    🤖 Groq · Llama 3.1<br>
    🔢 HuggingFace Embeddings<br>
    🗄️ FAISS Vector Store<br>
    ⚡ LangChain LCEL
    </div>
    """, unsafe_allow_html=True)


# ── Main Area ─────────────────────────────────────────────────────────────────
if uploaded_file:
    if st.session_state.doc_name != uploaded_file.name:
        with st.spinner("🔍 Indexing document..."):
            vectorstore = process_uploaded_file(uploaded_file, chunk_size=chunk_size)
            st.session_state.rag_chain = build_rag_chain(vectorstore, top_k=top_k)
            st.session_state.doc_name = uploaded_file.name
            st.session_state.chat_history = []
            st.session_state.msg_count = 0

    # Doc ready banner
    st.markdown(f"""
    <div class="doc-ready-banner">
        <div class="doc-ready-dot"></div>
        <div>
            <div class="doc-ready-name">📄 {uploaded_file.name}</div>
            <div class="doc-ready-text">Document indexed · Ready to answer questions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    questions = st.session_state.msg_count
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-value">{questions}</div>
            <div class="stat-label">Questions Asked</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{top_k}</div>
            <div class="stat-label">Sources / Query</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{chunk_size}</div>
            <div class="stat-label">Chunk Size</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "sources" in msg:
                with st.expander("📎 View Sources"):
                    st.markdown(format_sources(msg["sources"]))

    # Chat input
    if prompt := st.chat_input("Ask anything about your document..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state.msg_count += 1

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching document..."):
                result = ask_question(st.session_state.rag_chain, prompt)
                answer = result["answer"]
                sources = result["source_documents"]

            st.markdown(answer)
            with st.expander("📎 View Sources"):
                st.markdown(format_sources(sources))

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })
        st.rerun()

else:
    # Hero landing screen
    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge">⚡ RAG · Retrieval Augmented Generation</div>
        <div class="hero-title">Chat with any<br><span>document</span></div>
        <div class="hero-sub">
            Upload a PDF or text file. Ask questions in plain English.<br>
            Get precise answers — always cited, never hallucinated.
        </div>
        <div class="features-row">
            <div class="feat-pill"><span class="icon">📄</span> PDF & TXT</div>
            <div class="feat-pill"><span class="icon">🔍</span> Source Citations</div>
            <div class="feat-pill"><span class="icon">⚡</span> Instant Answers</div>
            <div class="feat-pill"><span class="icon">🛡️</span> No Hallucinations</div>
            <div class="feat-pill"><span class="icon">🆓</span> Free to Run</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # How it works
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="stat-card" style="text-align:left; padding:20px;">
            <div style="font-size:28px; margin-bottom:12px;">📤</div>
            <div style="font-size:15px; font-weight:600; color:#fff; margin-bottom:6px;">Upload</div>
            <div style="font-size:13px; color:#6b7280; line-height:1.5;">Drop any PDF or TXT file from the sidebar. The document is split into smart chunks.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-card" style="text-align:left; padding:20px;">
            <div style="font-size:28px; margin-bottom:12px;">🔢</div>
            <div style="font-size:15px; font-weight:600; color:#fff; margin-bottom:6px;">Index</div>
            <div style="font-size:13px; color:#6b7280; line-height:1.5;">Each chunk is embedded into vectors and stored in a FAISS index for lightning-fast retrieval.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-card" style="text-align:left; padding:20px;">
            <div style="font-size:28px; margin-bottom:12px;">💬</div>
            <div style="font-size:15px; font-weight:600; color:#fff; margin-bottom:6px;">Ask</div>
            <div style="font-size:13px; color:#6b7280; line-height:1.5;">Your question retrieves the most relevant chunks. Llama 3.1 answers using only that context.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-top:32px; font-size:13px; color:#4b5563;">
        ← Upload a document from the sidebar to get started
    </div>
    """, unsafe_allow_html=True)