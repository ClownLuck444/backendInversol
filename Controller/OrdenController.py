from flask import Blueprint, request, jsonify
from Model import db
from Model.usuario import Usuario
from Model.ubicacion import Ubicacion
from Model.wh_itemserie import WH_ItemSerie

from Model.orden import orden
from socketio_instance import socketio
from flask import send_file
import os

orden_bp = Blueprint('orden_bp', __name__)

def crearautomatica(data):
    print(">>> Ejecutando crearautomatica con:", data)
    idUbicacion = data['idUbicacion']
    idUsuario = data['idUsuario']
    nombre = data['nombre']
    ruc = data['ruc']
    celular = data['celular']
    biometria = data.get('biometria')
    direccion = data['direccion']
    region = data['region']
    provincia = data['provincia']
    distrito = data['distrito']
    referencia = data.get('referencia')
    recarga = data['recarga']
    tarjeta = data['tarjeta']
    observaciones = data.get('observaciones')
    lotes = data.get('lotes')
    dni=data['dni']
    motivo=data['motivo'] 
    tipo_negocio=data['tipo_negocio']
    activacion=data['activacion']
    codigo_lector=data['codigo_lector']
    id_crl=data['id_crl']
    duenoEncargado=data['duenoEncargado']
    encargado_nombre = data['encargado_nombre']
    encargado_dni = data['encargado_dni']
    encargado_celular = data['encargado_celular']
    encargado_foto =  data['encargado_foto']
    data_print = data.copy()

    # Abreviamos el campo largo solo para impresión
    foto = data_print.get('encargado_foto')
    if foto and isinstance(foto, str) and len(foto) > 50:
        data_print['encargado_foto'] = foto[:30] + '... ({} caracteres)'.format(len(foto))

    print(">>> Ejecutando crearautomatica con:", data_print)
    usuario = Usuario.query.filter_by(idUsuario=idUsuario).first()
    if not usuario:
        return {'error': 'El usuario con ID proporcionado no existe'}

    try:
        if lotes:
            for lote in lotes:
                nueva_orden = orden(
                    idUbicacion=idUbicacion,
                    idUsuario=idUsuario,
                    idWorker=None,
                    estado='pendiente',
                    nombre=nombre,
                    ruc=ruc,
                    celular=celular,
                    biometria=biometria,
                    direccion=direccion,
                    region=region,
                    provincia=provincia,
                    distrito=distrito,
                    referencia=referencia,
                    recarga=recarga,
                    tarjeta=tarjeta,
                    observaciones=observaciones,
                    chipInicio=lote['inicio'],
                    cantidad=lote['cantidad'],
                    chipFinal=lote['resultado'],
                    comprobante=lote['comprobante'],
                    importeCobrado=lote['importe'],
                    dni=dni,
                    motivo=motivo,
                    tipo_negocio=tipo_negocio,
                    activacion=activacion,
                    codigo_lector=codigo_lector,
                    id_crl=id_crl,
                    duenoEncargado=duenoEncargado,
                    encargado_nombre=encargado_nombre,
                    encargado_dni=encargado_dni,
                    encargado_celular=encargado_celular,
                    encargado_foto=encargado_foto

                )
                db.session.add(nueva_orden)
        else:
            nueva_orden = orden(
                idUbicacion=idUbicacion,
                idUsuario=idUsuario,
                idWorker=None,
                estado='pendiente',
                nombre=nombre,
                ruc=ruc,
                celular=celular,
                biometria=biometria,
                direccion=direccion,
                region=region,
                provincia=provincia,
                distrito=distrito,
                referencia=referencia,
                recarga=recarga,
                tarjeta=tarjeta,
                observaciones=observaciones,
                chipInicio=None,
                cantidad=0,
                chipFinal=None,
                comprobante="",
                importeCobrado=0,
                dni=dni,
                motivo=motivo,
                tipo_negocio=tipo_negocio,
                activacion=activacion,
                codigo_lector=codigo_lector,
                id_crl=id_crl,
                duenoEncargado=duenoEncargado,
                encargado_nombre=encargado_nombre,
                encargado_dni=encargado_dni,
                encargado_celular=encargado_celular,
                encargado_foto=encargado_foto

            )
            db.session.add(nueva_orden)

        db.session.commit()
        print(">>> Órdenes guardadas exitosamente")
    except Exception as e:
        db.session.rollback()
        print(">>> ERROR AL GUARDAR ORDEN:", str(e))  # <-- esto
        return {'error': f'Error al guardar las órdenes: {str(e)}'}

    socketio.emit('nueva_orden', {'mensaje': 'Órdenes creadas correctamente'})
    return {'mensaje': 'Órdenes creadas correctamente'}



@orden_bp.route('/aceptar-orden/<int:idOrden>', methods=['POST'])
def aceptar_orden(idOrden):
    data = request.json
    trabajador = Usuario.query.filter_by(idUsuario=data['idWorker']).first()

    if not trabajador:
        return jsonify({'error': 'Trabajador no encontrado'}), 404

    Orden = orden.query.filter_by(idOrden=idOrden).first()

    if not Orden:
        return jsonify({'error': 'Orden no encontrada'}), 404

    Orden.idWorker = trabajador.idUsuario  # Assign the worker
    Orden.estado = 'aceptado'

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar la orden: {str(e)}'}), 500

    socketio.emit('orden_aceptada', {
        'idOrden': Orden.idOrden,
        'idWorker': trabajador.idUsuario,
        'estado': Orden.estado
    })

    return jsonify({'message': 'Orden aceptada', 'idOrden': Orden.idOrden, 'idWorker': trabajador.idUsuario}), 200


