from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, render_template_string
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from basedatos.models import db, Usuario, Notificaciones, Direccion, Calendario,Pedido, Producto, Resena
from basedatos.decoradores import role_required
from basedatos.notificaciones import crear_notificacion
from datetime import datetime
from flask import render_template
from sqlalchemy import text


favoritos_usuario = set() 

from . import cliente
reviews = []

# ---------- DASHBOARD ----------
@cliente.route("/dashboard")
@login_required
@role_required("cliente")
def dashboard():
    return render_template("cliente/dashboard.html")

# ---------- NOTIFICACIONES ----------
@cliente.route("/notificaciones", methods=["GET", "POST"])
@login_required
def ver_notificaciones_cliente():
    if request.method == "POST":
        ids = request.form.getlist("ids")
        if ids:
            try:
                Notificaciones.query.filter(
                    Notificaciones.ID_Usuario == current_user.ID_Usuario,
                    Notificaciones.ID_Notificacion.in_(ids)
                ).delete(synchronize_session=False)
                db.session.commit()
                flash("✅ Notificaciones eliminadas", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"❌ Error al eliminar: {str(e)}", "danger")
        return redirect(url_for("cliente.ver_notificaciones_cliente"))

    notificaciones = Notificaciones.query.filter_by(ID_Usuario=current_user.ID_Usuario).order_by(Notificaciones.Fecha.desc()).all()
    return render_template("cliente/notificaciones_cliente.html", notificaciones=notificaciones)


# ---------- PERFIL Y DIRECCIONES ----------
@cliente.route("/actualizacion_datos", methods=["GET", "POST"])
@login_required
@role_required("cliente","admin")
def actualizacion_datos():
    usuario = current_user
    direcciones = Direccion.query.filter_by(ID_Usuario=usuario.ID_Usuario).all()
    notificaciones = Notificaciones.query.filter_by(ID_Usuario=usuario.ID_Usuario).order_by(Notificaciones.Fecha.desc()).all()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        correo = request.form.get("correo", "").strip()
        password = request.form.get("password", "").strip()

        if not nombre or not apellido or not correo:
            flash("⚠️ Los campos Nombre, Apellido y Correo son obligatorios.", "warning")
        else:
            usuario_existente = Usuario.query.filter(
                Usuario.Correo == correo,
                Usuario.ID_Usuario != usuario.ID_Usuario
            ).first()
            if usuario_existente:
                flash("El correo ya está registrado por otro usuario.", "danger")
            else:
                usuario.Nombre = nombre
                usuario.Apellido = apellido
                usuario.Correo = correo
                if password:
                    usuario.Contraseña = generate_password_hash(password)
                db.session.commit()
                crear_notificacion(
                    user_id=usuario.ID_Usuario,
                    titulo="Perfil actualizado ✏️",
                    mensaje="Tus datos personales se han actualizado correctamente."
                )
                flash("✅ Perfil actualizado correctamente", "success")

    return render_template(
        "cliente/actualizacion_datos.html",
        usuario=usuario,
        direcciones=direcciones,
        notificaciones=notificaciones
    )

