from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from basedatos.models import db, Calendario, Pedido, Usuario
from basedatos.decoradores import role_required
import datetime  # Importar el módulo completo para usar date, time, datetime

from . import transportista
reviews = []

# ---------- DASHBOARD ----------
@transportista.route("/")
@login_required
@role_required("transportista")
def dashboard():
    return render_template("transportista/transportista_dashboard.html")

@transportista.route('/api/calendario')
@login_required
@role_required("transportista")
def api_calendario():
    eventos = []

    # Obtener eventos del calendario
    calendarios = Calendario.query.all()
    for c in calendarios:
        usuario = Usuario.query.get(c.ID_Usuario)
        nombre_usuario = f"{usuario.Nombre} {usuario.Apellido or ''}".strip() if usuario else "Desconocido"

        # Construir fecha y hora en ISO 8601
        if isinstance(c.Fecha, datetime.date) and isinstance(c.Hora, datetime.time):
            start = datetime.datetime.combine(c.Fecha, c.Hora).isoformat()
        else:
            # Fallback si no son tipos datetime
            start = f"{c.Fecha}T{c.Hora}"

        eventos.append({
            "id": f"cal-{c.ID_Calendario}",
            "title": f"{c.Tipo} - Pedido #{c.ID_Pedido}",
            "start": start,
            "location": c.Ubicacion or "Sin ubicación",
            "tipo": c.Tipo,
            "usuario": nombre_usuario
        })

    # Obtener pedidos con fecha de entrega no asociados al calendario
    pedidos_con_fecha = Pedido.query.filter(Pedido.FechaEntrega != None).all()
    ids_en_calendario = {c.ID_Pedido for c in calendarios if c.ID_Pedido is not None}

    for p in pedidos_con_fecha:
        if p.ID_Pedido not in ids_en_calendario:
            usuario = Usuario.query.get(p.ID_Usuario)
            nombre_usuario = f"{usuario.Nombre} {usuario.Apellido or ''}".strip() if usuario else "Desconocido"

            hora = p.HoraLlegada if p.HoraLlegada else datetime.time(12, 0, 0)
            if isinstance(p.FechaEntrega, datetime.date) and isinstance(hora, datetime.time):
                start = datetime.datetime.combine(p.FechaEntrega, hora).isoformat()
            else:
                start = f"{p.FechaEntrega}T{hora}"

            eventos.append({
                "id": f"pedido-{p.ID_Pedido}",
                "title": f"Entrega - Pedido #{p.ID_Pedido}",
                "start": start,
                "location": p.Destino or "Sin dirección",
                "tipo": "Entrega",
                "usuario": nombre_usuario
            })

    return jsonify(eventos)

@transportista.route('/calendario')
@login_required
@role_required("transportista")
def calendario():
    return render_template("transportista/calendario.html")
