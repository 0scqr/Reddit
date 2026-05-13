from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
import os
import sys
import traceback
from utils.supabase_handler import get_supabase_client

# Añadir el directorio raíz al path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from services import post_service, user_service, comment_service

app = Flask(__name__)
app.secret_key = "reddit_secret_key"

def layout(content, show_back=False):
    back_btn = '<a href="/" style="color:var(--reddit-blue); text-decoration:none; font-size:14px; margin: 10px 15px; display:inline-block; font-weight:bold;">← Volver al inicio</a>' if show_back else ''
    nav = f"""
    <div class="navbar">
        <div style="display:flex; align-items:center;">
            <div style="background:linear-gradient(45deg, #FF4500, #FF5700); width:32px; height:32px; border-radius:50%; margin-right:10px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">R</div>
            <a href="/" style="color: white; text-decoration: none; font-weight: 700; font-size: 18px; letter-spacing: -0.5px;">Reddit Clone</a>
        </div>
        <div style="display:flex; align-items:center;">
            {"<span style='margin-right:10px; font-size:12px; color:#818384;'>u/" + session['username'] + "</span> <a href='/logout' class='btn' style='background:#343536; padding: 5px 12px; font-size:12px;'>Salir</a>" if 'username' in session else "<a href='/login' class='btn' style='padding: 5px 12px; font-size:12px;'>Login</a>"}
        </div>
    </div>
    """
    style = """
    <style>
        :root { --reddit-bg: #030303; --reddit-post-bg: #1A1A1B; --reddit-border: #343536; --reddit-text: #D7DADC; --reddit-orange: #FF4500; --reddit-blue: #0079D3; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: var(--reddit-bg); color: var(--reddit-text); margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        .navbar { background-color: var(--reddit-post-bg); padding: 8px 15px; border-bottom: 1px solid var(--reddit-border); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 1000; height: 48px; box-sizing: border-box; }
        .container { max-width: 800px; margin: 0 auto; padding: 0; box-sizing: border-box; }
        .post-card { background-color: var(--reddit-post-bg); border-bottom: 1px solid var(--reddit-border); display: flex; overflow: hidden; margin-bottom: 8px; }
        .vote-sidebar { background: transparent; padding: 12px 8px; display: flex; flex-direction: column; align-items: center; min-width: 45px; }
        .post-main { padding: 12px 12px 12px 0; flex-grow: 1; }
        .post-title { font-size: 17px; font-weight: 600; color: #FFFFFF; text-decoration: none; display: block; margin-bottom: 6px; line-height: 1.3; }
        .post-meta { font-size: 11px; color: #818384; margin-bottom: 4px; }
        .comment { border-left: 1.5px solid var(--reddit-border); margin-left: 10px; padding-left: 12px; margin-top: 16px; }
        .input-box { width: 100%; background: #272729; border: 1px solid var(--reddit-border); border-radius: 20px; padding: 10px 15px; color: white; margin-bottom: 10px; box-sizing: border-box; font-size: 14px; outline: none; }
        .btn { background-color: var(--reddit-blue); color: white; border: none; border-radius: 999px; padding: 8px 16px; font-weight: 700; cursor: pointer; text-decoration: none; display: inline-block; transition: opacity 0.2s; }
        .btn:active { opacity: 0.7; }
        .vote-btn { background: none; border: none; color: #818384; cursor: pointer; font-size: 22px; padding: 4px; border-radius: 4px; }
        .vote-btn.active { color: var(--reddit-orange); }
        
        /* Mobile specific adjustments */
        @media (max-width: 600px) {
            .post-card { border-bottom: 8px solid #000; } /* Spacing between cards */
            .post-title { font-size: 16px; }
            .container { padding-bottom: 50px; }
        }
    </style>
    """
    js = """
    <script>
    async function toggleLike(postId, btn) {
        try {
            const response = await fetch('/like/' + postId, { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                btn.classList.toggle('active');
                btn.nextElementSibling.innerText = data.likes;
            } else if (response.status === 401) {
                window.location.href = '/login';
            }
        } catch(e) { console.error(e); }
    }
    </script>
    """
    return f"<!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'>{style}{js}</head><body>{nav}<div class='container'>{back_btn}{content}</div></body></html>"

