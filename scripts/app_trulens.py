import logging
logging.basicConfig(level=logging.INFO)
logging.info("ultimate test")

import sys
from pathlib import Path

# Ajouter explicitement le dossier racine au PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

import asyncio
import streamlit as st
print("-3")
from trulens.dashboard.streamlit import trulens_trace, trulens_feedback
print("-2)")
from trulens_integration.session import tru
from trulens_integration.feedback.auto_feedback import feedbacks

from orchestrator import run_flow_sync
print("-1")
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


# =========================================
# CONFIG
# =========================================
PDF_PATH = "data/raw/CV_Eric_Wetzel_2026.pdf"
MISTRAL_API_KEY = "4qKlNV4ZM82sMknSJb0lo5tEQzJhZmbo"

st.set_page_config(page_title="Sales RAG Assistant (TruLens)", layout="wide")
st.title("🤖 Sales RAG Assistant avec TruLens")
print("0")

# =========================================
# SESSION STATE
# =========================================
for k, v in {
    "messages": [],
    "phase": "qualification",
    "step": 0,
    "qualification": {}
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

print("1")
enable_trulens = st.sidebar.checkbox("Afficher les traces TruLens", value=True)


# =========================================
# INIT COMPONENTS
# =========================================
print("2")
@st.cache_resource
def init_components():

    reader = PDFReader()
    chunker = RecursiveChunker()
    embedder = HFEmbedding(model_name="all-MiniLM-L6-v2")
    retriever = ChromaRetriever()

    llm = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0.2,
        max_tokens=512,
        mistral_api_key=MISTRAL_API_KEY,
    )
    print("3")
    reform_gen = LLMGenerator(llm, ReformulationPrompt())
    commercial_gen = LLMGenerator(llm, CommercialQualificationPrompt())
    print("4")
    return reader, chunker, embedder, retriever, reform_gen, commercial_gen


reader, chunker, embedder, retriever, reform_gen, commercial_gen = init_components()

print("5")
# =========================================
# BUILD INDEX
# =========================================
@st.cache_resource
def build_index():
    logging.basicConfig(level=logging.INFO)
    # Utilise l'event loop existante
    loop = asyncio.get_event_loop()

    logging.info("Loading PDF...")
    print("Loading PDF...")
    docs = loop.run_until_complete(reader.load(PDF_PATH))
    logging.info("Chunking PDF...")
    print("Chunking PDF...")
    docs = loop.run_until_complete(chunker.chunk(docs))
    logging.info("Indexing documents...")
    print("Indexing documents...")
    loop.run_until_complete(retriever.index(docs, embedder))
    logging.info("Index ready")
    print("Index ready")

    #docs = asyncio.run(reader.load(PDF_PATH))
    #docs = asyncio.run(chunker.chunk(docs))
    #asyncio.run(retriever.index(docs, embedder))


build_index()

print("6")
# =========================================
# CHAT HISTORY
# =========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


if not st.session_state.messages:
    st.session_state.messages.append(
        {"role": "assistant", "content": "Quel est le problème principal que cette personne doit résoudre ?"}
    )


# =========================================
# INPUT
# =========================================
user_input = st.chat_input("Votre réponse...")


# =========================================
# FLOW
# =========================================
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.phase == "qualification":

        keys = ["pain", "tempo", "success"]
        st.session_state.qualification[keys[st.session_state.step]] = user_input
        st.session_state.step += 1

        if st.session_state.step < 3:
            st.session_state.messages.append(
                {"role": "assistant", "content": "Question suivante..."}
            )

        else:
            qualification_text = "\n".join(
                f"{k}: {v}" for k, v in st.session_state.qualification.items()
            )

            answer, record = run_flow_sync(
                generator=reform_gen,
                user_input=qualification_text,
                conversation=[],
                enable_trulens=enable_trulens
            )

            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.phase = "chat"

    else:

        qualification_text = "\n".join(
            f"{k}: {v}" for k, v in st.session_state.qualification.items()
        )

        enriched_question = f"{user_input}\n\nContexte recruteur:\n{qualification_text}"
        context = asyncio.run(retriever.retrieve(enriched_question))

        answer, record = run_flow_sync(
            generator=commercial_gen,
            user_input=enriched_question,
            conversation=context,
            enable_trulens=enable_trulens
        )

        st.session_state.messages.append({"role": "assistant", "content": answer})

    if enable_trulens and record is not None:
        with st.expander("Trace TruLens"):
            trulens_trace(record)

        trulens_feedback(record)


    st.rerun()
