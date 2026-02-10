import asyncio
from components.Reader.PdfReader import PDFReader
from components.Chunker.RecursiveChunker import RecursiveChunker
from components.Embedder.HF_embedder import HFEmbedding
from components.Retriever.Chroma_retriever import ChromaRetriever
from components.Generator.MistralGenerator import LLMGenerator
from components.Prompt_Strategy.commercial_prompt import CommercialQualificationPrompt
from .qualification import qualify_need
from langchain_mistralai import ChatMistralAI

PDF_PATH = "/home/eric/RAG/RAG_langchain_tuto/data/raw/CV_Eric_Wetzel_2026.pdf"
MISTRAL_API_KEY = ""

async def main():
    # -----------------------------
    # 1️⃣ Initialisation components
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

    prompt_strategy = CommercialQualificationPrompt()
    generator = LLMGenerator(llm, prompt_strategy=prompt_strategy)

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
    # 3️⃣ Phase qualification CLI
    # -----------------------------
    qualification = qualify_need()
    print("\nChat démarré. Tapez 'exit' pour quitter.\n")

    # -----------------------------
    # 4️⃣ Boucle interactive
    # -----------------------------
    while True:
        question = input("> ")
        if question.lower() in ("exit", "quit"):
            print("Fin du chat. Au revoir !")
            break

        enriched_question = f"{question}\n\nInfos recruteur:\n{qualification}"

        # Récupérer contexte via retriever
        try:
            context = await retriever.retrieve(enriched_question)
        except Exception as e:
            print(f"[Retriever] Erreur récupération contexte: {e}")
            context = []

        # Génération de réponse LLM
        try:
            answer = await generator.generate(enriched_question, context)
        except Exception as e:
            answer = f"[LLM] Erreur génération réponse: {e}"

        print("\nRéponse:\n", answer, "\n")


if __name__ == "__main__":
    asyncio.run(main())
