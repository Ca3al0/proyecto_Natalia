from flask import Blueprint

cliente = Blueprint(
    'cliente',  
    __name__,
    template_folder='templates',
    url_prefix='/cliente'
)

from . import routes 
