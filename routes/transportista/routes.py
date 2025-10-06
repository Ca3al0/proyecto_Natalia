import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify,session
from flask_login import login_required, current_user
from datetime import date,datetime, timedelta
from flask import current_app
from basedatos.models import db, Usuario, Notificaciones, Direccion, Producto, Proveedor,Categorias,Resena,Compra,Pedido
from werkzeug.security import generate_password_hash
from basedatos.decoradores import role_required
from basedatos.notificaciones import crear_notificacion
from werkzeug.utils import secure_filename
from sqlalchemy import func



reviews = []

admin = Blueprint("transportista", __name__, url_prefix="/transportista")

@admin.route("/")
@login_required
@role_required("transportista")
def dashboard():
    return render_template("transportista/dashboard_transportista.html")
