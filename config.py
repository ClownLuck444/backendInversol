import os

class Config:
    # Leer las credenciales de PostgreSQL desde variables de entorno
    SERVER = os.getenv("POSTGRES_SERVER", "dpg-d0v06rh5pdvs73fvns5g-a.oregon-postgres.render.com")  # Host de la base de datos
    DATABASE = os.getenv("POSTGRES_DB", "inversol")  # Nombre de la base de datos
    USERNAME = os.getenv("POSTGRES_USER", "sa")  # Usuario
    PASSWORD = os.getenv("POSTGRES_PASSWORD", "243hXLa5WLbKg3lDBoYJ0Dgfxh95E1jO")  # Contraseña
    PORT = os.getenv("POSTGRES_PORT", "5432")  # Puerto por defecto de PostgreSQL

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{SERVER}:{PORT}/{DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False