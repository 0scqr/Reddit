import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno desde .env
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    # Si no están las variables, usamos valores por defecto vacíos para evitar errores al importar
    # pero avisamos al usuario
    print("WARNING: SUPABASE_URL o SUPABASE_KEY no configuradas en el archivo .env")

supabase: Client = create_client(url if url else "", key if key else "")

def get_supabase_client():
    return supabase
