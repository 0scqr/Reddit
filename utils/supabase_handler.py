import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno desde .env
load_dotenv()

def get_supabase_client():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL o SUPABASE_KEY no configuradas")
        
    return create_client(url, key)
