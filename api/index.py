from flask import Flask, render_template_string, request, redirect, session, url_for
import os
import sys
import traceback

# Añadir el directorio raíz al path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from services import post_service, user_service, comment_service

app = Flask(__name__)
app.secret_key = "reddit_secret_key"

CSS_STYLE = """
<style>
    :root { --reddit-bg: #030303; --reddit-post-bg: #1A1A1B; --reddit-border: #343536; --reddit-text: #D7DADC; --reddit-orange: #FF4500; --reddit-blue: #0079D3; }
    body { font-family: 'IBM Plex Sans', sans-serif; background-color: var(--reddit-bg); color: var(--reddit-text); margin: 0; }
    .navbar { background-color: var(--reddit-post-bg); padding: 10px 20px; border-bottom: 1px solid var(--reddit-border); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; }
    .container { max-width: 800px; margin: 20px auto; padding: 0 10px; }
    .post-card { background-color: var(--reddit-post-bg); border: 1px solid var(--reddit-border); border-radius: 5px; padding: 15px; margin-bottom: 15px; }
    .post-title { font-size: 20px; font-weight: 600; color: white; text-decoration: none; display: block; margin-bottom: 10px; }
    .comment { border-left: 2px solid var(--reddit-border); margin-left: 10px; padding-left: 15px; margin-top: 15px; }
    .input-box { width: 100%; background: #272729; border: 1px solid var(--reddit-border); border-radius: 4px; padding: 10px; color: white; margin-bottom: 10px; box-sizing: border-box; }
    .btn { background-color: var(--reddit-blue); color: white; border: none; border-radius: 20px; padding: 8px 16px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; }
</style>
"""

def layout(content):
    nav = f"""
    <div class="navbar">
        <a href="/" style="color: white; text-decoration: none; font-weight: bold; font-size: 20px;">Reddit Clone</a>
        <div>
            {"<span>u/" + session['username'] + "</span> | <a href='/logout' style='color: var(--reddit-blue);'>Logout</a>" if 'username' in session else "<a href='/login' class='btn'>Login</a> <a href='/register' class='btn' style='background: var(--reddit-orange);'>Registro</a>"}
        </div>
    </div>
    """
    return f"""<!DOCTYPE html><html><head>
    <meta charset='UTF-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    :root {{ --reddit-bg: #030303; --reddit-post-bg: #1A1A1B; --reddit-border: #343536; --reddit-text: #D7DADC; --reddit-orange: #FF4500; --reddit-blue: #0079D3; }}
    body {{ font-family: 'IBM Plex Sans', sans-serif; background-color: var(--reddit-bg); color: var(--reddit-text); margin: 0; padding: 0; }}
    .navbar {{ background-color: var(--reddit-post-bg); padding: 10px 15px; border-bottom: 1px solid var(--reddit-border); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 1000; }}
    .container {{ max-width: 800px; margin: 0 auto; padding: 15px; box-sizing: border-box; }}
    .post-card {{ background-color: var(--reddit-post-bg); border: 1px solid var(--reddit-border); border-radius: 5px; padding: 15px; margin-bottom: 15px; }}
    .post-title {{ font-size: 18px; font-weight: 600; color: white; text-decoration: none; display: block; margin-bottom: 10px; line-height: 1.4; }}
    .comment {{ border-left: 2px solid var(--reddit-border); margin-left: 5px; padding-left: 10px; margin-top: 15px; }}
    .input-box {{ width: 100%; background: #272729; border: 1px solid var(--reddit-border); border-radius: 4px; padding: 12px; color: white; margin-bottom: 10px; box-sizing: border-box; font-size: 16px; }}
    .btn {{ background-color: var(--reddit-blue); color: white; border: none; border-radius: 20px; padding: 10px 20px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; font-size: 14px; }}
    
    @media (max-width: 600px) {{
        .post-title {{ font-size: 16px; }}
        .navbar {{ padding: 10px; }}
        .navbar a {{ font-size: 16px !important; }}
        .comment {{ margin-left: 2px; padding-left: 8px; }}
    }}
    </style>
</head>
<body>{nav}<div class='container'>{content}</div></body></html>"""

@app.route('/')
def home():
    try:
        posts = post_service.read_all_posts()
        content = "<h1>Tendencias</h1>"
        for p in posts:
            content += f'''
            <div class="post-card">
                <div style="font-size: 12px; color: #818384;">Publicado por u/{p.author}</div>
                <a href="/post/{p.id}" class="post-title">{p.title}</a>
                <div style="color: #818384;">{p.likes} votos | <a href="/post/{p.id}" style="color: var(--reddit-blue);">Ver comentarios</a></div>
            </div>'''
        return layout(content)
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route('/post/<post_id>')
def post_detail(post_id):
    try:
        post = post_service.read_post(post_id)
        comments = comment_service.get_comments_for_post(post_id)
        
        def render_tree(nodes):
            html = ""
            for c in nodes:
                html += f'<div class="comment">'
                html += f'<div style="font-size: 12px; color: #818384;">u/{c["author"]}</div>'
                html += f'<div>{c["content"]}</div>'
                if 'username' in session:
                    html += f'<button onclick="this.nextElementSibling.style.display=\'block\'" style="background:none; border:none; color:#818384; cursor:pointer; font-size:12px;">Responder</button>'
                    html += f'<div style="display:none; margin-top:10px;">'
                    html += f'<form action="/reply/{post_id}/{c["id"]}" method="post"><textarea name="content" class="input-box" required></textarea><button class="btn">Enviar</button></form></div>'
                if c.get("replies"):
                    html += render_tree(c["replies"])
                html += '</div>'
            return html

        form = f'<form action="/comment/{post_id}" method="post"><textarea name="content" class="input-box" placeholder="¿Qué piensas?" required></textarea><button class="btn">Comentar</button></form>' if 'username' in session else '<p>Inicia sesión para comentar</p>'
        
        content = f'''
        <div class="post-card">
            <div style="font-size: 12px; color: #818384;">u/{post.author}</div>
            <h1>{post.title}</h1>
            <p>{post.content}</p>
        </div>
        <h3>Comentarios</h3>
        {form}
        {render_tree(comments)}
        '''
        return layout(content)
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = user_service.authenticate_user(request.form['username'], request.form['password'])
        if user:
            session['username'] = user.name
            return redirect('/')
        return "Error: Usuario o clave incorrectos", 401
    return layout('<h2>Login</h2><form method="post"><input name="username" placeholder="Usuario" class="input-box" required><input name="password" type="password" placeholder="Clave" class="input-box" required><button class="btn">Entrar</button></form>')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_service.create_user(request.form['username'], request.form['password'])
        return redirect('/login')
    return layout('<h2>Registro</h2><form method="post"><input name="username" placeholder="Usuario" class="input-box" required><input name="password" type="password" placeholder="Clave" class="input-box" required><button class="btn" style="background: var(--reddit-orange);">Registrarse</button></form>')

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
