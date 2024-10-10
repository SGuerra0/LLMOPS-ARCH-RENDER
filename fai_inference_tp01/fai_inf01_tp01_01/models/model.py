import os
import chromadb
from langchain_fireworks import FireworksEmbeddings, Fireworks
from dotenv import load_dotenv

load_dotenv(".env")

# Set up Fireworks Model Wrapper
model_wrapper = Fireworks(
    model=os.getenv("FIREWORKS_WRAPPER_MODEL"),
    temperature=0.6,
    max_tokens=400
)

# Load Fireworks Embeddings for document retrieval
embedding_model = FireworksEmbeddings(
    model=os.getenv("FIREWORKS_EMBEDDING_MODEL")
)

# Configure ChromaDB client for document storage and retrieval
chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_PATH"))
collection = chroma_client.get_collection(os.getenv("DB_NAME"))

def retrieve_docs(question: str) -> str:
    """
    Retrieve relevant documents based on the question using embeddings.
    """
    try:
        query_embedding = embedding_model.embed_query(question)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=8
        )
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return ""

    # Filter documents based on similarity threshold
    threshold = 1.0
    filtered_docs = []
    for doc_list, distance_list in zip(results['documents'], results['distances']):
        for doc, distance in zip(doc_list, distance_list):
            if distance >= threshold:
                filtered_docs.append(doc)

    # Use all documents if no filtered documents meet the threshold
    if not filtered_docs:
        filtered_docs = [item for sublist in results['documents'] for item in sublist]

    return "\n\n---\n\n".join(filtered_docs)

# Define the RAGBot class for handling inference and Q&A
class RagBot:
    def __init__(self, model, retriever):
        self._model = model
        self._retriever = retriever

    def get_answer(self, question: str):
        """
        Get the answer based on the input question using the generative model.
        """
        docs = self._retriever(question)
        if not docs.strip():
            return "No relevant information found.", ""

        prompt = f"""You are an AFP Uno expert. Based on the following information, answer the question concisely and clearly:
        Information:    
        {docs}
        Question: {question}
        Answer:"""

        try:
            result = self._model.generate([prompt])
            generated_text = result.generations[0][0].text.strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            generated_text = "Error generating the response."

        return generated_text, docs
    
# Clase para el bot por defecto (sin contexto de documentos)
class DefaultBot:
    def __init__(self, model):
        self._model = model

    def get_answer(self, question: str):
        """
        Obtener respuesta basada únicamente en la pregunta, sin contexto adicional.
        """
        prompt = f"""You are an AFP Uno expert. Answer the question concisely and clearly:
        Question: {question}
        Answer:"""

        try:
            result = self._model.generate([prompt])
            generated_text = result.generations[0][0].text.strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            generated_text = "Error generating the response."

        return generated_text
