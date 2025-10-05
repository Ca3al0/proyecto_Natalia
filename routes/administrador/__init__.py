from flask import Blueprint

# Importar el blueprint desde routes.py
from .routes import admin

# Hacemos visible el blueprint para que app.py lo pueda registrar
__all__ = ["admin"]
