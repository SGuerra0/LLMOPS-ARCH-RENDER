from langchain_fireworks import FireworksEmbeddings
import nltk 
import spacy

from src.utilities import *

def main():
    # Cargar variables de entorno
    load_dotenv()
    
    # Cargar el modelo de spaCy para espanol
    nlp = spacy.load(os.getenv("SPACY_MODEL"))

    # Descargar recursos de NLTK
    nltk.download(os.getenv("NLTK_RESOURCE"))

    # Cliente LangSmith
    # Configura tu cliente de ChromaDB
    chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_PATH"))

    embedding_model = FireworksEmbeddings(
        model=os.getenv("FIREWORKS_EMBEDDING_MODEL"),
        api_key=os.getenv("FIREWORKS_API_KEY")
    )

    documents = load_documents()

    chunks = split_text(documents, nlp, max_chunk_size=1000)

    save_to_chroma(chunks, chroma_client, embedding_model)

    return 0


if __name__ == "__main__":
    main()