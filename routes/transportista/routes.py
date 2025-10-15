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

    # Eventos del calendario
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

    # Pedidos con FechaEntrega o HoraLlegada definida
    pedidos_con_fecha = Pedido.query.filter(
        or_(
            Pedido.FechaEntrega.isnot(None),
            Pedido.HoraLlegada.isnot(None)
        )
    ).all()

    for p in pedidos_con_fecha:
        usuario = Usuario.query.get(p.ID_Usuario)
        nombre_usuario = f"{usuario.Nombre} {usuario.Apellido or ''}".strip() if usuario else "Desconocido"

        # Fecha base del evento
        if p.FechaEntrega:
            fecha_evento = p.FechaEntrega
        elif p.HoraLlegada:
            fecha_evento = p.HoraLlegada.date()
        else:
            continue  # Sin fecha no lo añadimos

        # Hora base del evento
        hora_evento = p.HoraLlegada.time() if p.HoraLlegada else time(12, 0, 0)

        start = datetime.combine(fecha_evento, hora_evento).isoformat()

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
