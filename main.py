import os
from services import *

LIMPIAR = "cls" if os.name == "nt" else "clear"

def limpiar_pantalla():
    os.system(LIMPIAR)

def pausa():
    input("\nPresiona Enter para continuar...")

def mostrar_titulo(titulo):
    print("=" * 55)
    print(f"  {titulo}")
    print("=" * 55)

# ============================
# MENÚ PRINCIPAL
# ============================

def menu_principal():
    while True:
        limpiar_pantalla()
        mostrar_titulo("REDDIT CLI")
        print("")
        print("  1. Gestión de Usuarios")
        print("  2. Gestión de Posts")
        print("  3. Salir")
        print("")
        op = input("  Selecciona una opción: ").strip()

        if op == "1":
            menu_usuarios()
        elif op == "2":
            menu_posts()
        elif op == "3":
            limpiar_pantalla()
            print("¡Hasta luego!")
            break
        else:
            print("  Opción inválida.")
            pausa()

# ============================
# MENÚ USUARIOS
# ============================

def menu_usuarios():
    while True:
        limpiar_pantalla()
        mostrar_titulo("GESTIÓN DE USUARIOS")
        print("")
        print("  1. Crear usuario")
        print("  2. Ver usuario por ID")
        print("  3. Listar todos los usuarios")
        print("  4. Actualizar usuario")
        print("  5. Eliminar usuario")
        print("  6. Volver al menú principal")
        print("")
        op = input("  Selecciona una opción: ").strip()

        if op == "1":
            crear_usuario_cli()
        elif op == "2":
            ver_usuario_cli()
        elif op == "3":
            listar_usuarios_cli()
        elif op == "4":
            actualizar_usuario_cli()
        elif op == "5":
            eliminar_usuario_cli()
        elif op == "6":
            break
        else:
            print("  Opción inválida.")
            pausa()

def crear_usuario_cli():
    limpiar_pantalla()
    mostrar_titulo("CREAR USUARIO")
    nombre = input("  Nombre: ").strip()
    password = input("  Contraseña: ").strip()
    if not nombre or not password:
        print("  Error: Nombre y contraseña no pueden estar vacíos.")
        pausa()
        return
    user = create_user(nombre, password)
    print(f"\n   Usuario creado: {user}")
    pausa()

def ver_usuario_cli():
    limpiar_pantalla()
    mostrar_titulo("VER USUARIO")
    try:
        id_usuario = int(input("  ID del usuario: ").strip())
    except ValueError:
        print("  Error: Ingresa un número válido.")
        pausa()
        return
    user = read_user(id_usuario)
    if user:
        print(f"\n  {user}")
    else:
        print(f"\n   Usuario con ID {id_usuario} no encontrado.")
    pausa()

def listar_usuarios_cli():
    limpiar_pantalla()
    mostrar_titulo("LISTAR USUARIOS")
    users = read_all_users()
    if not users:
        print("\n  No hay usuarios registrados.")
    else:
        print("")
        for u in users:
            print(f"  {u}")
    pausa()

def actualizar_usuario_cli():
    limpiar_pantalla()
    mostrar_titulo("ACTUALIZAR USUARIO")
    try:
        id_usuario = int(input("  ID del usuario a actualizar: ").strip())
    except ValueError:
        print("  Error: Ingresa un número válido.")
        pausa()
        return
    user = read_user(id_usuario)
    if not user:
        print(f"\n   Usuario con ID {id_usuario} no encontrado.")
        pausa()
        return
    print(f"\n  Datos actuales: {user}\n")
    nombre = input(f"  Nuevo nombre (Enter para mantener '{user.name}'): ").strip()
    password = input(f"  Nueva contraseña (Enter para mantener '{user.password}'): ").strip()
    if not nombre:
        nombre = user.name
    if not password:
        password = user.password
    updated = update_user(nombre, password, id_usuario)
    if updated:
        print(f"\n   Usuario actualizado: {updated}")
    else:
        print("\n   Error al actualizar.")
    pausa()

def eliminar_usuario_cli():
    limpiar_pantalla()
    mostrar_titulo("ELIMINAR USUARIO")
    try:
        id_usuario = int(input("  ID del usuario a eliminar: ").strip())
    except ValueError:
        print("  Error: Ingresa un número válido.")
        pausa()
        return
    user = read_user(id_usuario)
    if not user:
        print(f"\n   Usuario con ID {id_usuario} no encontrado.")
        pausa()
        return
    print(f"\n  Usuario: {user}")
    confirm = input("\n  ¿Estás seguro? (s/N): ").strip().lower()
    if confirm == "s":
        delete_user(id_usuario)
        print(f"\n  Usuario con ID {id_usuario} eliminado.")
    else:
        print("\n  Operación cancelada.")
    pausa()

