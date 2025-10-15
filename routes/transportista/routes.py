from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from basedatos.models import db, Calendario,Pedido
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

    calendarios = Calendario.query.all()
    for c in calendarios:
        eventos.append({
            "title": f"{c.Tipo.title()} - Pedido #{c.ID_Pedido}" if c.ID_Pedido else c.Tipo.title(),
            "start": f"{c.Fecha}T{c.Hora}",
            "location": c.Ubicacion,
            "tipo": c.Tipo,
            "id": f"cal-{c.ID_Calendario}"
        })

    
    pedidos = Pedido.query.filter(Pedido.FechaEntrega != None).all()
    ids_en_calendario = set(c.ID_Pedido for c in calendarios if c.ID_Pedido is not None)

    for p in pedidos:
        if p.ID_Pedido not in ids_en_calendario:
            eventos.append({
                "title": f"Entrega pendiente - Pedido #{p.ID_Pedido}",
                "start": f"{p.FechaEntrega}T{p.HoraLlegada.time() if p.HoraLlegada else '12:00:00'}",
                "location": p.Destino,
                "tipo": "entrega",
                "id": f"pedido-{p.ID_Pedido}"
            })

    return jsonify(eventos)


@transportista.route('/calendario')
@login_required
@role_required("transportista")
def calendario():
    return render_template("transportista/calendario.html")