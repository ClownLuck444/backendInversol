from . import db

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    idUsuario = db.Column(db.Integer, primary_key=True)
    
    empleado_id = db.Column(db.Integer)
    
    nombre = db.Column(db.String(50), nullable=False)
    apell = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    documento = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)

    # Relación en SQLAlchemy (opcional pero útil)
    #empleado = db.relationship('EmpleadoMast_Copia', backref='usuarios')
