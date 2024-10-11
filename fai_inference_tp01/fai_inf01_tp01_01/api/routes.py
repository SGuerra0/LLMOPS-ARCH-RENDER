from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from models.model import RagBot, DefaultBot, update_model, retrieve_docs
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from models.database import get_db, ChatHistory

# Definir API Router
router = APIRouter()

# Modelo de solicitud
class Question(BaseModel):
    question: str
    temperature: float  # Valor de temperatura
    model: str  # Modelo seleccionado
    history: Optional[List[Dict[str, str]]] = None  # Historial de la conversacion actual

@router.post("/get_answer")
async def get_answer(question: Question, db: Session = Depends(get_db)):
    """
    Obtener la respuesta basada en la pregunta usando el modelo RAG.
    """
    if not question.question.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacia.")
    
    # Obtener el historial de la solicitud
    history = question.history or []
    
    # Actualizar el model_wrapper con el modelo y temperatura seleccionados
    model_wrapper = update_model(question.model, question.temperature)
    
    # Inicializar RagBot con el nuevo model_wrapper
    rag_bot = RagBot(model_wrapper, retrieve_docs)
    
    try:
        # Obtener la respuesta del bot, pasando el historial
        response, context = rag_bot.get_answer(question.question, history=history)
        
        # Almacenar solo la pregunta y la respuesta en la base de datos
        chat_entry = ChatHistory(
            question=question.question,
            answer=response
        )
        db.add(chat_entry)
        db.commit()
        
        # Retornar la respuesta y el contexto
        return {"answer": response, "context": context}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar la pregunta: {e}")

@router.post("/get_default_answer")
async def get_default_answer(question: Question):
    """
    Obtener la respuesta basada en la pregunta usando el modelo por defecto (sin contexto).
    """
    if not question.question.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacia.")
    
    # Actualizar el model_wrapper con el modelo y temperatura seleccionados
    model_wrapper = update_model(question.model, question.temperature)
    
    # Inicializar DefaultBot con el nuevo model_wrapper
    default_bot = DefaultBot(model_wrapper)
    
    try:
        response = default_bot.get_answer(question.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la pregunta: {e}")
