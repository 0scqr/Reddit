import tkinter as tk
from tkinter import messagebox
import hashlib
from services import user_service, post_service, comment_service

# --- Backend Classes (slightly modified for GUI and DB) ---
class Comment:
    def __init__(self, user, text, parent_id=None, comment_id=None):
        self.comment_id = comment_id # Added for DB management
        self.user = user
        self.text = text
        self.parent_id = parent_id # Store parent comment ID for tree structure
        self.replies = []

    def add_reply(self, comment):
        self.replies.append(comment)

    def display(self, indent=0):
        return "  " * indent + f"@{self.user}: {self.text}"

class Post:
    def __init__(self, user, title, content, post_id=None):
        self.post_id = post_id # Added for DB management
        self.user = user
        self.title = title
        self.content = content
        self.comments = [] # Comments will be loaded from DB when needed

    def add_comment(self, comment):
        self.comments.append(comment)

    def display(self):
        return f"--- {self.title} by @{self.user} ---\n{self.content}\n"

class User:
    def __init__(self, username, password_hash=None):
        self.username = username
        self.password_hash = password_hash

    def create_post(self, title, content):
        post = Post(self.username, title, content)
        # Post will be saved to DB externally
        return post

    def __str__(self):
        return self.username

# --- Database Manager (Now using Supabase services) ---
class DatabaseManager:
    def __init__(self):
        # No longer needs to connect to local sqlite
        pass

    def add_user(self, username, password_hash):
        # The password_hash here is what we store in Supabase "password" column
        user = user_service.create_user(username, password_hash)
        return user is not None

    def get_user(self, username):
        # We need a way to get user by name. I'll add this to user_service
        users = user_service.read_all_users()
        for u in users:
            if u.name == username:
                # Return an object that has username and password_hash
                return User(u.name, u.password)
        return None

    def add_post(self, user, title, content):
        post = post_service.create_post(title, content, user)
        return post.id if post else None

    def get_all_posts(self):
        s_posts = post_service.read_all_posts()
        posts = []
        for p in s_posts:
            # Convert service Post to GUI Post
            posts.append(Post(p.author, p.title, p.content, p.id))
        return posts

    def get_comments_for_post(self, post_id):
        # Returns root comments with replies nested
        return comment_service.get_comments_for_post(post_id)

    def add_comment(self, post_id, user, text, parent_id=None):
        return comment_service.add_comment(post_id, user, text, parent_id)

    def close(self):
        pass

