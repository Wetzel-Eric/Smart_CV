from dependency_injector import containers, providers
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

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Dépendances (votre configuration est déjà correcte)
    reader = providers.Singleton(PDFReader)
    chunker = providers.Singleton(
        RecursiveChunker,
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap
    )
    embedder = providers.Singleton(
        HFEmbedding,
        model_name=config.embedder_model
    )
    retriever = providers.Singleton(
        ChromaRetriever,
        persist_directory="data/chroma_index"
    )

    # LLM Mistral
    llm = providers.Singleton(
        ChatMistralAI,
        model=config.llm_model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        mistral_api_key=config.mistral_api_key
    )

    # Prompt Strategies
    reformulation_prompt = providers.Singleton(ReformulationPrompt)
    commercial_prompt = providers.Singleton(CommercialQualificationPrompt)

    # Générateurs
    reform_gen = providers.Singleton(
        LLMGenerator,
        llm=llm,
        prompt_strategy=reformulation_prompt
    )
    commercial_gen = providers.Singleton(
        LLMGenerator,
        llm=llm,
        prompt_strategy=commercial_prompt
    )
