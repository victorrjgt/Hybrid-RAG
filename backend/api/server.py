import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

# Importamos nuestra lógica
from backend.core.config import DATA_DIR
from backend.services.pdf_loader import procesar_y_guardar_pdf
from backend.services.rag_chain import responder_pregunta

app = FastAPI(
    title="API de RAG Híbrido",
    description="API para procesar PDFs y chatear con ellos usando Corrective RAG",
    version="1.0.0"
)

# DEFINICIÓN DE CONTRATOS DE DATOS
class QueryRequest(BaseModel):
    pregunta: str
    permitir_busqueda_web: bool = True

class QueryResponse(BaseModel):
    respuesta: str
    fuente: str

# ENDPOINTS

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Recibe un archivo PDF, lo guarda temporalmente y lo procesa
    para indexarlo en la base de datos vectorial ChromaDB.
    """
    # VALIDACIÓN DE SEGURIDAD
    if not file.filename:
        raise HTTPException(status_code=400, detail="El archivo subido no tiene nombre.")
        
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")
        
    # Crear carpeta temporal si no existe
    temp_dir = DATA_DIR / "temp_uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = temp_dir / file.filename
    
    try:
        # Guardamos el archivo en disco
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Llamamos a nuestro servicio para triturarlo y guardarlo en Chroma
        num_fragmentos = procesar_y_guardar_pdf(str(file_path))
        
        return {
            "mensaje": f"PDF '{file.filename}' procesado con éxito",
            "fragmentos_creados": num_fragmentos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Limpieza: borramos el PDF temporal después de procesarlo
        if file_path.exists():
            os.remove(file_path)


@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """
    Recibe una pregunta, busca en la base de datos vectorial y, si no lo encuentra
    y el usuario lo permite, hace fallback a internet (Tavily).
    """
    try:
        resultado = responder_pregunta(
            pregunta=request.pregunta,
            permitir_busqueda_web=request.permitir_busqueda_web
        )
        return QueryResponse(
            respuesta=resultado["respuesta"],
            fuente=resultado["fuente"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))