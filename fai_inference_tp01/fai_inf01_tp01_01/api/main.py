from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as api_router

# FastAPI Application Instance
app = FastAPI(title="Inference Pipeline API", 
              description="Pipeline for AI model inference", 
              version="1.0")

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint raíz para verificar que la API está funcionando
@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}

# Endpoint de estado para verificar la salud del sistema
@app.get("/status")
def status():
    return {"status": "running"}

# Include the API Router
app.include_router(api_router)

# Main Entry Point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
