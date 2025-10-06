import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from flask import current_app
from basedatos.models import db, Usuario, Notificaciones, Direccion, Producto, Proveedor,Categorias,Resena
from werkzeug.security import generate_password_hash
from basedatos.decoradores import role_required
from basedatos.notificaciones import crear_notificacion
from werkzeug.utils import secure_filename
from sqlalchemy import func

reviews = []

admin = Blueprint("admin", __name__, url_prefix="/admin")

# ---------- DASHBOARD ----------
@admin.route("/")
@login_required
@role_required("admin")
def dashboard():
    return render_template("administrador/admin_dashboard.html")

# ---------- GESTION_ROLES ----------
@admin.route("/gestion_roles", methods=["GET", "POST"])
@login_required
@role_required("admin")
def gestion_roles():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        nuevo_rol = request.form.get("rol")

        usuario = Usuario.query.get(user_id)
        if not usuario:
            flash("❌ Usuario no encontrado", "danger")
            return redirect(url_for("admin.gestion_roles"))

        usuario.Rol = nuevo_rol
        db.session.commit()

        flash(f"✅ Rol de {usuario.Nombre} actualizado a {nuevo_rol}", "success")
        return redirect(url_for("admin.gestion_roles"))

    usuarios = Usuario.query.all()
    roles_disponibles = ["admin", "cliente", "instalador", "transportista"]
    return render_template("administrador/gestion_roles.html", usuarios=usuarios, roles=roles_disponibles)

# ---------- CAMBIAR_ROL ----------
@admin.route("/cambiar_rol/<int:user_id>", methods=["POST"])
@login_required
@role_required("admin")
def cambiar_rol(user_id):
    nuevo_rol = request.form["rol"]
    usuario = Usuario.query.get(user_id)

    if usuario:
        usuario.Rol = nuevo_rol
        db.session.commit()
        flash(f"✅ Rol de {usuario.Nombre} cambiado a {nuevo_rol}", "success")
    else:
        flash("❌ Usuario no encontrado", "danger")

    return redirect(url_for("admin.gestion_roles"))

