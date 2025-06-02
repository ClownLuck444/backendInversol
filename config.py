import os

class Config:
    # Leer las credenciales de PostgreSQL desde variables de entorno
    SERVER = os.getenv("POSTGRES_SERVER", "localhost")  # Host de la base de datos
    DATABASE = os.getenv("POSTGRES_DB", "inversol")  # Nombre de la base de datos
    USERNAME = os.getenv("POSTGRES_USER", "sa")  # Usuario
    PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")  # Contraseña
    PORT = os.getenv("POSTGRES_PORT", "5432")  # Puerto por defecto de PostgreSQL

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{SERVER}:{PORT}/{DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False