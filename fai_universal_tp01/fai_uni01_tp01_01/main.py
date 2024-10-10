import os
from dotenv import load_dotenv
from langchain_fireworks import FireworksEmbeddings
import nltk
import spacy

from src.utilities import *

def main():
    # Cargar variables de entorno
    load_dotenv(".env")
    
    # Cargar el modelo de spaCy para español
    nlp = spacy.load(os.getenv("SPACY_MODEL"))

    # Descargar recursos de NLTK
    nltk.download(os.getenv("NLTK_RESOURCE"))

    # Configurar el cliente de ChromaDB
    chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_PATH"))

    # Inicializar el modelo de embeddings
    embedding_model = FireworksEmbeddings(
        model=os.getenv("FIREWORKS_EMBEDDING_MODEL"),
        api_key=os.getenv("FIREWORKS_API_KEY")
    )

    # Cargar documentos
    documents = load_documents()

    # Aplicar normalización preservando entidades a cada documento
    for doc in documents:
        doc.page_content = normalize_text_preserve_entities(doc.page_content)

    # Dividir el texto en chunks
    chunks = split_text(documents, nlp, max_chunk_size=1000)

    # Guardar los chunks en ChromaDB
    save_to_chroma(chunks, chroma_client, embedding_model)
    
    return 0


if __name__ == "__main__":
    main()
