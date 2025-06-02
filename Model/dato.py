from typing import Any, List, Optional

from sqlalchemy import Boolean, CHAR, Column, DECIMAL, Date, DateTime, Float, ForeignKeyConstraint, Identity, Integer, LargeBinary, Numeric, PrimaryKeyConstraint, String, Table, Unicode
from sqlalchemy.dialects.mssql import MONEY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import decimal

class Base(DeclarativeBase):
    pass

t_Datos = Table(
    'Datos', Base.metadata,
    Column('RazonSocial', String(100, 'Modern_Spanish_CI_AS')),
    Column('RUC', String(12, 'Modern_Spanish_CI_AS')),
    Column('Contacto', String(100, 'Modern_Spanish_CI_AS')),
    Column('DNI', Integer),
    Column('Celular', String(9, 'Modern_Spanish_CI_AS')),
    Column('CodigoBiometria', String(11, 'Modern_Spanish_CI_AS')),
    Column('Direccion', String(100, 'Modern_Spanish_CI_AS')),
    Column('Provincia', String(20, 'Modern_Spanish_CI_AS')),
    Column('Distrito', String(20, 'Modern_Spanish_CI_AS')),
    Column('Referencia', String(150, 'Modern_Spanish_CI_AS')),
    Column('Recarga', String(2, 'Modern_Spanish_CI_AS')),
    Column('NumeroRecarga', Integer),
    Column('FechaCaptacion', Date),
    Column('EstadoEmpradronamiento', String(15, 'Modern_Spanish_CI_AS')),
    Column('SeEntrego', String(2, 'Modern_Spanish_CI_AS')),
    Column('TarjetaActiva', String(2, 'Modern_Spanish_CI_AS')),
    Column('ObservacionesTarjeta', String(50, 'Modern_Spanish_CI_AS')),
    Column('FechaVisita', String(20, 'Modern_Spanish_CI_AS')),
    Column('FechaInventario', String(20, 'Modern_Spanish_CI_AS')),
    Column('GPS', String(50, 'Modern_Spanish_CI_AS'))
)


