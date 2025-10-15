from flask import Blueprint

transportista  = Blueprint(
    'transportista',  
    __name__,
    template_folder='templates',
    url_prefix='/transportista'
)

from . import routes  
