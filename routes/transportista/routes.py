from flask_login import login_required
from sqlalchemy import or_
from basedatos.models import db, Calendario, Pedido, Usuario
from basedatos.decoradores import role_required
from datetime import datetime, time
import os
import json
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from datetime import datetime
from flask import current_app
from basedatos.models import db, Usuario,Pedido, RegistroFotografico,Calendario
from basedatos.decoradores import role_required
from werkzeug.utils import secure_filename
from sqlalchemy import func


from . import transportista

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

    try:
        # --- Eventos de Calendario ---
        calendarios = db.session.query(Calendario, Usuario)\
            .join(Usuario, Calendario.ID_Usuario == Usuario.ID_Usuario, isouter=True).all()

        for c, u in calendarios:
            nombre_usuario = f"{u.Nombre} {u.Apellido or ''}".strip() if u else "Desconocido"

            try:
                start = datetime.combine(c.Fecha, c.Hora).isoformat()
            except Exception:
                start = f"{c.Fecha}T{c.Hora}"  # fallback

            eventos.append({
                "id": f"cal-{c.ID_Calendario}",
                "title": f"{c.Tipo} - Pedido #{c.ID_Pedido}",
                "start": start,
                "location": c.Ubicacion or "Sin ubicación",
                "tipo": c.Tipo or "Evento",
                "usuario": nombre_usuario
            })

        # --- Pedidos con FechaEntrega o HoraLlegada ---
        pedidos = Pedido.query.filter(
            or_(
                Pedido.FechaEntrega.isnot(None),
                Pedido.HoraLlegada.isnot(None)
            )
        ).all()

        for p in pedidos:
            usuario = Usuario.query.get(p.ID_Usuario)
            nombre_usuario = f"{usuario.Nombre} {usuario.Apellido or ''}".strip() if usuario else "Desconocido"

            # Fecha y hora del evento
            fecha_evento = p.FechaEntrega or (p.HoraLlegada.date() if p.HoraLlegada else None)
            hora_evento = p.HoraLlegada.time() if p.HoraLlegada else time(12, 0)

            if fecha_evento:
                start = datetime.combine(fecha_evento, hora_evento).isoformat()
            else:
                continue  # saltar si no hay fecha

            tipo_evento = "Instalación" if getattr(p, "Instalacion", 0) == 1 else "Entrega"

            eventos.append({
                "id": f"pedido-{p.ID_Pedido}",
                "title": f"{tipo_evento} - Pedido #{p.ID_Pedido}",
                "start": start,
                "location": getattr(p, "Destino", "Sin dirección"),
                "tipo": tipo_evento,
                "usuario": nombre_usuario
            })

        return jsonify(eventos)

    except Exception as e:
        print("Error en /api/calendario:", e)
        return jsonify({"error": str(e)}), 500


@transportista.route('/calendario')
@login_required
@role_required("transportista")
def calendario():
    return render_template("transportista/calendario.html")


