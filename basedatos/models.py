from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, CheckConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import date
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()

db = SQLAlchemy()

# ------------------ Usuario ------------------
class Usuario(UserMixin, db.Model):
    __tablename__ = 'Usuario'

    ID_Usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Apellido = db.Column(db.String(100))
    Genero = db.Column(db.String(10))
    Telefono = db.Column(db.String(20))
    Correo = db.Column(db.String(100), nullable=False, unique=True)
    Contraseña = db.Column(db.String(200), nullable=False)
    Rol = db.Column(db.String(50), default='cliente')
    Activo = db.Column(db.Boolean, default=True)

    # Relaciones
    calendarios = db.relationship('Calendario', backref='usuario', lazy=True)
    notificaciones = db.relationship('Notificaciones', backref='usuario', lazy=True)
    novedades = db.relationship('Novedades', backref='usuario', lazy=True)
    pedidos = db.relationship('Pedido', backref='usuario', lazy=True, foreign_keys='Pedido.ID_Usuario')
    pedidos_asignados = db.relationship('Pedido', backref='empleado', lazy=True, foreign_keys='Pedido.ID_Empleado')
    direcciones = db.relationship('Direccion', backref='usuario', lazy=True, cascade="all, delete-orphan")
    resenas = db.relationship('Resena', back_populates='usuario', lazy=True)

    def get_id(self):
        return str(self.ID_Usuario)

    @property
    def id(self):
        return self.ID_Usuario

    def __repr__(self):
        return f'<Usuario {self.Nombre} {self.Apellido or ""}>'

# ------------------ Direccion ------------------
class Direccion(db.Model):
    __tablename__ = 'Direccion'

    ID_Direccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_Usuario', ondelete="CASCADE"), nullable=False)
    Pais = db.Column(db.String(100), default="Colombia")
    Departamento = db.Column(db.String(100))
    Ciudad = db.Column(db.String(100))
    Direccion = db.Column(db.String(200), nullable=False)
    InfoAdicional = db.Column(db.String(200))
    Barrio = db.Column(db.String(100))
    Destinatario = db.Column(db.String(100))

# ------------------ Proveedor ------------------
class Proveedor(db.Model):
    __tablename__ = 'Proveedor'

    ID_Proveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NombreEmpresa = db.Column(db.String(100), nullable=False)
    NombreContacto = db.Column(db.String(100))
    Telefono = db.Column(db.String(20))
    Pais = db.Column(db.String(50))
    CargoContacto = db.Column(db.String(50))
    Ciudad = db.Column(db.String(100))
    Direccion = db.Column(db.String(200))

    productos = db.relationship('Producto', back_populates='proveedor', lazy=True)
    compras = db.relationship('Compra', back_populates='proveedor', lazy=True)

    def __repr__(self):
        return f'<Proveedor {self.NombreEmpresa} - {self.Ciudad}>'

# ------------------ Categorias ------------------
class Categorias(db.Model):
    __tablename__ = 'Categorias'

    ID_Categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NombreCategoria = db.Column(db.String(100), nullable=False)
    Descripcion = db.Column(db.Text)

    productos = db.relationship('Producto', back_populates='categoria', lazy=True)

# ------------------ Producto ------------------
class Producto(db.Model):
    __tablename__ = 'Producto'

    ID_Producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NombreProducto = db.Column(db.String(100), nullable=False)
    Stock = db.Column(db.Integer, nullable=False)
    Material = db.Column(db.String(50))
    PrecioUnidad = db.Column(db.Float, nullable=False)
    Color = db.Column(db.String(30))
    Descripcion = db.Column(db.Text)
    ImagenPrincipal = db.Column(db.String(200))  
    ID_Proveedor = db.Column(db.Integer, db.ForeignKey('Proveedor.ID_Proveedor'), nullable=False)
    ID_Categoria = db.Column(db.Integer, db.ForeignKey('Categorias.ID_Categoria'))

    Comentario = db.Column(db.Text)  # Nuevo campo
    Calificacion = db.Column(db.Integer)  # Nuevo campo

    proveedor = db.relationship('Proveedor', back_populates='productos')
    categoria = db.relationship('Categorias', back_populates='productos')
    imagenes = db.relationship('ImagenProducto', backref='producto', lazy=True)
    novedades = db.relationship('Novedades', backref='producto', lazy=True)
    detalles_pedido = db.relationship('Detalle_Pedido', backref='producto', lazy=True)
    resenas = db.relationship('Resena', back_populates='producto', lazy=True)


# ------------------ ImagenProducto ------------------
class ImagenProducto(db.Model):
    __tablename__ = 'ImagenProducto'

    ID_Imagen = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ruta = db.Column(db.String(200), nullable=False)
    ID_Producto = db.Column(db.Integer, db.ForeignKey('Producto.ID_Producto'), nullable=False)

