from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.model import RagBot, DefaultBot, update_model, retrieve_docs

# Definir API Router
router = APIRouter()

# Modelo de solicitud
class Question(BaseModel):
    question: str
    temperature: float  # Agregar el valor de temperatura
    model: str  # Agregar el valor del modelo seleccionado

@router.post("/get_answer")
async def get_answer(question: Question):
    """
    Obtener la respuesta basada en la pregunta usando el modelo RAG.
    """
    if not question.question.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")
    
    # Actualizar el model_wrapper con el modelo y temperatura seleccionados
    model_wrapper = update_model(question.model, question.temperature)
    
    # Inicializar RagBot con el nuevo model_wrapper
    rag_bot = RagBot(model_wrapper, retrieve_docs)
    
    try:
        response, context = rag_bot.get_answer(question.question)
        return {"answer": response, "context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la pregunta: {e}")

@router.post("/get_default_answer")
async def get_default_answer(question: Question):
    """
    Obtener la respuesta basada en la pregunta usando el modelo por defecto (sin contexto).
    """
    if not question.question.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")
    
    # Actualizar el model_wrapper con el modelo y temperatura seleccionados
    model_wrapper = update_model(question.model, question.temperature)
    
    # Inicializar DefaultBot con el nuevo model_wrapper
    default_bot = DefaultBot(model_wrapper)
    
    try:
        response = default_bot.get_answer(question.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la pregunta: {e}")
