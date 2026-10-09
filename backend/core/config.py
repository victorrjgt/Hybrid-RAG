import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Rutas principales del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_PATH = DATA_DIR / "chroma_db"

# Asegurar que el directorio de datos exista
DATA_DIR.mkdir(parents=True, exist_ok=True)

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

if not GOOGLE_API_KEY:
    print("GOOGLE_API_KEY no está configurada en el archivo .env")

if not TAVILY_API_KEY:
    print("TAVILY_API_KEY no está configurada en el archivo .env")