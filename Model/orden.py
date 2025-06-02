from . import db
from sqlalchemy import Enum


class orden(db.Model):
    __tablename__ = 'orden'
    idOrden = db.Column(db.Integer, primary_key=True)
    idUbicacion = db.Column(db.Integer, db.ForeignKey('ubicacion.idUbicacion'), nullable=False)

    # Foreign key to the user who created the order
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)

    # Foreign key to the worker who will handle the order
    idWorker = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'),
                         nullable=True)  # nullable=True because it may be assigned later

    estado = db.Column(Enum('pendiente', 'cancelado', 'completado', 'aceptado', name='estado_enum'), nullable=False,
                       default='pendiente')
    nombre = db.Column(db.String(255), nullable=False)
    ruc = db.Column(db.String(11), nullable=False)
    celular = db.Column(db.String(15), nullable=False)
    biometria = db.Column(db.String(50), nullable=True)
    direccion = db.Column(db.String(255), nullable=False)
    region=db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(100), nullable=False)
    distrito = db.Column(db.String(100), nullable=False)
    referencia = db.Column(db.String(255), nullable=True)
    recarga = db.Column(db.String(3), nullable=False)
    tarjeta = db.Column(db.String(3), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    chipInicio = db.Column(db.String(50), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    chipFinal = db.Column(db.String(50), nullable=False)
    comprobante = db.Column(db.String(50), nullable=False)
    importeCobrado = db.Column(db.Float, nullable=False)
    dni=db.Column(db.String(8),nullable=False)
    txt_generado = db.Column(db.Boolean, default=False)
    motivo=db.Column(db.String(255), nullable=False)
    tipo_negocio = db.Column(db.String(50), nullable=True)  # PUESTO MERCADO / QUIOSCO / BODEGA / OTROS
    activacion = db.Column(db.String(20), nullable=True)    # CAMARA / BIOMETRIA
    codigo_lector = db.Column(db.String(50), nullable=True) # Solo si activación es BIOMETRÍA
    id_crl = db.Column(db.String(50), nullable=True)
    duenoEncargado=db.Column(db.String(10), nullable=True)
    encargado_nombre = db.Column(db.String(255), nullable=True)
    encargado_dni = db.Column(db.String(20), nullable=True)
    encargado_celular = db.Column(db.String(20), nullable=True)
    encargado_foto = db.Column(db.Text, nullable=True)
    # Relationships to refer to the Usuario model
    usuario = db.relationship('Usuario', foreign_keys=[idUsuario])
    worker = db.relationship('Usuario', foreign_keys=[idWorker])