@orden_bp.route('/pedidos', methods=['GET'])
def obtener_pedidos():
    pedidos = orden.query.all()
    resultados = []
    for pedido in pedidos:
        ubicacion = Ubicacion.query.get(pedido.idUbicacion)
        usuario = Usuario.query.get(pedido.idUsuario)  # User who created the order
        trabajador = Usuario.query.get(pedido.idWorker)  # Worker who accepted the order (if assigned)

        resultados.append({
            'idOrden': pedido.idOrden,
            'usuario': usuario.nombre,  # User's name who created the order
            'trabajador': trabajador.nombre if trabajador else None,  # Worker’s name (if any)
            'latitud': ubicacion.latitud,
            'longitud': ubicacion.longitud,
            'detalles': 'Detalles del pedido',
            'direccion': ubicacion.direccion
        })

    return jsonify(resultados)


@orden_bp.route('/solicitudes_worker/<int:idWorker>', methods=['GET'])
def get_pedidos_worker(idWorker):
    pedidos_worker = db.session.query(orden, Ubicacion) \
        .join(Ubicacion, orden.idUbicacion == Ubicacion.idUbicacion) \
        .filter(
            (orden.idWorker == idWorker) |  # Órdenes asignadas al trabajador
            ((orden.idWorker == None) & (orden.estado == 'pendiente'))  # Órdenes pendientes
        ).all()

    resultado = []
    for pedido, ubicacion in pedidos_worker:
        asesor = Usuario.query.get(pedido.idUsuario) 
        resultado.append({
            'idOrden': pedido.idOrden,
            'motivo':pedido.motivo,
            "direccion": ubicacion.direccion,
            "fecha": ubicacion.fechaHora.strftime('%d/%m/%Y'),
            'nombre': pedido.nombre,
            'asesor':asesor.nombre if asesor else None,
            'dni': pedido.dni,
            'ruc': pedido.ruc,
            'celular': pedido.celular,
            'biometria': pedido.biometria,
            'provincia': pedido.provincia,
            'distrito': pedido.distrito,
            'referencia': pedido.referencia,
            'recarga': pedido.recarga,
            'tarjeta': pedido.tarjeta,
            'observaciones': pedido.observaciones,
            'estado': pedido.estado,
            'latitud': ubicacion.latitud,
            'longitud': ubicacion.longitud,
            'comprobante':pedido.comprobante,
            'cantidad':pedido.cantidad,
            "hora": ubicacion.fechaHora.strftime('%H:%M:%S'),
            'chipInicio': pedido.chipInicio,
            'chipFinal': pedido.chipFinal,
            'txt_generado': pedido.txt_generado,
            'region':pedido.region
        })

    return jsonify(resultado), 200

def generar_iccids(chip_inicio, chip_final):
    try:
        inicio = int(chip_inicio)
        final = int(chip_final)
    except ValueError:
        return []
    if inicio > final:
        return []
    
    iccids = []
    current = inicio
    while current <= final:
        iccids.append(str(current).zfill(len(chip_inicio)))  # mantén los ceros a la izquierda si hay
        current += 1
    return iccids


@orden_bp.route('/generar_txt/<int:idOrden>', methods=['GET', 'OPTIONS'])
def generar_txt(idOrden):
    # Obtener la orden desde la base de datos
    orden_actual = orden.query.get_or_404(idOrden)
    print(f"chipInicio: {orden_actual.chipInicio}, chipFinal: {orden_actual.chipFinal}")

    if not orden_actual.chipInicio or not orden_actual.chipFinal:
        return jsonify({'error': 'Esta orden no tiene chipInicio o chipFinal'}), 400

    # Generar los ICCIDs
    iccids = generar_iccids(orden_actual.chipInicio, orden_actual.chipFinal)
    if not iccids:
        return jsonify({'error': 'Rango inválido de ICCIDs'}), 400

    # Crear las líneas para el archivo
    lineas = [f"{iccid},1" for iccid in iccids]             

    # Formatear el nombre del archivo según los requisitos
    cantidad_chips = len(iccids)
    nombre_archivo = f"{orden_actual.region}_{orden_actual.dni}_{cantidad_chips} chips.txt"

    # Crear el directorio para guardar los archivos generados
    os.makedirs('txt_generados', exist_ok=True)
    filepath = os.path.join('txt_generados', nombre_archivo)

    # Escribir el archivo de texto
    with open(filepath, 'w') as f:
        f.write('\n'.join(lineas))

    # Actualizar el estado en la base de datos
    orden_actual.txt_generado = True
    db.session.commit()

    # Enviar el archivo generado al cliente
    return send_file(filepath, as_attachment=True)

@orden_bp.route('/buscar_serie/<numero_serie>', methods=['GET'])
def buscar_serie(numero_serie):
    if not numero_serie:
        return jsonify({'error': 'Número de serie no proporcionado'}), 400

    resultado = WH_ItemSerie.query.filter_by(NumeroSerie=numero_serie).first()

    if resultado:
        return jsonify({
            'mensaje': 'Número de serie encontrado',
            'numero_serie': resultado.NumeroSerie
        }), 200
    else:
        return jsonify({'mensaje': 'Número de serie no encontrado'}), 404
    
@orden_bp.route('/eliminar_orden/<int:idOrden>', methods=['DELETE'])
def eliminar_orden(idOrden):
    orden_a_eliminar = orden.query.get(idOrden)

    if not orden_a_eliminar:
        return jsonify({'error': 'Orden no encontrada'}), 404

    try:
        db.session.delete(orden_a_eliminar)
        db.session.commit()
        return jsonify({'mensaje': f'Orden {idOrden} eliminada correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar la orden', 'detalle': str(e)}), 500