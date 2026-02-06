import logging
import streamlit as st
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser


# =====================================================
# CONFIG
# =====================================================
MISTRAL_API_KEY = "4qKlNV4ZM82sMknSJb0lo5tEQzJhZmbo"

st.set_page_config(page_title="Sales RAG Assistant", layout="wide")
st.title("🤖 Sales RAG Assistant")

logging.basicConfig(level=logging.INFO)


# =====================================================
# BUILD RAG (cache lourd)
# =====================================================
@st.cache_resource
def build_chain():

    BASE_DIR = Path(__file__).resolve().parent.parent
    PDF_PATH = BASE_DIR / "data" / "raw" / "CV_Eric_Wetzel_2026.pdf"

    loader = PyPDFLoader(str(PDF_PATH))
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    docsearch = Chroma.from_documents(texts, embeddings)

    llm = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0.2,
        max_tokens=512,
        mistral_api_key=MISTRAL_API_KEY
    )

    wrapped_retriever = RunnableLambda(
        lambda x: "\n\n".join(
            [d.page_content for d in docsearch.similarity_search(x["question"], k=3)]
        )
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         """Tu es un assistant commercial spécialisé dans l’analyse de profils.
Tu dois évaluer l’adéquation entre un besoin recruteur et le profil fourni via le contexte.
Réponses courtes, concrètes, orientées décision."""
        ),
        ("placeholder", "{chat_history}"),
        ("system", "Contexte CV: {context}"),
        ("human", "{question}")
    ])

    rag_chain = (
        {"context": wrapped_retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    store = {}

    def get_history(session_id: str):
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

    return RunnableWithMessageHistory(
        rag_chain,
        get_history,
        input_messages_key="question",
        history_messages_key="chat_history",
    )


chat = build_chain()


# =====================================================
# SESSION STATE
# =====================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "step" not in st.session_state:
    st.session_state.step = 0

if "qualification" not in st.session_state:
    st.session_state.qualification = {}

if "phase" not in st.session_state:
    st.session_state.phase = "qualification"


# =====================================================
# QUESTIONS QUALIF
# =====================================================
qualif_questions = [
    "Quel est le problème principal que cette personne doit résoudre ?",
    "À quel horizon souhaitez-vous que la personne soit opérationnelle ?",
    "Dans 6 mois, qu’est-ce qui fera dire que ce recrutement est un succès ?"
]


# =====================================================
# INITIALISATION PREMIER MESSAGE (UNE SEULE FOIS)
# =====================================================
if len(st.session_state.messages) == 0:
    st.session_state.messages.append(
        {"role": "assistant", "content": qualif_questions[0]}
    )


# =====================================================
# AFFICHAGE UNIQUE DES MESSAGES
# =====================================================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])


# =====================================================
# INPUT USER
# =====================================================
user_input = st.chat_input("Votre réponse...")

if user_input:

    # ---------------- USER MESSAGE
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    # ---------------- PHASE QUALIFICATION
    if st.session_state.phase == "qualification":

        keys = ["pain", "tempo", "success"]
        st.session_state.qualification[keys[st.session_state.step]] = user_input

        st.session_state.step += 1

        if st.session_state.step < 3:
            st.session_state.messages.append(
                {"role": "assistant", "content": qualif_questions[st.session_state.step]}
            )

        else:
            # Reformulation
            qualification_text = "\n".join(
                f"{k}: {v}" for k, v in st.session_state.qualification.items()
            )

            reform_prompt = ChatPromptTemplate.from_messages([
                ("system",
                 """Reformule uniquement le besoin en 2 phrases.
Termine par: Ai-je bien compris votre besoin ?"""
                 ),
                ("human", "{qualification}")
            ])

            reform_chain = (
                reform_prompt
                | ChatMistralAI(
                    model="mistral-large-latest",
                    mistral_api_key=MISTRAL_API_KEY
                )
                | StrOutputParser()
            )

            reform = reform_chain.invoke({"qualification": qualification_text})

            st.session_state.messages.append(
                {"role": "assistant", "content": reform}
            )

            st.session_state.phase = "chat"

    # ---------------- PHASE CHAT RAG
    else:

        qualification_text = "\n".join(
            f"{k}: {v}" for k, v in st.session_state.qualification.items()
        )

        answer = chat.invoke(
            {"question": f"{user_input}\n\nContexte recruteur:\n{qualification_text}"},
            config={"configurable": {"session_id": "streamlit"}}
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    st.rerun()
