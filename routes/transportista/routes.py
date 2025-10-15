from flask import Blueprint, render_template
from flask_login import login_required
from basedatos.models import db
from basedatos.decoradores import role_required



from . import transportista
reviews = []

# ---------- DASHBOARD ----------
@transportista.route("/")
@login_required
@role_required("transportista")
def dashboard():
    return render_template("transportista/transportista_dashboard.html")