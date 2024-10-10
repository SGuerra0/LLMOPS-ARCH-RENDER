from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.model import RagBot, model_wrapper, retrieve_docs, DefaultBot

# Define API Router
router = APIRouter()

# Initialize RagBot
rag_bot = RagBot(model_wrapper, retrieve_docs)

DefaultBot = DefaultBot(model_wrapper)

# Request Model for the input
class Question(BaseModel):
    question: str

@router.post("/get_answer")
async def get_answer(question: Question):
    """
    Get the answer for the given question.
    """
    if not question.question.strip():
        raise HTTPException(status_code=400, detail="The question cannot be empty.")
    try:
        response, context = rag_bot.get_answer(question.question)
        return {"answer": response, "context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the question: {e}")

@router.post("/get_default_answer")
async def get_default_answer(question: Question):
    """
    Get the answer for the given question using the default model (without context).
    """
    if not question.question.strip():
        raise HTTPException(status_code=400, detail="The question cannot be empty.")
    try:
        response = DefaultBot.get_answer(question.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the question: {e}")