# ============================
# MENÚ POSTS
# ============================

def menu_posts():
    while True:
        limpiar_pantalla()
        mostrar_titulo("GESTIÓN DE POSTS")
        print("")
        print("  1. Crear post")
        print("  2. Ver post por ID")
        print("  3. Listar todos los posts")
        print("  4. Actualizar post")
        print("  5. Dar like a un post")
        print("  6. Eliminar post")
        print("  7. Volver al menú principal")
        print("")
        op = input("  Selecciona una opción: ").strip()

        if op == "1":
            crear_post_cli()
        elif op == "2":
            ver_post_cli()
        elif op == "3":
            listar_posts_cli()
        elif op == "4":
            actualizar_post_cli()
        elif op == "5":
            like_post_cli()
        elif op == "6":
            eliminar_post_cli()
        elif op == "7":
            break
        else:
            print("  Opción inválida.")
            pausa()

def crear_post_cli():
    limpiar_pantalla()
    mostrar_titulo("CREAR POST")
    titulo = input("  Título: ").strip()
    contenido = input("  Contenido: ").strip()
    autor = input("  Autor (nombre de usuario): ").strip()
    if not titulo or not contenido or not autor:
        print("  Error: Todos los campos son obligatorios.")
        pausa()
        return
    post = create_post(titulo, contenido, autor)
    print(f"\n   Post creado: {post}")
    pausa()

def ver_post_cli():
    limpiar_pantalla()
    mostrar_titulo("VER POST")
    try:
        id_post = int(input("  ID del post: ").strip())
    except ValueError:
        print("  Error: Ingresa un número válido.")
        pausa()
        return
    post = read_post(id_post)
    if post:
        print(f"\n  {post}")
    else:
        print(f"\n   Post con ID {id_post} no encontrado.")
    pausa()

def listar_posts_cli():
    limpiar_pantalla()
    mostrar_titulo("LISTAR POSTS")
    posts = read_all_posts()
    if not posts:
        print("\n  No hay posts registrados.")
    else:
        print("")
        for p in posts:
            print(f"  {p}")
            print("  " + "-" * 50)
    pausa()

def actualizar_post_cli():
    limpiar_pantalla()
    mostrar_titulo("ACTUALIZAR POST")
    try:
        id_post = int(input("  ID del post a actualizar: ").strip())
    except ValueError:
        print("  Error: Ingresa un número válido.")
        pausa()
        return
    post = read_post(id_post)
    if not post:
        print(f"\n   Post con ID {id_post} no encontrado.")
        pausa()
        return
    print(f"\n  Datos actuales:\n  {post}\n")
    titulo = input(f"  Nuevo título (Enter para mantener '{post.title}'): ").strip()
    contenido = input(f"  Nuevo contenido (Enter para mantener): ").strip()
    if not titulo:
        titulo = post.title
    if not contenido:
        contenido = post.content
    updated = update_post(id_post, title=titulo, content=contenido)
    if updated:
        print(f"\n  Post actualizado: {updated}")
    else:
        print("\n  Error al actualizar.")
    pausa()

def like_post_cli():
    limpiar_pantalla()
    mostrar_titulo("DAR LIKE A POST")
    try:
        id_post = int(input("  ID del post: ").strip())
    except ValueError:
        print("  Error: Ingresa un número válido.")
        pausa()
        return
    post = add_like_to_post(id_post)
    if post:
        print(f"\n  Like agregado. El post ahora tiene {post.likes} likes.")
    else:
        print(f"\n  Post con ID {id_post} no encontrado.")
    pausa()

def eliminar_post_cli():
    limpiar_pantalla()
    mostrar_titulo("ELIMINAR POST")
    try:
        id_post = int(input("  ID del post a eliminar: ").strip())
    except ValueError:
        print("  Error: Ingresa un número válido.")
        pausa()
        return
    post = read_post(id_post)
    if not post:
        print(f"\n  Post con ID {id_post} no encontrado.")
        pausa()
        return
    print(f"\n  Post:\n  {post}")
    confirm = input("\n  ¿Estás seguro? (s/N): ").strip().lower()
    if confirm == "s":
        delete_post(id_post)
        print(f"\n  Post con ID {id_post} eliminado.")
    else:
        print("\n  Operación cancelada.")
    pausa()

# ============================
# ENTRY POINT
# ============================

if __name__ == "__main__":
    menu_principal()
