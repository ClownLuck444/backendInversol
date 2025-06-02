from flask import Blueprint, request,jsonify
import requests
from datetime import datetime
from Model import db
from Model.ubicacion import Ubicacion
from flask_socketio import SocketIO,emit
from socketio_instance import socketio
import requests
from .OrdenController import crearautomatica

ubicacion_bp=Blueprint('ubicacion_bp',__name__)

LOCATIONIQ_API_KEY = 'pk.4f504fe055f1173a74e9e625f2a2a59f'
def geocodificar_direccion(direccion):
    url = 'https://us1.locationiq.com/v1/search.php'
    params = {
        'key': LOCATIONIQ_API_KEY,
        'q': direccion,
        'format': 'json',
        'limit': 1
    }
    respuesta = requests.get(url, params=params)
    data = respuesta.json()

    if data:
        latitud = float(data[0]['lat'])
        longitud = float(data[0]['lon'])
        return latitud, longitud
    else:
        return None

# Geocodificación inversa (lat/lng → dirección)
def geocode_coordinates(lat, lng):
    url = 'https://us1.locationiq.com/v1/reverse.php'
    params = {
        'key': LOCATIONIQ_API_KEY,
        'lat': lat,
        'lon': lng,
        'format': 'json'
    }
    respuesta = requests.get(url, params=params)
    data = respuesta.json()

    if 'display_name' in data:
        return data['display_name']
    return None

@ubicacion_bp.route('/guardar-ubicacion', methods=['POST'])
def localizacion():
    print(">>> Ruta /guardar-ubicacion llamada")
    data = request.json
    lat = data['latitud']
    lng = data['longitud']
    idUsuario = data['idUsuario']
    nombre = data.get('nombre', '')
    ruc = data.get('ruc', '')
    celular = data.get('celular', '')
    biometria = data.get('biometria', '')
    region = data.get('region', '')
    provincia = data.get('provincia', '')
    distrito = data.get('distrito', '')
    referencia = data.get('referencia', '')
    recarga = data.get('recarga', False)
    tarjeta = data.get('tarjeta', False)
    observaciones = data.get('observaciones', '')
    lotes = data.get('lotes', [])
    dni=data.get('dni','')
    motivo=data.get('motivo','')
    tipo_negocio=data.get('tipo_negocio','')
    activacion=data.get('activacion','')
    codigo_lector=data.get('codigo_lector','')
    id_crl=data.get('id_crl','')
    duenoEncargado=data.get('duenoEncargado','')
    encargado_nombre=data.get('encargado_nombre','')
    encargado_dni=data.get('encargado_dni','')
    encargado_celular=data.get('encargado_celular','')
    encargado_foto=data.get('encargado_foto','')
    direccion=data.get('direccion','')
    direccion1 = geocode_coordinates(lat, lng)
    if not direccion1:
        return jsonify({'error': 'No se pudo obtener la dirección'}), 400

    # Guardar la ubicación
    nueva_ubicacion = Ubicacion(
        idUsuario=idUsuario,
        latitud=lat,
        longitud=lng,
        direccion=direccion1,
        fechaHora=datetime.now()
    )
    db.session.add(nueva_ubicacion)
    db.session.commit()

    # ✅ Llamar solo una vez a crearautomatica con todos los lotes
    crearautomatica({
        'idUbicacion': nueva_ubicacion.idUbicacion,
        'idUsuario': idUsuario,
        'nombre': nombre,
        'ruc': ruc,
        'celular': celular,
        'biometria': biometria,
        'direccion': direccion,
        'region': region,
        'provincia': provincia,
        'distrito': distrito,
        'referencia': referencia,
        'recarga': recarga,
        'tarjeta': tarjeta,
        'observaciones': observaciones,
        'lotes': lotes,
        'dni':dni,
        'motivo':motivo,
        'tipo_negocio':tipo_negocio,
        'activacion':activacion,
        'codigo_lector':codigo_lector,
        'id_crl':id_crl,
        'duenoEncargado':duenoEncargado,
        'encargado_nombre': encargado_nombre,
        'encargado_dni': encargado_dni,
        'encargado_celular': encargado_celular,
        'encargado_foto': encargado_foto
    })

    socketio.emit('nueva_ubicacion', {'idUsuario': idUsuario, 'latitud': lat, 'longitud': lng})

    return jsonify({'status': 'ubicación y órdenes guardadas', 'direccion': direccion}), 201
# Función para calcular la ruta usando la API de Google Maps Directions
def calcular_ruta(origen, destino):
    api_key = 'AIzaSyB464cx0wCPJ2cJBuWGR9mHXOH0pDCCgSc'
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origen}&destination={destino}&key={api_key}'
    respuesta = requests.get(url)
    data = respuesta.json()

    if data['status'] == 'OK':
        ruta = data['routes'][0]['legs'][0]
        return {
            'distancia': ruta['distance']['text'],
            'duracion': ruta['duration']['text'],
            'pasos': ruta['steps']
        }
    else:
        return None

@ubicacion_bp.route('/calcular-ruta', methods=['POST'])
def calcular_ruta_endpoint():
    data = request.json
    try:
        origen = f"{data['latitud']},{data['longitud']}"
        destino = data['direccion']
    except KeyError as e:
        return jsonify({'error': f'Llave faltante: {str(e)}'}), 400

    ruta = calcular_ruta(origen, destino)
    if ruta:
        return jsonify(ruta), 200
    else:
        return jsonify({'error': 'No se pudo calcular la ruta'}), 400
@socketio.on('conectar_trabajador')
def conectar_trabajador(data):
    emit('respuesta_conexion', {'status': 'Trabajador conectado'}, broadcast=True)

@ubicacion_bp.route('/obtener-foto/<int:idUbicacion>', methods=['GET'])
def obtener_foto(idUbicacion):
    # Buscar la ubicación en la base de datos
    ubicacion = Ubicacion.query.filter_by(idUbicacion=idUbicacion).first()

    if not ubicacion:
        return jsonify({'error': 'Ubicación no encontrada'}), 404

    # Recuperar la foto en Base64
    foto_base64 = ubicacion.encargado_foto

    if not foto_base64:
        return jsonify({'error': 'Foto no disponible para esta ubicación'}), 404

    # Devolver la foto en la respuesta
    return jsonify({'foto': foto_base64}), 200