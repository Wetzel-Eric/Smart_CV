# scripts/orchestrator.py
import asyncio
from components.Reader.PdfReader import PDFReader
from components.Chunker.RecursiveChunker import RecursiveChunker
from components.Embedder.HF_embedder import HFEmbedding
from components.Retriever.Chroma_retriever import ChromaRetriever
from components.Generator.MistralGenerator import LLMGenerator
from components.Prompt_Strategy.commercial_prompt import CommercialQualificationPrompt
from components.Prompt_Strategy.commercial_prompt import ReformulationPrompt
from .qualification import qualify_need
from langchain_mistralai import ChatMistralAI

PDF_PATH = "/home/eric/RAG/RAG_langchain_tuto/data/raw/CV_Eric_Wetzel_2026.pdf"
MISTRAL_API_KEY = "4qKlNV4ZM82sMknSJb0lo5tEQzJhZmbo"

async def orchestrator():
    """
    Orchestrateur complet avec flow métier :
    1. Qualification
    2. Reformulation / confirmation
    3. Sales LLM RAG
    """
    # -----------------------------
    # 1️⃣ Initialisation des composants
    # -----------------------------
    reader = PDFReader()
    chunker = RecursiveChunker()
    embedder = HFEmbedding(model_name="all-MiniLM-L6-v2", batch_size=128)
    retriever = ChromaRetriever()

    llm = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0.2,
        max_tokens=512,
        mistral_api_key=MISTRAL_API_KEY
    )

    reformulation_strategy = ReformulationPrompt()
    commercial_strategy = CommercialQualificationPrompt()
    reformulation_generator = LLMGenerator(llm, prompt_strategy=reformulation_strategy)
    commercial_generator = LLMGenerator(llm, prompt_strategy=commercial_strategy)

    # -----------------------------
    # 2️⃣ Pipeline ingestion PDF → chunks → embeddings → Chroma
    # -----------------------------
    print("Chargement du PDF...")
    documents = await reader.load(PDF_PATH)

    print("Découpage en chunks...")
    documents = await chunker.chunk(documents)

    print("Indexation embeddings dans Chroma...")
    await retriever.index(documents, embedder)
    print("Pipeline ingestion terminée.\n")

    # -----------------------------
    # 3️⃣ Phase de qualification
    # -----------------------------
    qualification_text = qualify_need()
    print("\n--- Qualification recueillie ---\n")
    print(qualification_text)
    print("\n-----------------------------\n")


    # -----------------------------
    # 4️⃣ Reformulation neutre
    # -----------------------------
    # Générer la reformulation avec le LLM déjà configuré (clé incluse)
    try:
        reformulation = await reformulation_generator.generate(question=qualification_text,context=[])
    except Exception as e:
        reformulation = f"[LLM] Erreur reformulation : {e}"

    print("\n--- Reformulation ---\n")
    print(reformulation)
    print("\n-----------------------------\n")

    # Demande confirmation
    confirm = input("Votre besoin est-il correctement reformulé ? (oui/non)\n> ").strip().lower()
    if confirm not in ["oui", "yes"]:
        print("Merci de corriger la reformulation et relancer.")
        return

    print("\nMerci ! Démarrage du chat RAG interactif. Tapez 'exit' pour quitter.\n")


    # -----------------------------
    # 5️⃣ Boucle interactive Sales / RAG
    # -----------------------------
    while True:
        question = input("> ")
        if question.lower() in ("exit", "quit"):
            print("Fin du chat. Au revoir !")
            break

        enriched_question = f"{question}\n\nInfos recruteur:\n{qualification_text}"

        # Récupération contexte RAG
        try:
            context = await retriever.retrieve(enriched_question)
        except Exception as e:
            print(f"[Retriever] Erreur récupération contexte: {e}")
            context = []

        # Génération réponse LLM commerciale
        try:
            answer = await commercial_generator.generate(question=enriched_question,context=context)
        except Exception as e:
            answer = f"[LLM] Erreur génération réponse: {e}"

        print("\nRéponse:\n", answer, "\n")


if __name__ == "__main__":
    asyncio.run(orchestrator())
