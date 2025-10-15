from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from basedatos.models import db, Calendario,Pedido, Usuario
from basedatos.decoradores import role_required



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
        nombre_usuario = f"{usuario.Nombre} {usuario.Apellido or ''}" if usuario else "Desconocido"

        eventos.append({
            "id": f"cal-{c.ID_Calendario}",
            "title": f"{c.Tipo} - Pedido #{c.ID_Pedido}",
            "start": f"{c.Fecha}T{c.Hora}",
            "location": c.Ubicacion,
            "tipo": c.Tipo,
            "usuario": nombre_usuario
        })

    # Obtener pedidos con fecha de entrega no asociados al calendario
    pedidos_con_fecha = Pedido.query.filter(Pedido.FechaEntrega != None).all()
    ids_en_calendario = {c.ID_Pedido for c in calendarios if c.ID_Pedido is not None}

    for p in pedidos_con_fecha:
        if p.ID_Pedido not in ids_en_calendario:
            usuario = Usuario.query.get(p.ID_Usuario)
            nombre_usuario = f"{usuario.Nombre} {usuario.Apellido or ''}" if usuario else "Desconocido"

            hora = p.HoraLlegada.strftime("%H:%M:%S") if p.HoraLlegada else "12:00:00"

            eventos.append({
                "id": f"pedido-{p.ID_Pedido}",
                "title": f"Entrega - Pedido #{p.ID_Pedido}",
                "start": f"{p.FechaEntrega}T{hora}",
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