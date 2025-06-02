import os

class Config:
    SERVER = os.getenv("MYSQL_SERVER", "167.114.196.68")
    DATABASE = os.getenv("MYSQL_DB", "inv3rsol_prueba")
    USERNAME = os.getenv("MYSQL_USER", "inv3rsol_sa")
    PASSWORD = os.getenv("MYSQL_PASSWORD", "Inversol123@")
    PORT = os.getenv("MYSQL_PORT", "3306")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{USERNAME}:{PASSWORD}@{SERVER}:{PORT}/{DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False