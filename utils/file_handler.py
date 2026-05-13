import os


def ensure_file_exists(filename, header):
    """Crea el archivo con header si no existe."""
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(header + "\n")


def read_csv(filename):
    """Lee un CSV y devuelve lista de filas (como strings), excluyendo header."""
    ensure_file_exists(filename, "")
    with open(filename, "r") as f:
        lines = f.readlines()
    if not lines:
        return []
    return [line.strip() for line in lines[1:] if line.strip()]


def write_csv(filename, header, rows):
    """Escribe header + filas al CSV."""
    with open(filename, "w") as f:
        f.write(header + "\n")
        for row in rows:
            f.write(row + "\n")


def append_with_newline(filename, text):
    """Agrega una línea al final asegurando que termine con newline."""
    ensure_file_exists(filename, "")
    with open(filename, "a+") as f:
        if os.path.getsize(filename) > 0:
            f.seek(0, os.SEEK_END)
            pos = f.tell()
            if pos > 0:
                f.seek(pos - 1)
                last_char = f.read(1)
                if last_char != "\n":
                    f.write("\n")
        f.write(text + "\n")
