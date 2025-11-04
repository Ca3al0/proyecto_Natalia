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
from flask_login import current_user
from basedatos.models import db, Usuario,Pedido, RegistroFotografico,Calendario, Notificaciones
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


@transportista.route('/registro_fotografico', methods=['POST'])
@login_required
def registrar_fotografia_transportista():
    if current_user.Rol != 'transportista':
        return jsonify({'status': 'danger', 'message': 'No autorizado.'})

    try:
        pedido_id = request.form.get('pedido_id')
        tipo = request.form.get('tipo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        imagen = request.files.get('imagen')

        if not pedido_id or not imagen:
            return jsonify({'status': 'warning', 'message': 'Pedido e imagen son obligatorios.'})

        # Guardar imagen en carpeta estática
        carpeta = os.path.join('static', 'uploads', 'registros')
        os.makedirs(carpeta, exist_ok=True)
        nombre_archivo = secure_filename(imagen.filename)
        ruta_guardado = os.path.join(carpeta, nombre_archivo)
        imagen.save(ruta_guardado)

        # Crear registro en la DB
        registro = RegistroFotografico(
            pedido_id=int(pedido_id),
            usuario_id=current_user.ID_Usuario,  # transportista que sube la foto
            tipo=tipo,
            descripcion=descripcion,
            imagen_url=ruta_guardado
        )
        db.session.add(registro)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Foto registrada correctamente.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'danger', 'message': f'Error: {str(e)}'})
    
@transportista.route('/guardar_registro', methods=['POST'])
def guardar_registro():
    try:
        pedido_id = request.form.get('pedido_id')
        desc_antes = request.form.get('desc_antes')
        desc_despues = request.form.get('desc_despues')
        fotos_antes = request.files.getlist('fotos_antes')
        fotos_despues = request.files.getlist('fotos_despues')

        upload_folder = os.path.join(current_app.root_path, 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)

        for f in fotos_antes:
            filename = secure_filename(f.filename)
            f.save(os.path.join(upload_folder, filename))
            registro = RegistroFotografico(
                pedido_id=pedido_id,
                tipo='antes',
                descripcion=desc_antes,
                imagen_url=f'uploads/{filename}'
            )
            db.session.add(registro)

        for f in fotos_despues:
            filename = secure_filename(f.filename)
            f.save(os.path.join(upload_folder, filename))
            registro = RegistroFotografico(
                pedido_id=pedido_id,
                tipo='despues',
                descripcion=desc_despues,
                imagen_url=f'uploads/{filename}'
            )
            db.session.add(registro)

        db.session.commit()
        return jsonify({'status':'success'})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)})


@transportista.route('/registro_fotografico/<int:pedido_id>')
def get_registro_fotografico(pedido_id):
    registros = RegistroFotografico.query.filter_by(pedido_id=pedido_id).all()
    data = [{
        'tipo': r.tipo,
        'descripcion': r.descripcion,
        'imagen_url': r.imagen_url
    } for r in registros]
    return jsonify(data)

@transportista.route('/pedidos')
@login_required
@role_required('transportista')
def pedidos_transportista():
    
    pedidos = Pedido.query.filter(Pedido.Estado.in_(['pendiente', 'en proceso'])).all()
    return render_template('transportista/pedidos.html', pedidos=pedidos)

@transportista.route('/pedido/<int:pedido_id>/estado', methods=['POST'])
@login_required
def actualizar_estado_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    nuevo_estado = request.json.get('estado')

    if nuevo_estado not in ['pendiente', 'en proceso', 'en reparto', 'entregado']:
        return jsonify({'status': 'error', 'message': 'Estado no válido'}), 400

    pedido.Estado = nuevo_estado
    db.session.commit()

    # Crear notificación
    notificacion = Notificaciones(
        Titulo='Actualización de pedido',
        Mensaje=f'El estado de tu pedido #{pedido.ID_Pedido} cambió a "{nuevo_estado}".',
        ID_Usuario=pedido.ID_Usuario
    )
    db.session.add(notificacion)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Estado actualizado'})
