#!/usr/bin/env python3
import logging
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

# -----------------------------
# Config
# -----------------------------
MISTRAL_API_KEY = "LrUF1SfniLMzv5O8kWuZA73mUxl04ihh"
FILENAME_TEST_PATH = "/home/eric/RAG/RAG_langchain_tuto/data/raw/CV_Eric_Wetzel_2026.pdf"
logging.basicConfig(level=logging.INFO)

# -----------------------------
# Load documents
# -----------------------------
loader = PyPDFLoader(FILENAME_TEST_PATH)
documents = loader.load()
logging.info(f"{len(documents)} pages loaded from PDF")

# -----------------------------
# Chunk documents
# -----------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", "!", "?"]
)
texts = text_splitter.split_documents(documents)
logging.info(f"{len(texts)} chunks created")

# -----------------------------
# Embeddings + vector store
# -----------------------------
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
docsearch = Chroma.from_documents(texts, embeddings)
logging.info(f"{len(texts)} chunks ingested into Chroma")

# -----------------------------
# LLM
# -----------------------------
llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0.2,
    max_tokens=512,
    mistral_api_key=MISTRAL_API_KEY
)

# -----------------------------
# Retriever wrapper pour retourner le texte
# -----------------------------
wrapped_retriever = RunnableLambda(
    lambda x: "\n\n".join([doc.page_content for doc in docsearch.similarity_search(x["question"], k=3)])
)

# -----------------------------
# Prompt pour reformulation neutre
# -----------------------------
reformulation_prompt = ChatPromptTemplate.from_messages([
    ("system", """
Tu es un assistant conversationnel dont le rôle est uniquement de reformuler le besoin du recruteur. 
Ne parle jamais de toi ni de ton expertise.
Formule la reformulation en 2-3 phrases maximum.
Termine toujours par : "Ai-je bien compris votre besoin ?"
"""),
    ("human", "{qualification}")
])

# -----------------------------
# Runnable pour reformulation
# -----------------------------
reformulation_runnable = reformulation_prompt | llm | StrOutputParser()

# -----------------------------
# Prompt commercial / scénarios (après confirmation)
# -----------------------------
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """
Tu es un assistant commercial spécialisé dans l’analyse de profils professionnels. 
Tu évalues si un profil correspond à une demande, selon 4 scénarios :

1) Match parfait et intéressé → Convaincre le recruteur.
2) Match partiel et intéressé → Montrer les points forts et convaincre.
3) Match parfait mais pas intéressé → Confirmer le match, mais orienter et poser des questions sur d’autres opportunités.
4) Pas de match → Expliquer pourquoi le profil ne correspond pas et demander s’il existe d’autres opportunités.

**Règles** :
- Première réponse max 3 phrases.
- Utilise le contexte RAG ({context}) pour étayer tes réponses.
- Pose des questions si nécessaire pour clarifier le besoin.
"""),
    ("placeholder", "{chat_history}"),
    ("system", "Contexte tiré des documents: {context}"),
    ("human", "{question}")
])

# -----------------------------
# RAG chain
# -----------------------------
rag_chain = (
    {
        "context": wrapped_retriever,
        "question": RunnablePassthrough()
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)

# -----------------------------
# Mémoire
# -----------------------------
store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

chat = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history",
)

# -----------------------------
# Phase de qualification (3 questions max)
# -----------------------------
def qualify_need():
    print("Avant de continuer, 3 questions rapides (1–2 phrases suffisent) :\n")
    
    pain = input("1) Quel est le problème principal que cette personne doit résoudre ?\n> ")
    temporalite = input("2) À quel horizon souhaitez-vous que la personne soit opérationnelle ?\n> ")
    criteres_succes = input("3) Dans 6 mois, qu’est-ce qui fera dire que ce recrutement est un succès ? (2–3 éléments max)\n> ")
    
    return f"Pain: {pain}\nTemporalité: {temporalite}\nCritères de succès: {criteres_succes}"

# -----------------------------
# Chat interactif
# -----------------------------
def qa():
    session_id = "cli-session"
    
    # Phase de qualification
    qualification = qualify_need()
    
    # Étape A : reformulation neutre
    reformulation = reformulation_runnable.invoke({"qualification": qualification})
    print("\n--- Reformulation du besoin ---\n")
    print(reformulation)
    print("\n-----------------------------\n")
    
    # Demande confirmation avant de poursuivre
    confirm = input("Votre besoin est-il correctement reformulé ? (oui/non)\n> ").strip().lower()
    if confirm not in ["oui", "yes"]:
        print("Merci de préciser ou corriger la reformulation et relancer le script.")
        return
    
    print("\nMerci ! Le chat interactif démarre. Tapez 'quit', 'exit' ou 'bye' pour quitter.\n")
    
    while True:
        query = input("Votre question ou point à clarifier :\n> ")
        if query.lower() in ["quit", "exit", "bye"]:
            print("Answer: Goodbye!")
            break
        
        # Injecter la qualification comme partie du contexte
        answer = chat.invoke(
            {"question": f"{query}\n\nInformations supplémentaires du recruteur:\n{qualification}"},
            config={"configurable": {"session_id": session_id}}
        )
        print("Answer:", answer)

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    qa()
