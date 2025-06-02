import os
from urllib.parse import quote_plus

class Config:
    DRIVER = "ODBC Driver 17 for SQL Server"
    SERVER = "192.168.1.98"
    DATABASE = "prueba"
    USERNAME = "sa"
    PASSWORD = "inversol2016"

    DRIVER_ENCODED = quote_plus(DRIVER)
    
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}"
        f"?driver={DRIVER_ENCODED}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
