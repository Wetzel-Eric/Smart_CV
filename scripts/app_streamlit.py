# =========================================
# Fix imports when run via Streamlit
# =========================================
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# =========================================
# Imports
# =========================================
import asyncio
import streamlit as st

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

st.set_page_config(page_title="Sales RAG Assistant", layout="wide")
st.title("🤖 Sales RAG Assistant")


# =========================================
# Utils async → sync wrapper
# =========================================
def run_async(coro):
    """Streamlit-safe async runner"""
    return asyncio.run(coro)


# =========================================
# SESSION STATE
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


# =========================================
# QUESTIONS QUALIFICATION
# =========================================
qualif_questions = [
    "Quel est le problème principal que cette personne doit résoudre ?",
    "À quel horizon souhaitez-vous que la personne soit opérationnelle ?",
    "Dans 6 mois, qu’est-ce qui fera dire que ce recrutement est un succès ?",
]


# =========================================
# INIT COMPONENTS (cached)
# =========================================
@st.cache_resource
def init_components():
    reader = PDFReader()
    chunker = RecursiveChunker()
    embedder = HFEmbedding(model_name="all-MiniLM-L6-v2")
    retriever = ChromaRetriever()

    reform_strategy = ReformulationPrompt()
    commercial_strategy = CommercialQualificationPrompt()

    llm = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0.2,
        max_tokens=512,
        mistral_api_key=MISTRAL_API_KEY,
    )

    reform_generator = LLMGenerator(llm, reform_strategy)
    commercial_generator = LLMGenerator(llm, commercial_strategy)

    return reader, chunker, embedder, retriever, reform_generator, commercial_generator


reader, chunker, embedder, retriever, reform_gen, commercial_gen = init_components()


# =========================================
# BUILD RAG INDEX (sync + cached)
# =========================================
@st.cache_resource
def build_index():
    with st.spinner("🔄 Indexation du CV (premier lancement uniquement)…"):
        docs = run_async(reader.load(PDF_PATH))
        docs = run_async(chunker.chunk(docs))
        run_async(retriever.index(docs, embedder))


build_index()


# =========================================
# HISTORIQUE CHAT
# =========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# Message initial
if not st.session_state.messages:
    st.session_state.messages.append(
        {"role": "assistant", "content": qualif_questions[0]}
    )
    st.rerun()


# =========================================
# INPUT UTILISATEUR
# =========================================
user_input = st.chat_input("Votre réponse...")


# =========================================
# STREAMING helper
# =========================================
def stream_generator(generator, question, context):
    async def collect():
        output = ""
        placeholder = st.empty()

        async for token in generator.generate_stream(question, context):
            output += token
            placeholder.write(output)

        return output

    return run_async(collect())


# =========================================
# HANDLE MESSAGE
# =========================================
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # -----------------------------
    # PHASE QUALIFICATION
    # -----------------------------
    if st.session_state.phase == "qualification":
        keys = ["pain", "tempo", "success"]
        st.session_state.qualification[keys[st.session_state.step]] = user_input
        st.session_state.step += 1

        if st.session_state.step < 3:
            st.session_state.messages.append(
                {"role": "assistant", "content": qualif_questions[st.session_state.step]}
            )

        else:
            qualification_text = "\n".join(
                f"{k}: {v}" for k, v in st.session_state.qualification.items()
            )

            answer = stream_generator(reform_gen, qualification_text, [])

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

            st.session_state.phase = "chat"

    # -----------------------------
    # PHASE RAG CHAT
    # -----------------------------
    else:
        qualification_text = "\n".join(
            f"{k}: {v}" for k, v in st.session_state.qualification.items()
        )

        enriched_question = f"{user_input}\n\nContexte recruteur:\n{qualification_text}"

        context = run_async(retriever.retrieve(enriched_question))

        answer = stream_generator(commercial_gen, enriched_question, context)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    st.rerun()
