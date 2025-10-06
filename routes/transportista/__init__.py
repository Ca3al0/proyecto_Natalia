from flask import Blueprint

transportista = Blueprint('transportista', __name__, url_prefix='/transportista', template_folder='../../templates')

# Importar rutas después de definir el blueprint
from . import routes
