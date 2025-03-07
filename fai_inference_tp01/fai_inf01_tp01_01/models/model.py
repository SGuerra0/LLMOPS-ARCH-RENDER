import os
import chromadb
from langchain_fireworks import FireworksEmbeddings, Fireworks
from dotenv import load_dotenv
from typing import Optional, List, Dict
import unicodedata

load_dotenv(".env")

# Funcion para actualizar dinamicamente el modelo del model_wrapper
def update_model(model_name: str, temperature: float) -> Fireworks:
    """
    Actualiza el model_wrapper con el nuevo modelo y temperatura seleccionados.
    """
    return Fireworks(
        model=model_name,
        temperature=temperature,
        max_tokens=600
    )

# Cargar Fireworks Embeddings para la recuperacion de documentos
embedding_model = FireworksEmbeddings(
    model=os.getenv("FIREWORKS_EMBEDDING_MODEL")
)

# Configurar ChromaDB para almacenamiento y recuperacion de documentos
chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_PATH"))
collection = chroma_client.get_collection(os.getenv("DB_NAME"))

def retrieve_docs(question: str) -> str:
    """
    Recuperar documentos relevantes basados en la pregunta usando embeddings.
    """
    try:
        query_embedding = embedding_model.embed_query(question)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=15
        )
    except Exception as e:
        print(f"Error retrieving documents: {e}")
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
        original_answer = new_answer
        for entry in history:
            previous_answer = entry['answer']
            # Eliminar las partes de la nueva respuesta que ya se mencionaron antes
            new_answer = new_answer.replace(previous_answer, "")
        new_answer = new_answer.strip()
        # Si la nueva respuesta está vacía después de filtrar, proporcionar un mensaje predeterminado
        if not new_answer:
            new_answer = "He proporcionado toda la información disponible sobre este tema."
        return new_answer

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
        last_question = history[-1]['question'] if history else ""

        if (normalized_question in [normalize_string(q) for q in generic_questions]) or \
           (history and normalize_string(question) == normalize_string(last_question)):
            # Cambiar el prompt para proporcionar más detalles
            question = f"Proporciona más detalles sobre: {last_question}. Asegúrate de no repetir información y expande en temas relacionados."

        # Detectar si el tema ha cambiado
        if history and self.is_new_topic(question, last_question):
            history_text += f"\nNuevo tema detectado. Enfócate en la nueva pregunta: {question}\n"

        # Recuperar los documentos relacionados con la pregunta actualizada
        docs = self._retriever(question)
        if not docs.strip():
            return "No se encontró información relevante.", ""

        # Prompt actualizado para que el historial no sea dominante
        prompt = f"""Eres un asistente de AFP UNO que proporciona información basada en los documentos proporcionados, y puedes inferir información a partir de estos documentos. Usa el siguiente contexto para responder la pregunta de manera concisa y clara.

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
        Obtener respuesta basada unicamente en la pregunta, sin contexto adicional.
        """
        # Enviar la pregunta directamente al modelo sin prompt adicional
        try:
            result = self._model.generate([question])
            generated_text = result.generations[0][0].text.strip()
        except Exception as e:
            print(f"Error generando la respuesta: {e}")
            generated_text = "Error al generar la respuesta."

        return generated_text


'''
def dynamic_threshold(distances: List[float], factor: float = 0.8) -> float:
    """
    Calcula un umbral dinámico basado en la distribución de las distancias.
    El factor determina qué tan estricto es el umbral (más cercano al máximo).
    """
    max_distance = max(distances)
    return max_distance * factor

def retrieve_docs(question: str) -> str:
    """Recuperar documentos relevantes usando embeddings."""
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

    # Extraer todas las distancias
    all_distances = [dist for d_list in results['distances'] for dist in d_list]

    # Calcular el umbral dinámico
    threshold = dynamic_threshold(all_distances)

    # Filtrar documentos usando el umbral dinámico
    filtered_docs = [
        doc for doc_list, distance_list in zip(results['documents'], results['distances'])
        for doc, distance in zip(doc_list, distance_list) if distance >= threshold
    ]

    # Si no hay documentos suficientes, utilizar todos los recuperados
    if not filtered_docs:
        filtered_docs = [item for sublist in results['documents'] for item in sublist]

    return "\n\n---\n\n".join(filtered_docs)
'''

'''
Few-shot Prompting

EXAMPLE_PROMPT = """
Usuario: ¿Cuáles son los beneficios del sistema de pensiones?
Bot: Los beneficios incluyen pensiones de vejez, invalidez, sobrevivencia y ahorro voluntario.

Usuario: ¿Qué es una pensión de vejez?
Bot: Es un beneficio al que pueden acceder las personas que han cumplido la edad legal de jubilación, financiado por las cotizaciones que realizaron durante su vida laboral.
"""

def get_prompt(question: str, docs: str, history_text: str) -> str:
    """
    Genera un prompt optimizado con ejemplos y contexto relevante.
    """
    return f"""{EXAMPLE_PROMPT}

Contexto:
{docs}

Pregunta actual: {question}

Historial de la conversación:
{history_text}

Si es relevante, puedes referirte brevemente a interacciones anteriores, 
pero enfócate en responder la pregunta actual. No repitas información que ya diste.

Respuesta:"""
'''