# ------------------ Calendario ------------------
class Calendario(db.Model):
    __tablename__ = 'Calendario'

    ID_Calendario = db.Column(db.Integer, primary_key=True)
    Fecha = db.Column(db.Date, nullable=False)
    Hora = db.Column(db.Time, nullable=False)
    Ubicacion = db.Column(db.String(255), nullable=False)
    Tipo = db.Column(db.String(50), nullable=False)

    ID_Usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_Usuario'), nullable=False)
    ID_Pedido = db.Column(db.Integer, db.ForeignKey('Pedido.ID_Pedido'), nullable=True)

# ------------------ Notificaciones ------------------
class Notificaciones(db.Model):
    __tablename__ = 'Notificaciones'

    ID_Notificacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Titulo = db.Column(db.String(200), nullable=False)
    Mensaje = db.Column(db.Text, nullable=False)
    Fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
    Leida = db.Column(db.Boolean, default=False)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_Usuario'), nullable=False)

# ------------------ Novedades ------------------
class Novedades(db.Model):
    __tablename__ = 'Novedades'

    ID_Novedad = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Tipo = db.Column(db.String(50))
    EstadoNovedad = db.Column(db.String(50))
    FechaReporte = db.Column(db.Date)

    ID_Usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_Usuario'), nullable=False)
    ID_Producto = db.Column(db.Integer, db.ForeignKey('Producto.ID_Producto'), nullable=False)

# ------------------ Pedido ------------------
from datetime import datetime

class Pedido(db.Model):
    __tablename__ = 'Pedido'

    ID_Pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NombreComprador = db.Column(db.String(100))
    Estado = db.Column(db.Enum('pendiente', 'en proceso', 'en reparto', 'entregado'))
    FechaPedido = db.Column(db.Date)
    FechaEntrega = db.Column(db.Date)
    Destino = db.Column(db.String(200))
    Descuento = db.Column(db.Float)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_Usuario'), nullable=False)

   
    ID_Empleado = db.Column(db.Integer, db.ForeignKey('Usuario.ID_Usuario'))

    HoraLlegada = db.Column(db.DateTime)

    pagos = db.relationship('Pagos', backref='pedido', lazy=True)
    detalles_pedido = db.relationship('Detalle_Pedido', backref='pedido', lazy=True)
    firmas = db.relationship('Firmas', backref='pedido', lazy=True)
    comentarios = db.relationship('Comentarios', backref='pedido', lazy=True)
    calendario = db.relationship('Calendario', backref='pedido', lazy=True)

# ------------------ Pagos ------------------
class Pagos(db.Model):
    __tablename__ = 'Pagos'

    ID_Pagos = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MetodoPago = db.Column(db.String(50))
    FechaPago = db.Column(db.Date)
    Monto = db.Column(db.Float)
    ID_Pedido = db.Column(db.Integer, db.ForeignKey('Pedido.ID_Pedido'), nullable=False)

# ------------------ Detalle Pedido ------------------
class Detalle_Pedido(db.Model):
    __tablename__ = 'Detalle_Pedido'

    ID_Pedido = db.Column(db.Integer, db.ForeignKey('Pedido.ID_Pedido'), primary_key=True)
    ID_Producto = db.Column(db.Integer, db.ForeignKey('Producto.ID_Producto'), primary_key=True)
    Cantidad = db.Column(db.Integer)
    PrecioUnidad = db.Column(db.Float)

   
    producto = db.relationship('Producto', backref='detalles_pedido')

    @property
    def subtotal(self):
        return self.Cantidad * self.PrecioUnidad
# ------------------ Firmas ------------------
class Firmas(db.Model):
    __tablename__ = 'Firmas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('Pedido.ID_Pedido'), nullable=False)
    nombre_cliente = db.Column(db.String(100), nullable=False)
    firma = db.Column(db.Text, nullable=False)
    fecha_firma = db.Column(db.DateTime, default=db.func.current_timestamp())

# ------------------ Comentarios ------------------
class Comentarios(db.Model):
    __tablename__ = 'Comentarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('Pedido.ID_Pedido', ondelete="CASCADE"), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())

# ------------------ Reseñas ------------------

class Resena(db.Model):
    __tablename__ = 'Resena'  

    ID_Resena = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Producto = db.Column(db.Integer, db.ForeignKey('Producto.ID_Producto'), nullable=False)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_Usuario'), nullable=False)
    Calificacion = db.Column(db.Integer, nullable=False)
    Comentario = db.Column(db.Text, nullable=False)
    Fecha = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    producto = db.relationship("Producto", back_populates="resenas")
    usuario = db.relationship("Usuario", back_populates="resenas")

    __table_args__ = (
        CheckConstraint('Calificacion >= 1 AND Calificacion <= 5', name='check_calificacion_range'),
    )

# ------------------ Compras ------------------

class Compra(db.Model):
    __tablename__ = 'Compra'

    ID_Compra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Producto = db.Column(db.String(100), nullable=False)
    Cantidad = db.Column(db.Integer, nullable=False)
    Fecha = db.Column(db.Date, nullable=False, default=date.today)
    ProveedorID = db.Column(db.Integer, db.ForeignKey('Proveedor.ID_Proveedor'), nullable=False)

    proveedor = db.relationship('Proveedor', back_populates='compras')

    def __repr__(self):
        return f'<Compra {self.Producto} - {self.Cantidad} unidades>'