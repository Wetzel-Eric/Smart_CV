import streamlit as st
import asyncio
import time

BOOT_START = time.perf_counter()

def log(step: str):
    now = time.perf_counter()
    print(f"[BOOT] {step:<35} {now - BOOT_START:.2f}s")


log("script start")

from trulens.dashboard.streamlit import trulens_trace, trulens_feedback
from flow.state import RAGState

from orchestrator import SalesPipeline
from qualification import QUESTIONS

from components.Reader.PdfReader import PDFReader
from components.Chunker.RecursiveChunker import RecursiveChunker
from components.Embedder.HF_embedder import HFEmbedding
from components.Retriever.Chroma_retriever import ChromaRetriever
from components.Generator.MistralGenerator import LLMGenerator
from components.Prompt_Strategy.commercial_prompt import (
    CommercialQualificationPrompt,
    ReformulationPrompt,
)

from langchain_mistralai import ChatMistralAI

log("imports finished")


# =========================================
# CONFIG
# =========================================
PDF_PATH = "data/raw/CV_Eric_Wetzel_2026.pdf"
RECOS_PATH = "data/recommandations.json"
MISTRAL_API_KEY = "4qKlNV4ZM82sMknSJb0lo5tEQzJhZmbo"

st.set_page_config(page_title="CV interactif", layout="wide")
st.title("🤖 Find your guy")
enable_trulens = st.checkbox("Afficher les traces TruLens", value=True)

log("page config ready")


# =========================================
# SESSION STATE (UI uniquement)
# =========================================
defaults = {
    "messages": [],
    "phase": "qualification",
    "step": 0,
    "qualification": {},
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

log("session state init")


# =========================================
# INIT ASYNC LOOP (persistante)
# =========================================
if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.loop)

log("event loop ready")


# =========================================
# SIDEBAR
# =========================================
with st.sidebar:
    st.title("Eric Wetzel")
    st.markdown("---")

    st.markdown('<div class="active-item">🤖 Chatbot de matching</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item"><a href="https://github.com/Wetzel-Eric/RAG-curriculum" class="menu-item" target="_blank">📂 GitHub Repo</a></div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item">💡 Recommandations</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item">🚀 Projets</div>', unsafe_allow_html=True)

    st.markdown("---")

log("sidebar rendered")


# =========================================
# INIT COMPONENTS
# =========================================
@st.cache_resource
def init_components():
    t0 = time.perf_counter()

    reader = PDFReader()
    print(f"[BOOT] reader init: {time.perf_counter()-t0:.2f}s")

    t1 = time.perf_counter()
    chunker = RecursiveChunker()
    print(f"[BOOT] chunker init: {time.perf_counter()-t1:.2f}s")

    t2 = time.perf_counter()
    embedder = HFEmbedding("all-MiniLM-L6-v2")
    print(f"[BOOT] embedder init (HF load): {time.perf_counter()-t2:.2f}s")

    t3 = time.perf_counter()
    retriever = ChromaRetriever()
    print(f"[BOOT] retriever init: {time.perf_counter()-t3:.2f}s")

    t4 = time.perf_counter()
    llm = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0.2,
        max_tokens=512,
        mistral_api_key=MISTRAL_API_KEY,
    )
    print(f"[BOOT] mistral client init: {time.perf_counter()-t4:.2f}s")

    t5 = time.perf_counter()
    reform_gen = LLMGenerator(llm, ReformulationPrompt())
    commercial_gen = LLMGenerator(llm, CommercialQualificationPrompt())
    print(f"[BOOT] generators init: {time.perf_counter()-t5:.2f}s")

    print(f"[BOOT] init_components TOTAL: {time.perf_counter()-t0:.2f}s")

    return reader, chunker, embedder, retriever, reform_gen, commercial_gen


reader, chunker, embedder, retriever, reform_gen, commercial_gen = init_components()
log("components ready")


# =========================================
# BUILD INDEX
# =========================================
@st.cache_resource
def build_index():
    loop = st.session_state.loop

    t0 = time.perf_counter()
    docs = loop.run_until_complete(reader.load(PDF_PATH))
    print(f"[BOOT] pdf load: {time.perf_counter()-t0:.2f}s")

    t1 = time.perf_counter()
    docs = loop.run_until_complete(chunker.chunk(docs))
    print(f"[BOOT] chunking: {time.perf_counter()-t1:.2f}s")

    t2 = time.perf_counter()
    loop.run_until_complete(retriever.index(docs, embedder))
    print(f"[BOOT] indexing (embeddings): {time.perf_counter()-t2:.2f}s")

    print(f"[BOOT] build_index TOTAL: {time.perf_counter()-t0:.2f}s")


build_index()
log("index built")


# =========================================
# PIPELINE MÉTIER
# =========================================
pipeline = SalesPipeline(
    reform_gen=reform_gen,
    retriever=retriever,
    commercial_gen=commercial_gen
)

log("pipeline created")

print(f"\n[BOOT] TOTAL STARTUP TIME: {time.perf_counter()-BOOT_START:.2f}s\n")


# =========================================
# RENDER HISTORY
# =========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# =========================================
# FIRST MESSAGE
# =========================================
if not st.session_state.messages:
    _, first_q = QUESTIONS[0]
    st.session_state.messages.append({"role": "assistant", "content": first_q})
    st.rerun()


# =========================================
# INPUT
# =========================================
user_input = st.chat_input("Votre réponse...")

# =========================================
# FLOW UI ONLY
# =========================================
# ⚠️ Partie strictement inchangée (ton code original)
