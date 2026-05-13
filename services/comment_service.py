from utils.supabase_handler import get_supabase_client

supabase = get_supabase_client()

def add_comment(post_id, author, content, parent_id=None):
    data = {
        "post_id": post_id,
        "author": author,
        "content": content,
        "parent_id": parent_id
    }
    response = supabase.table("comments").insert(data).execute()
    return response.data

def get_comments_for_post(post_id):
    # Traer todos los comentarios del post ordenados por fecha
    response = supabase.table("comments").select("*").eq("post_id", post_id).order("created_at").execute()
    
    if not response.data:
        return []
    
    all_comments = response.data
    comment_dict = {c["id"]: {**c, "replies": []} for c in all_comments}
    root_comments = []
    
    for c_id, c_data in comment_dict.items():
        p_id = c_data.get("parent_id")
        if p_id and p_id in comment_dict:
            comment_dict[p_id]["replies"].append(c_data)
        else:
            root_comments.append(c_data)
            
    return root_comments
