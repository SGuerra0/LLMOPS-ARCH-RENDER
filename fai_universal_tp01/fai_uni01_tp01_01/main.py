from dotenv import load_dotenv
from langchain_fireworks import FireworksEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import chromadb
import nltk
import spacy
from src.utilities import *

def main():
    # Cargar variables de entorno
    load_dotenv(".env")

    # Cargar spaCy y aumentar límite máximo
    nlp = spacy.load(os.getenv("SPACY_MODEL"))
    nlp.max_length = 5000000

    # Descargar recursos de NLTK
    nltk.download(os.getenv("NLTK_RESOURCE"))

    # Inicializar cliente ChromaDB
    chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_PATH"))

    # Inicializar Fireworks Embeddings
    embedding_model = FireworksEmbeddings(
        model=os.getenv("FIREWORKS_EMBEDDING_MODEL"),
        api_key=os.getenv("FIREWORKS_API_KEY")
    )

    # Cargar y organizar los documentos en jerarquías
    documents = load_documents()
    document_tree = organize_documents_in_tree(documents)

    # Dividir recursivamente los documentos en chunks
    chunks = split_documents_in_chunks(document_tree)

    # Guardar los chunks y embeddings en ChromaDB
    save_to_chroma(chunks, chroma_client, embedding_model)

    print("Base de datos generada exitosamente con RAPTOR.")
    return 0

if __name__ == "__main__":
    main()