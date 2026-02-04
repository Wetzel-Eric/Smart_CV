import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# ---------------- Configuration ---------------- #
MISTRAL_API_KEY = "Rx4fJBvHFXfT7RryHk2IoHcRuvkANTLv"
FILENAME_TEST_PATH = "/home/eric/RAG/RAG_langchain_tuto/data/raw/CV_Eric_Wetzel_2026.pdf"

logging.basicConfig(level=logging.INFO)

# ---------------- Chargement du PDF ---------------- #
loader = PyPDFLoader(FILENAME_TEST_PATH)
documents = loader.load()
logging.info(f"{len(documents)} pages loaded from PDF")

# ---------------- Split avancé ---------------- #
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", "!", "?"]
)
texts = text_splitter.split_documents(documents)
logging.info(f"{len(texts)} chunks created")

# ---------------- Embeddings & VectorStore ---------------- #
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
docsearch = Chroma.from_documents(texts, embeddings)
logging.info(f"{len(texts)} chunks ingested into Chroma")

# ---------------- LLM Mistral ---------------- #
llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0.2,
    max_tokens=512,
    mistral_api_key=MISTRAL_API_KEY
)

# ---------------- Prompt RAG ---------------- #
prompt = ChatPromptTemplate.from_messages([
    ("system", """
        Tu es un assistant commercial spécialisé dans l’analyse de profils professionnels. 
        Ton rôle est d’évaluer si le profil correspond à une demande, et de répondre selon ces 4 scénarios :

        1) **Parfait match et intéressé** : Convaincs le recruteur que le profil correspond parfaitement et persuade-le que c’est une excellente opportunité.
        2) **Match partiel et intéressé** : Montre que certaines compétences ou expériences correspondent, persuade et explique pourquoi le profil reste pertinent.
        3) **Match parfait mais pas intéressé** : Confirme que le profil correspond, mais explique ce que la personne recherche réellement et demande si d’autres opportunités pourraient mieux correspondre.
        4) **Pas de match** : Explique en quelques lignes pourquoi le profil ne correspond pas, résume les points forts du profil et demande si d’autres opportunités pourraient convenir.

        **Règles** :
        - Pour la **première réponse**, sois concis : maximum 3 phrases.
        - Utilise toujours le contexte des documents ({context}) pour soutenir tes réponses.
        - Lis attentivement le chat_history pour conserver le contexte.
        - Si nécessaire, pose des questions pour clarifier le rôle recherché.
        """),
    ("placeholder", "{chat_history}"),
    ("system", "Contexte tiré des documents: {context}"),
    ("human", "{question}")
])

# ---------------- Retriever Runnable ---------------- #
retriever = docsearch.as_retriever(search_kwargs={"k": 3})
wrapped_retriever = RunnableLambda(lambda x: retriever.invoke(x["question"])) # Transforme dict -> string pour le retriever pour HuggingFace

# ---------------- Chaîne RAG ---------------- #
rag_chain = (
    {
        "context": wrapped_retriever,           # récupère automatiquement les chunks pertinents
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

# ---------------- Mémoire ---------------- #
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

# ---------------- Chat interactif ---------------- #
def qa():
    session_id = "cli-session"

    print("Chat interactif démarré. Tape 'quit', 'exit' ou 'bye' pour quitter.\n")
    while True:
        query = input("Question: ")

        if query.lower() in ["quit", "exit", "bye"]:
            print("Answer: Goodbye!")
            break

        answer = chat.invoke(
            {"question": query},
            config={"configurable": {"session_id": session_id}}
        )

        print("Answer:", answer)


# ---------------- Lancement ---------------- #
if __name__ == "__main__":
    qa()
