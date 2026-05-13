from utils.supabase_handler import get_supabase_client

supabase = get_supabase_client()

class Comment:
    def __init__(self, user, text, post_id, parent_id=None, comment_id=None):
        self.comment_id = comment_id
        self.user = user
        self.text = text
        self.post_id = post_id
        self.parent_id = parent_id
        self.replies = []

    def add_reply(self, comment):
        self.replies.append(comment)

def add_comment(post_id, user, text, parent_id=None):
    data = {
        "post_id": post_id,
        "user": user,
        "text": text,
        "parent_id": parent_id
    }
    response = supabase.table("comments").insert(data).execute()
    if response.data:
        return response.data[0]["id"]
    return None

def get_comments_for_post(post_id):
    response = supabase.table("comments").select("*").eq("post_id", post_id).execute()
    if not response.data:
        return []
    
    comments_data = response.data
    comments_by_id = {}
    root_comments = []

    for c in comments_data:
        comment = Comment(c["user"], c["text"], c["post_id"], c["parent_id"], c["id"])
        comments_by_id[c["id"]] = comment
        if c["parent_id"] is None:
            root_comments.append(comment)
    
    for c_id, comment in comments_by_id.items():
        if comment.parent_id is not None:
            parent_comment = comments_by_id.get(comment.parent_id)
            if parent_comment:
                parent_comment.add_reply(comment)

    return root_comments
