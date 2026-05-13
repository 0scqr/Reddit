class User:
    def __init__(self, name, password, id):
        self.name = name
        self.password = password
        self.id = id

    def __str__(self):
        return f"ID: {self.id} | Nombre: {self.name} | Contraseña: {self.password}"