@app.route('/')
def home():
    try:
        posts = post_service.read_all_posts()
        posts.sort(key=lambda x: x.likes, reverse=True)
        user_likes = []
        if 'username' in session:
            supabase = get_supabase_client()
            res = supabase.table("post_likes").select("post_id").eq("username", session['username']).execute()
            user_likes = [item['post_id'] for item in res.data]

        content = ""
        for p in posts:
            is_active = "active" if p.id in user_likes else ""
            content += f'''
            <div class="post-card">
                <div class="vote-sidebar">
                    <button class="vote-btn {is_active}" onclick="toggleLike('{p.id}', this)">▲</button>
                    <div style="font-weight:700; font-size:12px; margin:2px 0;">{p.likes}</div>
                </div>
                <div class="post-main">
                    <div class="post-meta">u/{p.author} • r/comunidad</div>
                    <a href="/post/{p.id}" class="post-title">{p.title}</a>
                    <div style="font-size:12px; color:#818384; display:flex; align-items:center;">
                        <span style="margin-right:15px;">💬 Comentar</span>
                    </div>
                </div>
            </div>'''
        return layout(content)
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route('/post/<post_id>')
def post_detail(post_id):
    try:
        post = post_service.read_post(post_id)
        comments = comment_service.get_comments_for_post(post_id)
        user_liked = False
        if 'username' in session:
            supabase = get_supabase_client()
            res = supabase.table("post_likes").select("*").eq("post_id", post_id).eq("username", session['username']).execute()
            user_liked = len(res.data) > 0
        
        is_active = "active" if user_liked else ""

        def render_tree(nodes):
            html = ""
            for c in nodes:
                html += f'<div class="comment">'
                html += f'<div style="font-size: 11px; color: #818384; font-weight:700;">u/{c["author"]}</div>'
                html += f'<div style="font-size:14px; margin:4px 0; line-height:1.4;">{c["content"]}</div>'
                if 'username' in session:
                    html += f'<button onclick="this.nextElementSibling.style.display=\'block\'" style="background:none; border:none; color:#818384; cursor:pointer; font-size:11px; font-weight:700; padding:4px 0;">Responder</button>'
                    html += f'<div style="display:none; margin-top:8px;">'
                    html += f'<form action="/reply/{post_id}/{c["id"]}" method="post"><input name="content" class="input-box" placeholder="Tu respuesta..." required><button class="btn" style="padding: 4px 12px; font-size:12px;">Enviar</button></form></div>'
                if c.get("replies"):
                    html += render_tree(c["replies"])
                html += '</div>'
            return html

        form = f'<form action="/comment/{post_id}" method="post"><input name="content" class="input-box" placeholder="Añadir un comentario..." required><button class="btn" style="width:100%; margin-top:5px;">Publicar</button></form>' if 'username' in session else '<p style="text-align:center; font-size:13px; color:#818384;"><a href="/login" style="color:var(--reddit-blue);">Inicia sesión</a> para comentar</p>'
        
        content = f'''
        <div class="post-card" style="border-bottom:none;">
            <div class="vote-sidebar">
                <button class="vote-btn {is_active}" onclick="toggleLike('{post.id}', this)">▲</button>
                <div style="font-weight:700; font-size:12px; margin:2px 0;">{post.likes}</div>
            </div>
            <div class="post-main">
                <div class="post-meta">u/{post.author}</div>
                <h1 style="font-size:19px; margin:5px 0 10px 0; line-height:1.3;">{post.title}</h1>
                <p style="font-size:15px; line-height:1.5; margin:0;">{post.content}</p>
            </div>
        </div>
        <div style="padding:15px; background:var(--reddit-post-bg); border-top: 1px solid var(--reddit-border);">
            {form}
            <div id="comments-list" style="margin-top:20px;">{render_tree(comments)}</div>
        </div>
        '''
        return layout(content, show_back=True)
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route('/like/<post_id>', methods=['POST'])
def like_post(post_id):
    if 'username' not in session: return jsonify({"error": "unauthorized"}), 401
    supabase = get_supabase_client()
    username = session['username']
    check = supabase.table("post_likes").select("*").eq("post_id", post_id).eq("username", username).execute()
    if check.data:
        supabase.table("post_likes").delete().eq("post_id", post_id).eq("username", username).execute()
        post = post_service.read_post(post_id)
        new_likes = max(0, post.likes - 1)
        post_service.update_post(post_id, likes=new_likes)
    else:
        supabase.table("post_likes").insert({"post_id": post_id, "username": username}).execute()
        post = post_service.add_like_to_post(post_id)
        new_likes = post.likes
    return jsonify({"likes": new_likes})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = user_service.authenticate_user(request.form['username'], request.form['password'])
        if user:
            session['username'] = user.name
            return redirect('/')
        return "Error: Credenciales inválidas", 401
    return layout('<div style="padding:20px;"><h2>Inicia sesión</h2><form method="post"><input name="username" placeholder="Nombre de usuario" class="input-box" required><input name="password" type="password" placeholder="Contraseña" class="input-box" required><button class="btn" style="width:100%;">Entrar</button></form></div>', show_back=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_service.create_user(request.form['username'], request.form['password'])
        return redirect('/login')
    return layout('<div style="padding:20px;"><h2>Crea tu cuenta</h2><form method="post"><input name="username" placeholder="Elige un nombre" class="input-box" required><input name="password" type="password" placeholder="Crea una contraseña" class="input-box" required><button class="btn" style="background: var(--reddit-orange); width:100%;">Registrarme</button></form></div>', show_back=True)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/comment/<post_id>', methods=['POST'])
def add_comment(post_id):
    if 'username' in session:
        comment_service.add_comment(post_id, session['username'], request.form['content'])
    return redirect(f'/post/{post_id}')

@app.route('/reply/<post_id>/<comment_id>', methods=['POST'])
def add_reply(post_id, comment_id):
    if 'username' in session:
        comment_service.add_comment(post_id, session['username'], request.form['content'], parent_id=comment_id)
    return redirect(f'/post/{post_id}')
