from flask import Flask, render_template_string, request, redirect, session, url_for
import os
import sys

# Añadir el directorio raíz al path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from services import post_service, user_service, comment_service

app = Flask(__name__)
app.secret_key = "reddit_secret_key" # Para manejar sesiones de usuario

# --- DISEÑO CSS PREMIUM ESTILO REDDIT ---
CSS_STYLE = """
<style>
    :root {
        --reddit-bg: #030303;
        --reddit-post-bg: #1A1A1B;
        --reddit-border: #343536;
        --reddit-text: #D7DADC;
        --reddit-orange: #FF4500;
        --reddit-blue: #0079D3;
    }
    body { font-family: 'IBM Plex Sans', Arial, sans-serif; background-color: var(--reddit-bg); color: var(--reddit-text); margin: 0; }
    .navbar { background-color: var(--reddit-post-bg); padding: 10px 20px; border-bottom: 1px solid var(--reddit-border); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }
    .container { max-width: 800px; margin: 20px auto; padding: 0 10px; }
    
    .post-card { background-color: var(--reddit-post-bg); border: 1px solid var(--reddit-border); border-radius: 5px; padding: 15px; margin-bottom: 15px; }
    .post-header { font-size: 12px; color: #818384; margin-bottom: 10px; }
    .post-title { font-size: 20px; font-weight: 600; margin-bottom: 15px; display: block; color: white; text-decoration: none; }
    .post-content { font-size: 14px; line-height: 21px; margin-bottom: 20px; }
    
    .comment-section { margin-top: 30px; border-top: 1px solid var(--reddit-border); padding-top: 20px; }
    .comment { border-left: 2px solid var(--reddit-border); margin-left: 10px; padding-left: 15px; margin-top: 15px; }
    .comment-meta { font-size: 12px; color: #818384; margin-bottom: 5px; }
    .comment-body { font-size: 14px; margin-bottom: 10px; }
    .reply-btn { background: none; border: none; color: #818384; cursor: pointer; font-size: 12px; font-weight: bold; padding: 0; }
    .reply-btn:hover { text-decoration: underline; }
    
    .input-box { width: 100%; background: #272729; border: 1px solid var(--reddit-border); border-radius: 4px; padding: 10px; color: white; margin-bottom: 10px; }
    .btn { background-color: var(--reddit-blue); color: white; border: none; border-radius: 20px; padding: 8px 16px; font-weight: bold; cursor: pointer; }
    .btn-orange { background-color: var(--reddit-orange); }
</style>
"""

# --- PLANTILLAS HTML ---
HTML_WRAPPER = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Reddit Simulation</title>
    {{ css | safe }}
</head>
<body>
    <div class="navbar">
        <a href="/" style="color: white; text-decoration: none; font-weight: bold; font-size: 20px;">Reddit Clone</a>
        <div>
            {% if session.get('username') %}
                <span>u/{{ session['username'] }}</span> | <a href="/logout" style="color: var(--reddit-blue);">Logout</a>
            {% else %}
                <a href="/login" class="btn">Login</a>
                <a href="/register" class="btn btn-orange">Registro</a>
            {% endif %}
        </div>
    </div>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

HOME_TEMPLATE = """
{% extends "wrapper" %}
{% block content %}
    {% for post in posts %}
    <div class="post-card">
        <div class="post-header">Publicado por u/{{ post.author }}</div>
        <a href="/post/{{ post.id }}" class="post-title">{{ post.title }}</a>
        <div class="post-content">{{ post.content | truncate(200) }}</div>
        <div class="post-header">{{ post.likes }} votos | <a href="/post/{{ post.id }}" style="color: var(--reddit-blue);">Ver comentarios</a></div>
    </div>
    {% endfor %}
{% endblock %}
"""

