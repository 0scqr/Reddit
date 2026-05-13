class Post:
    def __init__(self, title, content, author, likes, id):
        self.title = title
        self.content = content
        self.author = author
        self.likes = likes
        self.id = id

    def __str__(self):
        return (f"ID: {self.id} | Título: {self.title} | Autor: {self.author} | Likes: {self.likes}\n"
                f"   Contenido: {self.content}")
