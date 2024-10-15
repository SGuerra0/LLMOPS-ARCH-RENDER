import os
import chromadb
from langchain_fireworks import FireworksEmbeddings, Fireworks
from dotenv import load_dotenv
from typing import Optional, List, Dict
import unicodedata

# Cargar variables de entorno
load_dotenv(".env")

# Obtener el directorio actual (donde se encuentra 'model.py')
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta al directorio raíz del proyecto ('LLMops')
# Retrocediendo tres niveles desde 'model.py'
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))

# Construir la ruta completa a 'chroma.sqlite3' desde la raíz del proyecto
chroma_path = os.getenv(
    "CHROMA_PATH",
    os.path.join(project_root, 'data', 'universal', 'chroma.sqlite3')
)

print(f"Ruta de CHROMA_PATH resuelta: {chroma_path}")

# Verificar si el archivo 'chroma.sqlite3' existe
if os.path.exists(chroma_path):
    print("El archivo 'chroma.sqlite3' existe en la ruta resuelta.")
else:
    print("El archivo 'chroma.sqlite3' NO existe en la ruta resuelta.")

# Inicializar ChromaDB usando la ruta absoluta para la base de datos
try:
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    collection_name = os.getenv("DB_NAME", "default_collection")
    collection = chroma_client.get_collection(name=collection_name)
    print("ChromaDB inicializado correctamente.")
except Exception as e:
    print(f"Error al inicializar ChromaDB: {e}")
    collection = None  # Asegurarse de que 'collection' está definido

# Función para actualizar dinámicamente el modelo del model_wrapper
def update_model(model_name: str, temperature: float) -> Fireworks:
    """
    Actualiza el model_wrapper con el nuevo modelo y temperatura seleccionados.
    """
    return Fireworks(
        model=model_name,
        temperature=temperature,
        max_tokens=400
    )

# Cargar Fireworks Embeddings para la recuperación de documentos
embedding_model = FireworksEmbeddings(
    model=os.getenv("FIREWORKS_EMBEDDING_MODEL")
)

def retrieve_docs(question: str) -> str:
    """
    Recuperar documentos relevantes basados en la pregunta usando embeddings.
    """
    if collection is None:
        print("La colección de ChromaDB no está disponible.")
        return ""

    try:
        query_embedding = embedding_model.embed_query(question)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=8
        )
    except Exception as e:
        print(f"Error al recuperar documentos: {e}")
        return ""

    # Filtrar documentos basados en el umbral de similitud
    threshold = 1.0
    filtered_docs = []
    for doc_list, distance_list in zip(results['documents'], results['distances']):
        for doc, distance in zip(doc_list, distance_list):
            if distance >= threshold:
                filtered_docs.append(doc)

    # Usar todos los documentos si no se filtran por el umbral
    if not filtered_docs:
        filtered_docs = [item for sublist in results['documents'] for item in sublist]

    return "\n\n---\n\n".join(filtered_docs)

def normalize_string(s: str) -> str:
    """
    Normaliza una cadena de texto eliminando tildes y convirtiendo a minúsculas.
    """
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8').lower()

# Clase RAGBot que maneja las inferencias y preguntas
class RagBot:
    def __init__(self, model, retriever):
        self._model = model
        self._retriever = retriever

    def is_new_topic(self, question: str, last_question: str) -> bool:
        """
        Detectar si la nueva pregunta es un cambio de tema respecto a la pregunta anterior.
        """
        return normalize_string(question) != normalize_string(last_question)

    def filter_repeated_info(self, new_answer: str, history: List[Dict[str, str]]) -> str:
        """
        Filtrar información repetida en base al historial de respuestas anteriores.
        """
        for entry in history:
            previous_answer = entry['answer']
            # Eliminar las partes de la nueva respuesta que ya se mencionaron antes
            new_answer = new_answer.replace(previous_answer, "")
        return new_answer.strip()

    def get_answer(self, question: str, history: Optional[List[Dict[str, str]]] = None):
        """
        Obtener la respuesta basada en la pregunta utilizando el modelo generativo.
        """
        # Mantener el historial completo
        history_text = ""
        if history:
            for entry in history:
                history_text += f"Usuario: {entry['question']}\nBot: {entry['answer']}\n"

        # Lista ampliada de preguntas genéricas
        generic_questions = ["dame más información", "quiero saber más", "continúa", "amplía", 
                             "más detalles", "puedes decirme más", "cuéntame más", "dame detalles"]

        # Normalizar la pregunta para la comparación
        normalized_question = normalize_string(question)
        if normalized_question in [normalize_string(q) for q in generic_questions] and history:
            last_question = history[-1]['question']
            # Cambiar el prompt para proporcionar más detalles
            question = f"Proporciona más detalles sobre: {last_question}. Asegúrate de no repetir información y expande en temas relacionados."

        # Detectar si el tema ha cambiado
        if history and self.is_new_topic(question, history[-1]['question']):
            history_text += f"\nNuevo tema detectado. Enfócate en la nueva pregunta: {question}\n"

        # Recuperar los documentos relacionados con la pregunta actualizada
        docs = self._retriever(question)
        if not docs.strip():
            return "No se encontró información relevante.", ""

        # Prompt actualizado para que el historial no sea dominante
        prompt = f"""Eres un asistente de AFP UNO que proporciona información basada en los documentos proporcionados, también debes poder inferir información a partir de estos documentos. Usa el siguiente contexto para responder la pregunta de manera concisa y clara.

Contexto:
{docs}

Pregunta actual: {question}

Historial de la conversación:
{history_text}

Si es relevante, puedes referirte brevemente a interacciones anteriores, pero enfócate en responder la pregunta actual. Proporciona información adicional si es posible, y no repitas información que ya diste anteriormente.

Respuesta:"""

        try:
            result = self._model.generate([prompt])
            generated_text = result.generations[0][0].text.strip()

            # Filtrar información repetida
            if history:
                generated_text = self.filter_repeated_info(generated_text, history)

        except Exception as e:
            print(f"Error generando la respuesta: {e}")
            generated_text = "Error al generar la respuesta."

        return generated_text, docs

# Clase para el bot por defecto (sin contexto de documentos)
class DefaultBot:
    def __init__(self, model):
        self._model = model

    def get_answer(self, question: str):
        """
        Obtener respuesta basada únicamente en la pregunta, sin contexto adicional.
        """
        # Enviar la pregunta directamente al modelo sin prompt adicional
        try:
            result = self._model.generate([question])
            generated_text = result.generations[0][0].text.strip()
        except Exception as e:
            print(f"Error generando la respuesta: {e}")
            generated_text = "Error al generar la respuesta."

        return generated_text
