from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute  # Import necesario para customizar métodos
from .routes import router as api_router

# FastAPI Application Instance
app = FastAPI(
    title="Inference Pipeline API",
    description="Pipeline for AI model inference",
    version="1.0"
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función que permite GET y HEAD para un endpoint
def custom_route_get_and_head():
    return {"message": "API funcionando correctamente"}

# Añadir una ruta que acepte GET y HEAD explícitamente
app.add_api_route("/", custom_route_get_and_head, methods=["GET", "HEAD"])

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
