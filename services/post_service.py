from entities.post import Post
from utils.supabase_handler import get_supabase_client

supabase = get_supabase_client()

def create_post(title, content, author):
    data = {"title": title, "content": content, "author": author, "likes": 0}
    response = supabase.table("posts").insert(data).execute()
    if response.data:
        p = response.data[0]
        return Post(p["title"], p["content"], p["author"], p["likes"], p["id"])
    return None

def read_post(id):
    response = supabase.table("posts").select("*").eq("id", id).execute()
    if response.data:
        p = response.data[0]
        return Post(p["title"], p["content"], p["author"], p["likes"], p["id"])
    return None

def read_all_posts():
    response = supabase.table("posts").select("*").execute()
    posts = []
    for p in response.data:
        posts.append(Post(p["title"], p["content"], p["author"], p["likes"], p["id"]))
    return posts

def update_post(id, title=None, content=None, likes=None):
    data = {}
    if title is not None: data["title"] = title
    if content is not None: data["content"] = content
    if likes is not None: data["likes"] = likes
    
    response = supabase.table("posts").update(data).eq("id", id).execute()
    if response.data:
        p = response.data[0]
        return Post(p["title"], p["content"], p["author"], p["likes"], p["id"])
    return None

def delete_post(id):
    response = supabase.table("posts").delete().eq("id", id).execute()
    if response.data:
        return Post(None, None, None, None, id)
    return None

def add_like_to_post(id):
    post = read_post(id)
    if post is None:
        return None
    return update_post(id, likes=post.likes + 1)
