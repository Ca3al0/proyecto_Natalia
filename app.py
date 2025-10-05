import os
from flask import Flask, render_template, session, redirect, request, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# ------------------ MODELOS ------------------ #
from basedatos.models import db, Usuario, Producto

# ------------------ EXTENSIONES ------------------ #
from basedatos.decoradores import mail

# ------------------ BLUEPRINTS ------------------ #
from routes.auth import auth
from routes.cliente import cliente
from routes.administrador import admin

# ------------------ APP ------------------ #
app = Flask(__name__)

# ------------------ CONFIGURACIÓN PRINCIPAL ------------------ #
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY", "mi_clave_super_secreta_y_unica"),
    SQLALCHEMY_DATABASE_URI=os.getenv(
        "DATABASE_URI", "mysql+pymysql://root:2426@127.0.0.1:3306/Tienda_db"
    ),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
)

# ------------------ CONFIGURACIÓN MAIL ------------------ #
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "casaenelarbol236@gmail.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "usygdligtlewedju"),
    MAIL_DEFAULT_SENDER=("Casa en el Árbol", os.getenv("MAIL_USERNAME", "casaenelarbol236@gmail.com")),
)
mail.init_app(app)

# ------------------ DB ------------------ #
db.init_app(app)

# ------------------ FLASK LOGIN ------------------ #
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Debes iniciar sesión para acceder a esta página."
login_manager.login_message_category = "warning"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    try:
        return Usuario.query.get(int(user_id))
    except Exception as e:
        print(f"⚠️ Error cargando usuario: {e}")
        return None

# ------------------ REGISTRO DE BLUEPRINTS ------------------ #
app.register_blueprint(auth)
app.register_blueprint(cliente)
app.register_blueprint(admin)

# ------------------ RUTAS PÚBLICAS ------------------ #
@app.route("/")
def index():
    return render_template("common/index.html")

@app.route("/nosotros")
def nosotros():
    return render_template("common/nosotros.html")

@app.route("/catalogo")
def catalogo():
    productos = Producto.query.all()
    return render_template("common/catalogo.html", productos=productos)

@app.route("/favoritos", methods=["POST"])
def favoritos():
    data = request.get_json()
    ids = data.get("ids", [])
    if not ids:
        return jsonify({"html": "<p>No tienes productos favoritos.</p>"})
    productos = Producto.query.filter(Producto.ID_Producto.in_(ids)).all()
    html = render_template("cliente/lista_favoritos.html", productos=productos)
    return jsonify({"html": html})

# Inicializar carrito en session si no existe
def obtener_carrito():
    return session.get('carrito', [])

def guardar_carrito(carrito):
    session['carrito'] = carrito
    session.modified = True


@app.route('/carrito', methods=['GET', 'POST'])
def carrito():
    if request.method == 'POST':
        try:
            data = request.get_json() or {}
            ids = data.get('ids', [])
            ids = [int(i) for i in ids if str(i).isdigit()]
            productos = Producto.query.filter(Producto.ID_Producto.in_(ids)).all() if ids else []

            for p in productos:
                p.cantidad = 1
                p.subtotal = p.PrecioUnidad * p.cantidad

            total = sum(p.subtotal for p in productos)
            html = render_template('cliente/productos_carrito_modal.html', productos=productos, total=total)
            return jsonify({'html': html})
        except Exception as e:
            print("Error POST /carrito:", e)
            return jsonify({'html': '<p>Error al cargar el carrito.</p>'})
    else:
        # GET
        carrito_session = session.get('carrito', [])
        productos = Producto.query.filter(Producto.ID_Producto.in_(carrito_session)).all() if carrito_session else []
        total = sum(p.PrecioUnidad for p in productos)
        return render_template('cliente/ver_carrito.html', productos=productos, total=total)

@app.route('/agregar_carrito/<int:id>')
def agregar_carrito(id):
    carrito = session.get('carrito', {})

    if not isinstance(carrito, dict):
        carrito = {}

    # Incrementar cantidad
    if str(id) in carrito:
        carrito[str(id)] += 1
    else:
        carrito[str(id)] = 1

    session['carrito'] = carrito
    flash('Producto agregado al carrito', 'success')
    return redirect(request.referrer or url_for('index'))


# Eliminar producto
@app.route("/carrito/eliminar/<int:id>")
def eliminar_carrito(id):
    carrito = session.get("carrito", [])
    carrito = [pid for pid in carrito if pid != id]
    session["carrito"] = carrito
    return redirect(url_for("carrito"))

# Cambiar cantidad
@app.route("/carrito/cambiar/<int:id>/<accion>")
def cambiar_cantidad(id, accion):
    carrito = session.get("carrito", [])
    if accion == "sumar":
        carrito.append(id)
    elif accion == "restar":
        if id in carrito:
            carrito.remove(id)
    session["carrito"] = carrito
    return redirect(url_for("carrito"))

# ------------------ TEMPLATE FILTER ------------------ #
@app.template_filter("dict_get")
def dict_get(d, key):
    return d.get(int(key), 0)

# ------------------ DEBUG: MOSTRAR RUTAS ------------------ #
with app.app_context():
    print("\n🔗 RUTAS REGISTRADAS:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:35s} -> {rule}")
    print("-----------------------------\n")

# ------------------ MAIN ------------------ #
if __name__ == "__main__":
    app.run(debug=True)
