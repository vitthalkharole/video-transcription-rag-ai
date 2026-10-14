
from pathlib import Path

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.core.config import settings



from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from backend.core.config import settings

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = str(BASE_DIR / "vector_db")
COLLECTION_NAME = "video_transcripts_gemini"



EMBEDDING_MODEL = "models/gemini-embedding-001"


def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=settings.GEMINI_API_KEY
    )




def build_vector_store(
    video_id: int,
    transcript: str,
    source_url: str
) -> Chroma:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(transcript)

    documents = [
        Document(
            page_content=chunk,
            metadata={
                "video_id": video_id,
                "source_url": source_url,
                "chunk_index": i
            }
        )
        for i, chunk in enumerate(chunks)
    ]

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR
    )

    if documents:
        vector_store.add_documents(
            documents=documents,
            ids=[
                f"video_{video_id}_chunk_{i}"
                for i in range(len(documents))
            ]
        )

        print("Vectors stored:", vector_store._collection.count())

    return vector_store


def load_vector_store() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR
    )
