from flask import Flask, render_template_string
import os
import sys

# Forzar que la carpeta raíz sea visible para Python
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

app = Flask(__name__)

# Plantilla HTML minimalista con estilo Reddit
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reddit Simulation - Vercel</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #DAE0E6; margin: 0; padding: 20px; }
        .header { background-color: white; padding: 10px 20px; margin-bottom: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .post { background-color: white; padding: 15px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #ccc; }
        .post:hover { border-color: #888; }
        .title { font-size: 18px; font-weight: bold; color: #1c1c1c; text-decoration: none; }
        .meta { font-size: 12px; color: #787c7e; margin-top: 5px; }
        .content { margin-top: 10px; color: #1a1a1b; }
        .likes { font-weight: bold; color: #ff4500; }
        .no-posts { text-align: center; color: #787c7e; padding: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Simulación de Reddit</h1>
        <p>Conectado a Supabase</p>
    </div>

    {% if posts %}
        {% for post in posts %}
        <div class="post">
            <div class="title">{{ post.title }}</div>
            <div class="meta">Publicado por @{{ post.author }} | <span class="likes">▲ {{ post.likes }} likes</span></div>
            <div class="content">{{ post.content }}</div>
        </div>
        {% endfor %}
    {% else %}
        <div class="no-posts">
            <h2>No hay publicaciones todavía.</h2>
            <p>¡Crea la primera desde la App de escritorio!</p>
        </div>
    {% endif %}
</body>
</html>
"""

@app.route('/test')
def test():
    return "Servidor Flask funcionando correctamente!"

@app.route('/')
def home():
    try:
        from services import post_service
        posts = post_service.read_all_posts()
        return render_template_string(HTML_TEMPLATE, posts=posts)
    except Exception as e:
        return f"Error al conectar con Supabase: {str(e)}", 500

# Esto es necesario para que Vercel lo reconozca
app.debug = True