# ---------- NOTIFICACIONES ----------
@admin.route("/notificaciones", methods=["GET", "POST"])
@login_required
@role_required("admin")
def ver_notificaciones():
    if request.method == "POST":
        ids = request.form.getlist("ids")
        if not ids:
            flash("❌ No seleccionaste ninguna notificación", "warning")
            return redirect(url_for("admin.ver_notificaciones"))

        try:
            ids_int = [int(i) for i in ids if str(i).isdigit()]
            Notificaciones.query.filter(
                Notificaciones.ID_Usuario == current_user.ID_Usuario,
                Notificaciones.ID_Notificacion.in_(ids_int),
            ).delete(synchronize_session=False)
            db.session.commit()
            flash("✅ Notificaciones eliminadas", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error al eliminar: {e}", "danger")

        return redirect(url_for("admin.ver_notificaciones"))

    notificaciones = Notificaciones.query.filter_by(
        ID_Usuario=current_user.ID_Usuario
    ).order_by(Notificaciones.Fecha.desc()).all()

    return render_template("administrador/notificaciones_admin.html", notificaciones=notificaciones)

# ---------- ACTUALIZACION_DATOS ----------
@admin.route("/actualizacion_datos", methods=["GET", "POST"])
@login_required
@role_required("admin")
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
            # Verificar si el correo ya existe para otro usuario
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

                try:
                    db.session.commit()
                    crear_notificacion(
                        user_id=usuario.ID_Usuario,
                        titulo="Perfil actualizado ✏️",
                        mensaje="Tus datos personales se han actualizado correctamente."
                    )
                    flash("✅ Perfil actualizado correctamente", "success")
                except Exception as e:
                    db.session.rollback()
                    flash(f"❌ Error al actualizar perfil: {str(e)}", "danger")

    return render_template(
        "administrador/admin_actualizacion_datos.html",
        usuario=usuario,
        direcciones=direcciones,
        notificaciones=notificaciones
    )


# ---------- AGREGAR DIRECCION ----------
@admin.route("/direccion/agregar", methods=["POST"])
@login_required
def agregar_direccion():
    try:
        direccion_valor = request.form.get("direccion", "").strip()
        if not direccion_valor:
            flash("⚠️ La dirección es obligatoria.", "warning")
            return redirect(url_for("admin.actualizacion_datos"))

        nueva_direccion = Direccion(
            ID_Usuario=current_user.ID_Usuario,
            Pais="Colombia",
            Departamento="Bogotá, D.C.",
            Ciudad="Bogotá",
            Direccion=direccion_valor,
            InfoAdicional=request.form.get("infoAdicional", "").strip(),
            Barrio=request.form.get("barrio", "").strip(),
            Destinatario=request.form.get("destinatario", "").strip()
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

    return redirect(url_for("admin.actualizacion_datos"))


# ---------- BORRAR DIRECCION ----------
@admin.route("/direccion/borrar/<int:id_direccion>", methods=["POST"])
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

    return redirect(url_for("admin.actualizacion_datos"))



# ---------- AGREGAR PRODUCTO ----------

@admin.route('/admin/agregar-producto', methods=['GET', 'POST'])
def agregar_producto():
    proveedores = Proveedor.query.all()
    categorias = Categorias.query.all()

    if request.method == 'POST':
        nombre = request.form['nombre']
        stock = int(request.form['stock'])
        material = request.form['material']
        precio = float(request.form['precio'])
        color = request.form['color']
        id_proveedor = int(request.form['proveedor'])
        id_categoria = int(request.form['categoria'])

        # Manejo seguro de imagen
        imagen = request.files.get('imagen_principal')  # evita KeyError
        imagen_ruta = 'img/default.png'  # Valor por defecto

        if imagen and imagen.filename != '':
            filename = secure_filename(imagen.filename)
            ruta_img = os.path.join(current_app.static_folder, 'img', filename)

            # Guardar imagen en /static/img/
            imagen.save(ruta_img)

            imagen_ruta = f'img/{filename}'

        # Crear nuevo producto
        nuevo = Producto(
            NombreProducto=nombre,
            Stock=stock,
            Material=material,
            PrecioUnidad=precio,
            Color=color,
            ID_Proveedor=id_proveedor,
            ID_Categoria=id_categoria,
            ImagenPrincipal=imagen_ruta
        )

        db.session.add(nuevo)
        db.session.commit()
        flash('Producto agregado con éxito', 'success')
        return redirect(url_for('admin.agregar_producto'))

    return render_template('administrador/agregar_producto.html', proveedores=proveedores, categorias=categorias)



@admin.route('/resenas')
@login_required
def ver_resenas():
    productos = db.session.query(Producto).all()
    return render_template('administrador/ver_reseñas.html', productos=productos)


@admin.route('/estadisticas')
@login_required
def estadisticas_reseñas():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    canal = request.args.get('canal', 'todos')
    segmento = request.args.get('segmento', 'todos')

    query = Resena.query

    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            query = query.filter(Resena.Fecha >= fecha_inicio_dt)
        except:
            pass

    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
            query = query.filter(Resena.Fecha <= fecha_fin_dt)
        except:
            pass

    if canal != 'todos':
        query = query.filter(Resena.canal == canal)

    if segmento != 'todos':
        query = query.filter(Resena.segmento_cliente == segmento)

    reseñas_filtradas = query.all()

    # Calcular distribución de calificaciones
    rating_distribution = {str(i): 0 for i in range(1, 6)}
    total_respuestas = len(reseñas_filtradas)
    respuestas_positivas = 0
    comentarios_negativos_por_producto = {}

    for r in reseñas_filtradas:
        cal = r.Calificacion
        rating_distribution[str(cal)] += 1
        if cal >= 4:
            respuestas_positivas += 1
        elif cal <= 2:
            nombre_producto = r.producto.NombreProducto
            comentarios_negativos_por_producto[nombre_producto] = comentarios_negativos_por_producto.get(nombre_producto, 0) + 1

    porcentaje_positivas = round((respuestas_positivas / total_respuestas) * 100, 2) if total_respuestas else 0

    # Datos de productos
    productos_data = []
    productos = Producto.query.all()

    for producto in productos:
        reseñas_producto = [r for r in reseñas_filtradas if r.ID_Producto == producto.ID_Producto]
        if reseñas_producto:
            suma = sum(r.Calificacion for r in reseñas_producto)
            cantidad = len(reseñas_producto)
            promedio = round(suma / cantidad, 2)
            productos_data.append({
                'nombre': producto.NombreProducto,
                'promedio': promedio,
                'cantidad': cantidad
            })

    # Compras por mes - ejemplo, adapta según modelo real
    from sqlalchemy import func
    compras_por_mes = (
        db.session.query(
            func.date_format(Resena.Fecha, "%Y-%m").label("mes"),
            func.count(Resena.ID_Resena)
        )
        .filter(Resena.ID_Resena.in_([r.ID_Resena for r in reseñas_filtradas]))
        .group_by("mes")
        .order_by("mes")
        .all()
    )

    # Simulación de resolución de problemas - reemplaza con datos reales si tienes
    resolucion_por_mes = {
        "2023-05": 12,
        "2023-06": 17,
        "2023-07": 14,
        "2023-08": 19,
        "2023-09": 21,
    }

    return render_template('administrador/estadisticas.html',
        filtros={
            "fecha_inicio": fecha_inicio or '',
            "fecha_fin": fecha_fin or '',
            "canal": canal,
            "segmento": segmento
        },
        total_respuestas=total_respuestas,
        porcentaje_positivas=porcentaje_positivas,
        distribucion_json=json.dumps(rating_distribution),
        comentarios_negativos=comentarios_negativos_por_producto,
        productos=productos_data,
        compras_por_mes=compras_por_mes,
        resolucion_json=json.dumps(resolucion_por_mes)
    )

@admin.route('/administrar_proveedores')
def index():
    return render_template('administrador/compras.html')

# ----------------------------------------------------------
# 🟢 PANEL PRINCIPAL DEL ADMIN (Vista de proveedores)
# ----------------------------------------------------------
@admin.route('/proveedores', methods=['GET'])
def vista_proveedores():
    proveedores = Proveedor.query.all()
    return render_template('administrador/proveedores.html', proveedores=proveedores)


# ----------------------------------------------------------
# 🟢 API: Obtener todos los proveedores (JSON)
# ----------------------------------------------------------
@admin.route('/api/proveedores', methods=['GET'])
def obtener_proveedores():
    proveedores = Proveedor.query.all()
    data = [
        {
            "id": p.ID_Proveedor,
            "empresa": p.NombreEmpresa,
            "contacto": p.NombreContacto,
            "telefono": p.Telefono,
            "pais": p.Pais,
            "cargo": p.CargoContacto,
            "cantidad": p.Cantidad,
            "precio": float(p.Precio_Unitario or 0),
            "ciudad": p.Ciudad,
            "direccion": p.Direccion
        }
        for p in proveedores
    ]
    return jsonify(data)


# ----------------------------------------------------------
# 🟢 API: Agregar un nuevo proveedor
# ----------------------------------------------------------
@admin.route('/api/proveedores', methods=['POST'])
def agregar_proveedor():
    data = request.get_json()
    nuevo = Proveedor(
        NombreEmpresa=data.get('empresa'),
        NombreContacto=data.get('contacto'),
        Telefono=data.get('telefono'),
        Pais=data.get('pais'),
        CargoContacto=data.get('cargo'),
        Cantidad=data.get('cantidad'),
        Precio_Unitario=data.get('precio'),
        Ciudad=data.get('ciudad'),
        Direccion=data.get('direccion')
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"mensaje": "Proveedor agregado correctamente"}), 201


# ----------------------------------------------------------
# 🟡 API: Editar proveedor existente
# ----------------------------------------------------------
@admin.route('/api/proveedores/<int:id>', methods=['PUT'])
def editar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    data = request.get_json()

    proveedor.NombreEmpresa = data.get('empresa', proveedor.NombreEmpresa)
    proveedor.NombreContacto = data.get('contacto', proveedor.NombreContacto)
    proveedor.Telefono = data.get('telefono', proveedor.Telefono)
    proveedor.Pais = data.get('pais', proveedor.Pais)
    proveedor.CargoContacto = data.get('cargo', proveedor.CargoContacto)
    proveedor.Cantidad = data.get('cantidad', proveedor.Cantidad)
    proveedor.Precio_Unitario = data.get('precio', proveedor.Precio_Unitario)
    proveedor.Ciudad = data.get('ciudad', proveedor.Ciudad)
    proveedor.Direccion = data.get('direccion', proveedor.Direccion)

    db.session.commit()
    return jsonify({"mensaje": "Proveedor actualizado correctamente"})


# ----------------------------------------------------------
# 🔴 API: Eliminar proveedor
# ----------------------------------------------------------
@admin.route('/api/proveedores/<int:id>', methods=['DELETE'])
def eliminar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    db.session.delete(proveedor)
    db.session.commit()
    return jsonify({"mensaje": "Proveedor eliminado"}), 200