POST_DETAIL_TEMPLATE = """
{% extends "wrapper" %}
{% block content %}
    <div class="post-card">
        <div class="post-header">Publicado por u/{{ post.author }}</div>
        <h1 style="margin: 0 0 15px 0; font-size: 22px;">{{ post.title }}</h1>
        <div class="post-content">{{ post.content }}</div>
    </div>

    <div class="comment-section">
        <h3>Comentarios</h3>
        {% if session.get('username') %}
            <form action="/comment/{{ post.id }}" method="post">
                <textarea name="content" class="input-box" placeholder="¿Qué piensas?" required></textarea>
                <button type="submit" class="btn">Comentar</button>
            </form>
        {% else %}
            <p><a href="/login" style="color: var(--reddit-blue);">Inicia sesión</a> para dejar un comentario.</p>
        {% endif %}

        <div id="comments-container">
            {% for comment in comments %}
                {{ render_comment(comment) }}
            {% endfor %}
        </div>
    </div>
{% endblock %}
"""

# --- RUTAS DE LA APP ---

@app.route('/')
def home():
    posts = post_service.read_all_posts()
    return render_template_string(HOME_TEMPLATE, posts=posts, session=session, css=CSS_STYLE)

@app.route('/post/<post_id>')
def post_detail(post_id):
    post = post_service.read_post(post_id)
    # Lógica para obtener comentarios anidados
    all_comments = comment_service.get_comments_for_post(post_id)
    
    # Función recursiva para mostrar comentarios en árbol
    def render_comment(comment):
        html = f'<div class="comment">'
        html += f'<div class="comment-meta">u/{comment["author"]}</div>'
        html += f'<div class="comment-body">{comment["content"]}</div>'
        if session.get('username'):
            html += f'<button class="reply-btn" onclick="showReplyForm(\'{comment["id"]}\')">Responder</button>'
            html += f'<div id="reply-form-{comment["id"]}" style="display:none; margin-top:10px;">'
            html += f'<form action="/reply/{post_id}/{comment["id"]}" method="post">'
            html += f'<textarea name="content" class="input-box" required></textarea>'
            html += f'<button type="submit" class="btn">Enviar respuesta</button>'
            html += f'</form></div>'
        
        # Renderizar hijos si existen (esto requiere lógica en el service que devuelva hijos)
        if "replies" in comment:
            for reply in comment["replies"]:
                html += render_comment(reply)
        html += '</div>'
        return html

    # Modificamos la plantilla para incluir el script de respuesta
    custom_template = POST_DETAIL_TEMPLATE + """
    <script>
    function showReplyForm(commentId) {
        var form = document.getElementById('reply-form-' + commentId);
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
    }
    </script>
    """
    
    return render_template_string(custom_template, post=post, comments=all_comments, render_comment=render_comment, session=session, css=CSS_STYLE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = user_service.authenticate_user(request.form['username'], request.form['password'])
        if user:
            session['username'] = user.name
            return redirect(url_for('home'))
        return "Usuario o contraseña incorrectos", 401
    return render_template_string(HTML_WRAPPER + '<div class="post-card"><h2>Login</h2><form method="post"><input name="username" placeholder="Usuario" class="input-box" required><input name="password" type="password" placeholder="Contraseña" class="input-box" required><button class="btn">Entrar</button></form></div>', css=CSS_STYLE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_service.create_user(request.form['username'], request.form['password'])
        return redirect(url_for('login'))
    return render_template_string(HTML_WRAPPER + '<div class="post-card"><h2>Registro</h2><form method="post"><input name="username" placeholder="Usuario" class="input-box" required><input name="password" type="password" placeholder="Contraseña" class="input-box" required><button class="btn btn-orange">Registrarse</button></form></div>', css=CSS_STYLE)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/comment/<post_id>', methods=['POST'])
def add_comment(post_id):
    if 'username' in session:
        comment_service.add_comment(post_id, session['username'], request.form['content'])
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/reply/<post_id>/<comment_id>', methods=['POST'])
def add_reply(post_id, comment_id):
    if 'username' in session:
        # Usamos una función que soporte parent_id
        comment_service.add_comment(post_id, session['username'], request.form['content'], parent_id=comment_id)
    return redirect(url_for('post_detail', post_id=post_id))

# Registro de plantilla base
@app.context_processor
def inject_wrapper():
    return dict(wrapper=render_template_string(HTML_WRAPPER, css=CSS_STYLE))

if __name__ == "__main__":
    app.run(debug=True)