@cliente.route("/direccion/agregar", methods=["POST"])
@login_required
def agregar_direccion():
    try:
        nueva_direccion = Direccion(
            ID_Usuario=current_user.ID_Usuario,
            Pais="Colombia",
            Departamento="Bogotá, D.C.",
            Ciudad="Bogotá",
            Direccion=request.form.get("direccion"),
            InfoAdicional=request.form.get("infoAdicional"),
            Barrio=request.form.get("barrio"),
            Destinatario=request.form.get("destinatario")
        )
        db.session.add(nueva_direccion)
        db.session.commit()

        crear_notificacion(
            user_id=current_user.ID_Usuario,
            titulo="Dirección agregada 🏠",
            mensaje=f"Se ha agregado una nueva dirección: {nueva_direccion.Direccion}"
        )
        flash("Dirección agregada correctamente 🏠", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al agregar dirección: {str(e)}", "danger")

    return redirect(url_for("cliente.actualizacion_datos"))

@cliente.route("/direccion/borrar/<int:id_direccion>", methods=["POST"])
@login_required
def borrar_direccion(id_direccion):
    try:
        direccion = Direccion.query.get_or_404(id_direccion)
        db.session.delete(direccion)
        db.session.commit()

        crear_notificacion(
            user_id=current_user.ID_Usuario,
            titulo="Dirección eliminada 🗑️",
            mensaje=f"La dirección '{direccion.Direccion}' ha sido eliminada."
        )
        flash("Dirección eliminada correctamente 🗑️", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al eliminar dirección: {str(e)}", "danger")

    return redirect(url_for("cliente.actualizacion_datos"))


# ---------- AGENDAR_INSTALACION ----------

@cliente.route('/cliente/instalacion', methods=['GET', 'POST'])
@login_required
def agendar_instalacion():
    if request.method == 'POST':
        pedido_id = request.form.get('pedido_id')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        ubicacion = request.form.get('ubicacion')

        if not (pedido_id and fecha and hora and ubicacion):
            return jsonify({'success': False, 'message': 'Por favor completa todos los campos'}), 400

        nueva_cita = Calendario(
            Fecha=fecha,
            Hora=hora,
            Ubicacion=ubicacion,
            Tipo='Instalación',
            ID_Usuario=current_user.ID_Usuario,
            ID_Pedido=pedido_id
        )

        db.session.add(nueva_cita)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Instalación agendada exitosamente'})

    # GET
    pedidos = Pedido.query.filter_by(ID_Usuario=current_user.ID_Usuario).all()
    direcciones = Direccion.query.filter_by(ID_Usuario=current_user.ID_Usuario).all()

    return render_template('cliente/instalacion.html', pedidos=pedidos, direcciones=direcciones)

@cliente.route('/ver_instalaciones')
def ver_instalaciones():
    query = text("""
        SELECT 
            c.Fecha,
            c.Hora,
            c.Ubicacion,
            u.Nombre AS NombreUsuario
        FROM calendario c
        JOIN usuario u ON c.ID_Usuario = u.ID_Usuario
    """)

    result = db.session.execute(query)
    instalaciones = [dict(row) for row in result.mappings()] 

    return render_template("cliente/ver_instalaciones.html", instalaciones=instalaciones)



@cliente.route('/producto/<int:id>')
def detalle_producto(id):
    producto = Producto.query.get_or_404(id)
    return render_template('cliente/detalle_producto.html', producto=producto)


@cliente.route('/productos/<int:id>/resena', methods=['GET'])
@login_required
def escribir_resena(id):
    producto = Producto.query.get_or_404(id)
    return render_template('cliente/escribir_reseña.html', producto=producto)


@cliente.route('/productos/<int:id>/resena', methods=['POST'])
@login_required
def guardar_resena(id):
    producto = Producto.query.get_or_404(id)
    calificacion = int(request.form.get('calificacion'))
    comentario = request.form.get('comentario')

    if not (1 <= calificacion <= 5):
        flash('La calificación debe estar entre 1 y 5.', 'danger')
        return redirect(url_for('cliente/escribir_reseña', id=id))

    if not comentario:
        flash('El comentario no puede estar vacío.', 'danger')
        return redirect(url_for('cliente/escribir_reseña', id=id))

    nueva_resena = Resena(
        ID_Producto=id,
        ID_Usuario=current_user.ID_Usuario,
        Calificacion=calificacion,
        Comentario=comentario
    )
    db.session.add(nueva_resena)
    db.session.commit()
    flash('Reseña creada exitosamente.', 'success')
    return redirect(url_for('cliente.detalle_producto', id=id))  

@cliente.route('/comparar')
def comparar():
    # Obtener los IDs de la URL, pueden ser varios
    ids = request.args.getlist('ids')
    # Consultar los productos en la base de datos
    productos = Producto.query.filter(Producto.ID_Producto.in_(ids)).all()
    return render_template('comparar.html', productos=productos)