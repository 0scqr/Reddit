from entities.user import User
from utils.supabase_handler import get_supabase_client

supabase = get_supabase_client()

def create_user(name, password):
    data = {"name": name, "password": password}
    response = supabase.table("users").insert(data).execute()
    if response.data:
        u = response.data[0]
        return User(u["name"], u["password"], u["id"])
    return None

def read_user(id):
    response = supabase.table("users").select("*").eq("id", id).execute()
    if response.data:
        u = response.data[0]
        return User(u["name"], u["password"], u["id"])
    return None

def read_all_users():
    response = supabase.table("users").select("*").execute()
    users = []
    for u in response.data:
        users.append(User(u["name"], u["password"], u["id"]))
    return users

def update_user(name, password, id):
    data = {"name": name, "password": password}
    response = supabase.table("users").update(data).eq("id", id).execute()
    if response.data:
        u = response.data[0]
        return User(u["name"], u["password"], u["id"])
    return None

def delete_user(id):
    response = supabase.table("users").delete().eq("id", id).execute()
    if response.data:
        return User(None, None, id)
    return None
def authenticate_user(name, password):
    response = supabase.table("users").select("*").eq("name", name).eq("password", password).execute()
    if response.data:
        u = response.data[0]
        return User(u["name"], u["password"], u["id"])
    return None
