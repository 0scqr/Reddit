import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno desde .env
load_dotenv()

def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    # Depuración básica para ver si las variables existen (sin mostrar su valor real)
    if not url:
        raise ValueError("Error: SUPABASE_URL está vacía o no existe en Vercel")
    if not key:
        raise ValueError("Error: SUPABASE_KEY está vacía o no existe en Vercel")
        
    return create_client(url, key)
