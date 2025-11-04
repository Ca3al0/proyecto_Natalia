from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_login import login_required, login_user, logout_user
from basedatos.models import db, Usuario
from basedatos.decoradores import validar_password, validar_email, send_reset_email
from basedatos.notificaciones import crear_notificacion
from . import auth

# Serializador de tokens
s = URLSafeTimedSerializer("mi_clave_super_secreta_y_unica")

# ------------------ REGISTRO ------------------ #
@auth.route('/register', methods=['POST'])
def register():
    nombre_completo = request.form.get('name', '').strip()
    correo = request.form.get('email', '').strip().lower()  # 👈 corrección aquí
    telefono = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()

    if not nombre_completo or not correo or not password:
        return jsonify({'status': 'warning', 'message': 'Nombre, correo y contraseña son obligatorios.'})

    if not validar_email(correo):
        return jsonify({'status': 'danger', 'message': 'Correo inválido.'})

    error = validar_password(password)
    if error:
        return jsonify({'status': 'danger', 'message': error})

    if Usuario.query.filter_by(Correo=correo).first():
        return jsonify({'status': 'danger', 'message': 'Correo ya registrado.'})

    nombre, apellido = (nombre_completo.split(" ", 1) + [""])[:2]

    try:
        nuevo_usuario = Usuario(
            Nombre=nombre,
            Apellido=apellido,
            Telefono=telefono,
            Correo=correo,
            Contraseña=generate_password_hash(password),
            Rol="cliente"
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        crear_notificacion(
            user_id=nuevo_usuario.ID_Usuario,
            titulo="¡Bienvenido!",
            mensaje="Tu cuenta se ha creado correctamente."
        )

        return jsonify({'status': 'success', 'message': 'Cuenta creada correctamente. Ahora puedes iniciar sesión.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'danger', 'message': f'Error al registrar: {str(e)}'})


# ------------------ LOGIN ------------------ #
@auth.route('/login', methods=['POST'])
def login():
    correo = request.form.get('correo', '').strip()
    password = request.form.get('password', '').strip()

    usuario = Usuario.query.filter_by(Correo=correo).first()

    if usuario and check_password_hash(usuario.Contraseña, password):
        login_user(usuario)
        session['username'] = f"{usuario.Nombre} {usuario.Apellido or ''}".strip()

        rutas_por_rol = {
            'admin': 'admin.dashboard',
            'cliente': 'cliente.dashboard',
            'transportista': 'transportista.dashboard',
            'instalador': 'instalador.dashboard'
        }
        destino = rutas_por_rol.get(usuario.Rol, 'index')

        return jsonify({'status': 'success', 'message': 'Inicio de sesión exitoso.', 'redirect': url_for(destino)})

    return jsonify({'status': 'danger', 'message': 'Correo o contraseña incorrectos.'})


# ------------------ LOGOUT ------------------ #
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('index'))


# ------------------ OLVIDÉ CONTRASEÑA ------------------ #
@auth.route('/forgot_password', methods=['POST'])
def forgot_password():
    email = request.form.get("email")
    user = Usuario.query.filter_by(Correo=email).first()

    if not user:
        return jsonify({'status': 'warning', 'message': 'Correo no registrado.'})

    try:
        token = s.dumps(email, salt='password-recovery')
        send_reset_email(user_email=email, user_name=user.Nombre, token=token)
        # Mensaje para interfaz + borrado del campo vía JS
        return jsonify({'status': 'success', 'message': 'Correo enviado para restablecer contraseña. El campo se limpiará.'})
    except Exception as e:
        return jsonify({'status': 'danger', 'message': f'Error al enviar correo: {str(e)}'})


# ------------------ RESTABLECER CONTRASEÑA ------------------ #
@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        try:
            email = s.loads(token, salt='password-recovery', max_age=3600)
            return render_template('common/index.html', token=token, mostrar_modal_reset=True, token_expirado=False)
        except (SignatureExpired, BadSignature):
            return render_template('common/index.html', mostrar_modal_reset=False, token_expirado=True, token=None)

    # Si el método es POST
    try:
        email = s.loads(token, salt='password-recovery', max_age=3600)
    except (SignatureExpired, BadSignature):
        return jsonify({'status': 'danger', 'message': 'Enlace inválido o expirado.'})

    new_password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not new_password or not confirm_password:
        return jsonify({'status': 'warning', 'message': 'Completa ambos campos.'})
    if new_password != confirm_password:
        return jsonify({'status': 'warning', 'message': 'Las contraseñas no coinciden.'})

    error = validar_password(new_password)
    if error:
        return jsonify({'status': 'warning', 'message': error})

    user = Usuario.query.filter_by(Correo=email).first()
    if not user:
        return jsonify({'status': 'danger', 'message': 'Usuario no encontrado.'})

    user.Contraseña = generate_password_hash(new_password)
    db.session.commit()

    crear_notificacion(
        user_id=user.ID_Usuario,
        titulo="Contraseña actualizada",
        mensaje="Tu contraseña ha sido cambiada exitosamente."
    )

    # Redirige con mensaje flash
    flash('Contraseña restablecida correctamente. Ahora puedes iniciar sesión.', 'success')
    return jsonify({'status': 'success', 'redirect': url_for('index')})
