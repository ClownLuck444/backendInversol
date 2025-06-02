from flask import Blueprint, request,jsonify,make_response
from sqlalchemy.orm import aliased
from sqlalchemy import desc
from Model import db
from Model.usuario import Usuario
from Model.ubicacion import Ubicacion
from flask_socketio import SocketIO,emit
from socketio_instance import socketio
from sqlalchemy import or_
from werkzeug.security import generate_password_hash,check_password_hash
from Model.dato import t_Datos
from Model.orden import orden
from sqlalchemy import select

usuario_bp=Blueprint('usuario_bp',__name__)

@usuario_bp.route('/register', methods=['POST'])
def add_usuario():
    data=request.json
    documento = data['documento']
    password = data['password']
    nombre=data['nombre']
    apell=data['apell']
    estado=data['estado']
    rol=data['rol']

    # Verificar si el usuario ya existe
    if Usuario.query.filter_by(documento=documento).first():
        emit('register_response', {"message": "Usuario ya registrado"})
        return

    # Crear un nuevo usuario
    hashed_password = generate_password_hash(password)
    new_user = Usuario(
        nombre=nombre,
        apell=apell,
        estado=estado,
        documento=documento,
        password=hashed_password,
        rol=rol
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuario registrado exitosamente"}), 201


@usuario_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    documento = data.get('documento')
    password = data.get('password')
    user = Usuario.query.filter_by(documento=documento).first()

    # Usar check_password_hash para comparar
    if user and user.password == password:
        response = make_response(jsonify({
            "message": "Inicio de sesión exitoso",
            "user": {
                "idUsuario": user.idUsuario,
                "nombre": user.nombre,
                "apell": user.apell,
                "estado": user.estado,
                "documento": user.documento,
                "rol": user.rol
            }
        }))
        response.set_cookie(
            'userId',
            value=str(user.idUsuario),
            httponly=False,
            secure=False,
            samesite='Lax',
            max_age=60 * 60 * 24
        )
        return response
    else:
        return jsonify({"message": "Credenciales incorrectas"}), 401

@usuario_bp.route('/change_password', methods=['POST'])
def change_password():
    data = request.json
    documento = data.get('documento')
    password = data.get('password')
    new_password = data.get('new_password')

    user = Usuario.query.filter_by(documento=documento).first()

    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    if user.password != password:
        return jsonify({"message": "Contraseña actual incorrecta"}), 400

    user.password = new_password
    db.session.commit()

    return jsonify({"message": "Contraseña actualizada exitosamente"}), 200

@usuario_bp.route('/buscar_dni/<dni>', methods=['GET'])
def buscar_dni(dni):
    stmt = select(t_Datos).where(t_Datos.c.DNI == int(dni))
    result = db.session.execute(stmt).first()

    if result:
        row = result._mapping  # Para acceder por nombres de columna
        return jsonify({
            "nombre": row["Contacto"],
            "ruc": row["RUC"],
            "celular": row["Celular"],
            "biometria": row["CodigoBiometria"],
            "direccion": row["Direccion"],
            "referencia": row["Referencia"],
            "recarga": row["Recarga"],
            
        })
    else:
        return jsonify({"message": "No se encontró ningún dato para ese DNI"}), 404
    
@usuario_bp.route('/buscar_ruc/<ruc>', methods=['GET'])
def buscar_ruc(ruc):
    stmt = select(t_Datos).where(t_Datos.c.RUC == int(ruc))
    result = db.session.execute(stmt).first()

    if result:
        row = result._mapping  # Para acceder por nombres de columna
        return jsonify({
            "nombre": row["Contacto"],
            "dni": row["DNI"],
            "celular": row["Celular"],
            "biometria": row["CodigoBiometria"],
            "direccion": row["Direccion"],
            "referencia": row["Referencia"],
            "recarga": row["Recarga"],
            
        })
    else:
        return jsonify({"message": "No se encontró ningún dato para ese DNI"}), 404

@usuario_bp.route('/buscar_ruc1/<ruc>', methods=['GET'])
def buscar_ruc1(ruc):
    try:
        # Consulta para obtener toda la información del orden relacionado al RUC
        stmt = select(orden).where(orden.ruc == ruc)
        result = db.session.execute(stmt).first()

        if result:
            row = result._mapping[orden]  # Acceder al objeto ORM directamente

            # Extraer los datos del objeto ORM
            orden_data = {
                "ruc": row.ruc,
                "dni": row.dni,
                "nombre": row.nombre,
                "celular": row.celular,
                "biometria": row.biometria,
                "direccion": row.direccion,
                "region": row.region,
                "provincia": row.provincia,
                "distrito": row.distrito,
                "referencia": row.referencia,
                "recarga": row.recarga,
                "tarjeta": row.tarjeta,
                "observaciones": row.observaciones,
                "chipInicio": row.chipInicio,
                "cantidad": row.cantidad,
                "chipFinal": row.chipFinal,
                "comprobante": row.comprobante,
                "importeCobrado": row.importeCobrado,
                "txt_generado": row.txt_generado,
                "motivo": row.motivo,
                "tipo_negocio": row.tipo_negocio,
                "activacion": row.activacion,
                "codigo_lector": row.codigo_lector,
                "id_crl": row.id_crl,
                "duenoEncargado": row.duenoEncargado,
                "encargado_nombre": row.encargado_nombre,
                "encargado_dni": row.encargado_dni,
                "encargado_celular": row.encargado_celular,
                "encargado_foto": row.encargado_foto,
                "importeCobrado":row.importeCobrado
            }

            # Si deseas seguir incluyendo los lotes relacionados por DNI
            lotes_stmt = select(
                orden.chipInicio,
                orden.cantidad,
                orden.chipFinal,
                orden.comprobante,
            ).where(orden.dni == row.dni)
            lotes_result = db.session.execute(lotes_stmt).fetchall()

            lotes_data = []
            for lote in lotes_result:
                lote_row = lote._mapping
                lotes_data.append({
                    "inicio": lote_row.get("chipInicio", ""),
                    "cantidad": lote_row.get("cantidad", 0),
                    "resultado": lote_row.get("chipFinal", ""),
                    "comprobante": lote_row.get("comprobante", ""),
                })

            orden_data["lotes"] = lotes_data

            return jsonify(orden_data), 200
        else:
            return jsonify({"message": "No se encontró ningún dato para ese RUC"}), 404

    except ValueError:
        return jsonify({"message": "RUC inválido. Debe ser un número."}), 400
    except Exception as e:
        return jsonify({"message": f"Error interno: {str(e)}"}), 500

    
@usuario_bp.route('/buscar_dni1/<dni>', methods=['GET'])
def buscar_dni1(dni):
    try:
        # Obtener la orden más reciente del usuario por la fecha de la ubicación
        ubic = aliased(Ubicacion)  # Usar alias si es necesario

        stmt = (
            select(orden)
            .join(ubic, orden.idUbicacion == ubic.idUbicacion)
            .where(orden.dni == dni)
            .order_by(desc(ubic.fechaHora))
            .limit(1)
        )

        result = db.session.execute(stmt).first()

        if result:
            row = result._mapping[orden]

            # Extraer los datos
            orden_data = {
                "ruc": row.ruc,
                "dni": row.dni,
                "nombre": row.nombre,
                "celular": row.celular,
                "biometria": row.biometria,
                "direccion": row.direccion,
                "region": row.region,
                "provincia": row.provincia,
                "distrito": row.distrito,
                "referencia": row.referencia,
                "recarga": row.recarga,
                "tarjeta": row.tarjeta,
                "observaciones": row.observaciones,
                "chipInicio": row.chipInicio,
                "cantidad": row.cantidad,
                "chipFinal": row.chipFinal,
                "comprobante": row.comprobante,
                "importeCobrado": row.importeCobrado,
                "txt_generado": row.txt_generado,
                "motivo": row.motivo,
                "tipo_negocio": row.tipo_negocio,
                "activacion": row.activacion,
                "codigo_lector": row.codigo_lector,
                "id_crl": row.id_crl,
                "duenoEncargado": row.duenoEncargado,
                "encargado_nombre": row.encargado_nombre,
                "encargado_dni": row.encargado_dni,
                "encargado_celular": row.encargado_celular,
                "encargado_foto": row.encargado_foto,
                "importeCobrado": row.importeCobrado
            }

            # Solo incluir el último lote (mismo registro)
            lote_data = {
                "inicio": row.chipInicio,
                "cantidad": row.cantidad,
                "resultado": row.chipFinal,
                "comprobante": row.comprobante,
            }

            orden_data["lotes"] = [lote_data]

            return jsonify(orden_data), 200
        else:
            return jsonify({"message": "No se encontró ningún dato para ese DNI"}), 404

    except ValueError:
        return jsonify({"message": "DNI inválido. Debe ser un número."}), 400
    except Exception as e:
        return jsonify({"message": f"Error interno: {str(e)}"}), 500
