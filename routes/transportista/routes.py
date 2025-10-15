from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from basedatos.models import db, Calendario, Pedido, Usuario
from basedatos.decoradores import role_required
from datetime import datetime, date, time

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

    # Eventos del calendario (si los usas)
    calendarios = Calendario.query.all()

    for c in calendarios:
        usuario = Usuario.query.get(c.ID_Usuario)
        nombre_usuario = f"{usuario.Nombre} {usuario.Apellido or ''}".strip() if usuario else "Desconocido"

        if isinstance(c.Fecha, date) and isinstance(c.Hora, time):
            start = datetime.combine(c.Fecha, c.Hora).isoformat()
        else:
            start = f"{c.Fecha}T{c.Hora}"

        eventos.append({
            "id": f"cal-{c.ID_Calendario}",
            "title": f"{c.Tipo} - Pedido #{c.ID_Pedido}",
            "start": start,
            "location": c.Ubicacion or "Sin ubicación",
            "tipo": c.Tipo,
            "usuario": nombre_usuario
        })

    # Pedidos con fecha de entrega definida
    pedidos_con_fecha = Pedido.query.filter(Pedido.FechaEntrega.isnot(None)).all()

    for p in pedidos_con_fecha:
        usuario = Usuario.query.get(p.ID_Usuario)
        nombre_usuario = f"{usuario.Nombre} {usuario.Apellido or ''}".strip() if usuario else "Desconocido"

        hora_fija = time(12, 0, 0)  

        if isinstance(p.FechaEntrega, date):
            start = datetime.combine(p.FechaEntrega, hora_fija).isoformat()
        else:
            start = f"{p.FechaEntrega}T12:00:00"

        tipo_evento = "Instalación" if p.Instalacion == 1 else "Entrega"

        eventos.append({
            "id": f"pedido-{p.ID_Pedido}",
            "title": f"{tipo_evento} - Pedido #{p.ID_Pedido}",
            "start": start,
            "location": p.Destino or "Sin dirección",
            "tipo": tipo_evento,
            "usuario": nombre_usuario
        })

    return jsonify(eventos)

@transportista.route('/calendario')
@login_required
@role_required("transportista")
def calendario():
    return render_template("transportista/calendario.html")