# --- GUI (Tkinter) ---
class RedditGUI:
    def __init__(self, master):
        self.master = master
        master.title("Simulador de Reddit")
        master.geometry("800x600")

        self.db = DatabaseManager()
        self.current_user = None

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.main_frame = tk.Frame(master, bg="#f0f2f5")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.create_main_menu()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        self.clear_frame()
        self.main_frame.config(padx=20, pady=20)

        tk.Label(self.main_frame, text="--- Simulador de Reddit ---", font=("Arial", 16, "bold"), bg="#f0f2f5").pack(pady=15)

        tk.Button(self.main_frame, text="Crear usuario", command=self.create_user_menu, font=("Arial", 12), bg="#007bff", fg="white", width=20).pack(pady=5)
        tk.Button(self.main_frame, text="Iniciar sesión", command=self.login_menu, font=("Arial", 12), bg="#28a745", fg="white", width=20).pack(pady=5)
        tk.Button(self.main_frame, text="Ver todas las publicaciones", command=self.view_all_posts_menu, font=("Arial", 12), bg="#17a2b8", fg="white", width=20).pack(pady=5)
        tk.Button(self.main_frame, text="Salir", command=self.master.quit, font=("Arial", 12), bg="#dc3545", fg="white", width=20).pack(pady=5)

        # Información del creador y la materia
        tk.Label(self.main_frame, text="Creador: Oscar Ortega", font=("Arial", 10), bg="#f0f2f5").pack(side="bottom", anchor="e", padx=10, pady=5)
        tk.Label(self.main_frame, text="Materia: Programacion No Numerica I", font=("Arial", 10), bg="#f0f2f5").pack(side="bottom", anchor="e", padx=10)

    def create_user_menu(self):
        self.clear_frame()
        self.main_frame.config(padx=20, pady=20)

        tk.Label(self.main_frame, text="Crear Usuario", font=("Arial", 14, "bold"), bg="#f0f2f5").pack(pady=10)

        tk.Label(self.main_frame, text="Nombre de usuario:", bg="#f0f2f5").pack(anchor="w", pady=(10,0))
        self.username_entry = tk.Entry(self.main_frame, width=40, font=("Arial", 10))
        self.username_entry.pack(pady=2)

        tk.Label(self.main_frame, text="Contraseña:", bg="#f0f2f5").pack(anchor="w", pady=(10,0))
        self.password_entry = tk.Entry(self.main_frame, show="*", width=40, font=("Arial", 10))
        self.password_entry.pack(pady=2)

        tk.Label(self.main_frame, text="Confirmar Contraseña:", bg="#f0f2f5").pack(anchor="w", pady=(10,0))
        self.confirm_password_entry = tk.Entry(self.main_frame, show="*", width=40, font=("Arial", 10))
        self.confirm_password_entry.pack(pady=2)

        tk.Button(self.main_frame, text="Crear", command=self._create_user, font=("Arial", 12), bg="#28a745", fg="white", width=15).pack(pady=10)
        tk.Button(self.main_frame, text="Volver", command=self.create_main_menu, font=("Arial", 12), bg="#6c757d", fg="white", width=15).pack(pady=5)

    def _create_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not username or not password or not confirm_password:
            messagebox.showerror("Error de Validación", "Todos los campos son obligatorios.")
            return
        if " " in username:
            messagebox.showerror("Error de Validación", "El nombre de usuario no puede contener espacios.")
            return
        if password != confirm_password:
            messagebox.showerror("Error de Validación", "Las contraseñas no coinciden.")
            return
        if len(password) < 6:
            messagebox.showerror("Error de Validación", "La contraseña debe tener al menos 6 caracteres.")
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if self.db.add_user(username, password_hash):
            messagebox.showinfo("Éxito", f"Usuario {username} creado.")
            self.create_main_menu()
        else:
            messagebox.showerror("Error", "Ese nombre de usuario ya existe.")

    def login_menu(self):
        self.clear_frame()
        self.main_frame.config(padx=20, pady=20)

        tk.Label(self.main_frame, text="Iniciar Sesión", font=("Arial", 14, "bold"), bg="#f0f2f5").pack(pady=10)

        tk.Label(self.main_frame, text="Nombre de usuario:", bg="#f0f2f5").pack(anchor="w", pady=(10,0))
        self.login_username_entry = tk.Entry(self.main_frame, width=40, font=("Arial", 10))
        self.login_username_entry.pack(pady=2)

        tk.Label(self.main_frame, text="Contraseña:", bg="#f0f2f5").pack(anchor="w", pady=(10,0))
        self.login_password_entry = tk.Entry(self.main_frame, show="*", width=40, font=("Arial", 10))
        self.login_password_entry.pack(pady=2)

        tk.Button(self.main_frame, text="Iniciar Sesión", command=self._login, font=("Arial", 12), bg="#007bff", fg="white", width=15).pack(pady=10)
        tk.Button(self.main_frame, text="Volver", command=self.create_main_menu, font=("Arial", 12), bg="#6c757d", fg="white", width=15).pack(pady=5)

    def _login(self):
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get()

        if not username or not password:
            messagebox.showerror("Error de Validación", "Todos los campos son obligatorios.")
            return

        user = self.db.get_user(username)
        if user:
            provided_password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user.password_hash == provided_password_hash:
                self.current_user = user
                messagebox.showinfo("Bienvenido", f"Bienvenido, @{self.current_user.username}!")
                self.user_menu()
            else:
                messagebox.showerror("Error de Autenticación", "Contraseña incorrecta.")
        else:
            messagebox.showerror("Error de Autenticación", "Nombre de usuario no encontrado.")

    def user_menu(self):
        self.clear_frame()
        self.main_frame.config(padx=20, pady=20)

        tk.Label(self.main_frame, text=f"--- Menú de {self.current_user.username} ---", font=("Arial", 16, "bold"), bg="#f0f2f5").pack(pady=15)

        tk.Button(self.main_frame, text="Crear publicación", command=self.create_post_menu, font=("Arial", 12), bg="#007bff", fg="white", width=20).pack(pady=5)
        tk.Button(self.main_frame, text="Ver mis publicaciones", command=self.view_my_posts_menu, font=("Arial", 12), bg="#28a745", fg="white", width=20).pack(pady=5)
        tk.Button(self.main_frame, text="Ver todas las publicaciones", command=self.view_all_posts_menu, font=("Arial", 12), bg="#17a2b8", fg="white", width=20).pack(pady=5)
        tk.Button(self.main_frame, text="Cerrar sesión", command=self._logout, font=("Arial", 12), bg="#dc3545", fg="white", width=20).pack(pady=5)

    def _logout(self):
        self.current_user = None
        messagebox.showinfo("Sesión cerrada", "Has cerrado sesión.")
        self.create_main_menu()

    def create_post_menu(self):
        self.clear_frame()
        self.main_frame.config(padx=20, pady=20)

        tk.Label(self.main_frame, text="Crear Publicación", font=("Arial", 14, "bold"), bg="#f0f2f5").pack(pady=10)

        tk.Label(self.main_frame, text="Título:", bg="#f0f2f5").pack(anchor="w", pady=(10,0))
        self.post_title_entry = tk.Entry(self.main_frame, width=60, font=("Arial", 10))
        self.post_title_entry.pack(pady=2)

        tk.Label(self.main_frame, text="Contenido:", bg="#f0f2f5").pack(anchor="w", pady=(10,0))
        self.post_content_text = tk.Text(self.main_frame, height=10, width=60, font=("Arial", 10))
        self.post_content_text.pack(pady=2)

        tk.Button(self.main_frame, text="Publicar", command=self._create_post, font=("Arial", 12), bg="#28a745", fg="white", width=15).pack(pady=10)
        tk.Button(self.main_frame, text="Volver", command=self.user_menu, font=("Arial", 12), bg="#6c757d", fg="white", width=15).pack(pady=5)

    def _create_post(self):
        title = self.post_title_entry.get().strip()
        content = self.post_content_text.get("1.0", tk.END).strip()
        if title and content:
            post_id = self.db.add_post(self.current_user.username, title, content)
            messagebox.showinfo("Éxito", "Publicación creada.")
            self.user_menu()
        else:
            messagebox.showerror("Error", "El título y el contenido no pueden estar vacíos.")

    def view_my_posts_menu(self):
        self.clear_frame()
        self.main_frame.config(padx=20, pady=20)
        tk.Label(self.main_frame, text=f"--- Mis Publicaciones ({self.current_user.username}) ---", font=("Arial", 14, "bold"), bg="#f0f2f5").pack(pady=10)

        posts = self.db.get_all_posts() # Get all posts from DB
        user_posts = [post for post in posts if post.user == self.current_user.username]

        if not user_posts:
            tk.Label(self.main_frame, text="No has creado ninguna publicación todavía.", bg="#f0f2f5").pack(pady=10)
        else:
            for i, post in enumerate(user_posts):
                post_frame = tk.Frame(self.main_frame, bd=2, relief="groove", padx=10, pady=10, bg="#ffffff")
                post_frame.pack(fill=tk.X, pady=5)
                tk.Label(post_frame, text=f"ID: {post.post_id}", font=("Arial", 10, "bold"), bg="#ffffff").pack(anchor="w")
                tk.Label(post_frame, text=post.display(), justify=tk.LEFT, bg="#ffffff").pack(anchor="w")
                tk.Button(post_frame, text="Ver/Comentar", command=lambda p=post: self.view_post_details(p), bg="#17a2b8", fg="white").pack(pady=5)

        tk.Button(self.main_frame, text="Volver", command=self.user_menu, font=("Arial", 12), bg="#6c757d", fg="white", width=15).pack(pady=10)


    def view_all_posts_menu(self):
        self.clear_frame()
        self.main_frame.config(padx=20, pady=20)
        tk.Label(self.main_frame, text="--- Todas las Publicaciones ---", font=("Arial", 14, "bold"), bg="#f0f2f5").pack(pady=10)

        posts = self.db.get_all_posts()

        if not posts:
            tk.Label(self.main_frame, text="No hay publicaciones para mostrar.", bg="#f0f2f5").pack(pady=10)
        else:
            for i, post in enumerate(posts):
                post_frame = tk.Frame(self.main_frame, bd=2, relief="groove", padx=10, pady=10, bg="#ffffff")
                post_frame.pack(fill=tk.X, pady=5)
                tk.Label(post_frame, text=f"ID: {post.post_id}", font=("Arial", 10, "bold"), bg="#ffffff").pack(anchor="w")
                tk.Label(post_frame, text=post.display(), justify=tk.LEFT, bg="#ffffff").pack(anchor="w")
                tk.Button(post_frame, text="Ver/Comentar", command=lambda p=post: self.view_post_details(p), bg="#17a2b8", fg="white").pack(pady=5)

        if self.current_user:
            tk.Button(self.main_frame, text="Volver", command=self.user_menu, font=("Arial", 12), bg="#6c757d", fg="white", width=15).pack(pady=10)
        else:
            tk.Button(self.main_frame, text="Volver", command=self.create_main_menu, font=("Arial", 12), bg="#6c757d", fg="white", width=15).pack(pady=10)

    def view_post_details(self, post):
        self.clear_frame()
        self.main_frame.config(padx=20, pady=20)

        tk.Label(self.main_frame, text=f"--- {post.title} by @{post.user} ---", font=("Arial", 14, "bold"), bg="#f0f2f5").pack(pady=10)
        tk.Label(self.main_frame, text=post.content, justify=tk.LEFT, wraplength=700, bg="#f0f2f5").pack(anchor="w", pady=5)

        tk.Label(self.main_frame, text="\nComentarios:", font=("Arial", 12, "bold"), bg="#f0f2f5").pack(anchor="w", pady=(10,5))
        
        comments_frame = tk.Frame(self.main_frame, bg="#e9ecef", padx=10, pady=10)
        comments_frame.pack(fill=tk.BOTH, expand=True)

        post.comments = self.db.get_comments_for_post(post.post_id) # Load comments dynamically
        self._display_comments(post.comments, comments_frame)

        if self.current_user:
            tk.Label(self.main_frame, text="\nAñadir nuevo comentario:", bg="#f0f2f5").pack(anchor="w", pady=(10,0))
            self.new_comment_text = tk.Text(self.main_frame, height=3, width=70, font=("Arial", 10))
            self.new_comment_text.pack(pady=2)
            tk.Button(self.main_frame, text="Comentar", command=lambda: self._add_comment_to_post(post), bg="#28a745", fg="white").pack(pady=5)

            tk.Label(self.main_frame, text="\nResponder a un comentario (ID):", bg="#f0f2f5").pack(anchor="w", pady=(10,0))
            self.reply_comment_id_entry = tk.Entry(self.main_frame, width=10, font=("Arial", 10))
            self.reply_comment_id_entry.pack(pady=2, anchor="w")
            self.reply_comment_text = tk.Text(self.main_frame, height=3, width=70, font=("Arial", 10))
            self.reply_comment_text.pack(pady=2)
            tk.Button(self.main_frame, text="Responder", command=lambda: self._reply_to_comment(post), bg="#007bff", fg="white").pack(pady=5)

            tk.Button(self.main_frame, text="Volver a publicaciones", command=self.view_all_posts_menu, font=("Arial", 12), bg="#6c757d", fg="white", width=20).pack(pady=10)
        else:
            tk.Button(self.main_frame, text="Volver a publicaciones", command=self.view_all_posts_menu, font=("Arial", 12), bg="#6c757d", fg="white", width=20).pack(pady=10)

    def _display_comments(self, comments, parent_frame, indent=0):
        current_id_ref = [0]
        self._display_comments_recursive(comments, parent_frame, indent, current_id_ref)

    def _display_comments_recursive(self, comments, parent_frame, indent, current_id_ref):
        for comment in comments:
            current_id_ref[0] += 1
            comment_frame = tk.Frame(parent_frame, bg="#f8f9fa", bd=1, relief="solid")
            comment_frame.pack(fill=tk.X, padx=indent*15, pady=2)
            tk.Label(comment_frame, text=f"[{comment.comment_id}] @{comment.user}: {comment.text}", justify=tk.LEFT, wraplength=600 - indent*15, bg="#f8f9fa").pack(anchor="w", padx=5, pady=2)
            if comment.replies:
                self._display_comments_recursive(comment.replies, comment_frame, indent + 1, current_id_ref)

    def _add_comment_to_post(self, post):
        if not self.current_user:
            messagebox.showerror("Error", "Debes iniciar sesión para comentar.")
            return

        comment_text = self.new_comment_text.get("1.0", tk.END).strip()
        if comment_text:
            self.db.add_comment(post.post_id, self.current_user.username, comment_text)
            messagebox.showinfo("Éxito", "Comentario añadido.")
            self.view_post_details(post) # Refresh the view
        else:
            messagebox.showerror("Error", "El comentario no puede estar vacío.")

    def _reply_to_comment(self, post):
        if not self.current_user:
            messagebox.showerror("Error", "Debes iniciar sesión para responder.")
            return

        try:
            target_comment_id = int(self.reply_comment_id_entry.get())
            reply_text = self.reply_comment_text.get("1.0", tk.END).strip()

            if not reply_text:
                messagebox.showerror("Error", "La respuesta no puede estar vacía.")
                return

            # This requires a slight modification to find_comment_by_id to work with actual comment_ids from DB
            # For now, let's assume direct ID is used.
            # We need to fetch all comments for the post and then find the target comment by its DB ID.
            all_comments_for_post = self.db.get_comments_for_post(post.post_id)

            target_comment = None
            # Simple linear search for now, could be optimized with a dictionary if comments were stored that way
            def find_comment_by_db_id_recursive(comments_list, db_id):
                for c in comments_list:
                    if c.comment_id == db_id:
                        return c
                    found = find_comment_by_db_id_recursive(c.replies, db_id)
                    if found:
                        return found
                return None
            
            target_comment = find_comment_by_db_id_recursive(all_comments_for_post, target_comment_id)

            if target_comment:
                self.db.add_comment(post.post_id, self.current_user.username, reply_text, target_comment.comment_id)
                messagebox.showinfo("Éxito", "Respuesta añadida.")
                self.view_post_details(post) # Refresh the view
            else:
                messagebox.showerror("Error", "ID de comentario no válido.")
        except ValueError:
            messagebox.showerror("Error", "Entrada no válida. Por favor, introduce un número para el ID del comentario.")




root = tk.Tk()
app = RedditGUI(root)
root.mainloop()