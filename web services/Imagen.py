from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import pymssql
import hashlib
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
from flask import send_file, jsonify
from PIL import Image
import pillow_avif  # soporte AVIF
import io
import os
import traceback

app = Flask(__name__)
CORS(app)

app.secret_key = 'your_secret_key'  # Replace with a strong, random secret key

# Database configuration
server = "localhost"
port = 1433
database = "master"
username = "sa"
password = "YourPassword123!"



def get_connection():
    try:
        conn = pymssql.connect(
            server=server, port=port, database=database, user=username, password=password)
        return conn
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return None

@app.route('/imagen-secreta/<int:idUsuario>', methods=['GET'])
def get_imagen_secreta(idUsuario):
    try:
        # Aquí puedes hacer la lógica de cuánto ha avanzado el usuario
        # Por ahora vamos a simplemente enviar una imagen genérica tapada

        # RUTA RELATIVA A DONDE TENGAS TU IMAGEN EN EL SERVIDOR
        path_imagen_tapada = os.path.join('imagenes', 'oculta.jpg')

        return send_file(path_imagen_tapada, mimetype='image/jpeg')

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

    # Marcar una casilla como 'ocupada'
@app.route('/casilla/ocupar', methods=['PUT'])
def ocupar_casilla():
    data = request.json
    idCasilla = data['idCasilla']
    idImagen = data['idImagen']

    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Solo la ocupamos si todavía está libre
        cursor.execute('''
            UPDATE Casilla
            SET estado = 'ocupada'
            WHERE idCasilla = %s AND idImagen = %s AND estado = 'libre'
        ''', (idCasilla, idImagen))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'La casilla no estaba libre'}), 400

        return jsonify({'mensaje': 'Casilla ocupada'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# Marcar una casilla como 'libre' (fallo)
@app.route('/casilla/liberar', methods=['PUT'])
def liberar_casilla():
    data = request.json
    idCasilla = data['idCasilla']
    idImagen = data['idImagen']

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Casilla
            SET estado = 'libre'
            WHERE idCasilla = %s AND idImagen = %s
        ''', (idCasilla, idImagen))
        conn.commit()
        return jsonify({'mensaje': 'Casilla liberada'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# Marcar una casilla como 'descubierta' (acierto)
@app.route('/casilla/descubrir', methods=['PUT'])
def descubrir_casilla():
    data = request.json
    idCasilla = data['idCasilla']
    idImagen = data['idImagen']

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Casilla
            SET estado = 'descubierta'
            WHERE idCasilla = %s AND idImagen = %s
        ''', (idCasilla, idImagen))
        conn.commit()
        return jsonify({'mensaje': 'Casilla descubierta'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

ruta_imagen_original = os.path.abspath('./imagenes/Mulaka.avif')

@app.route('/fragmento/<int:x>/<int:y>', methods=['GET'])
def obtener_fragmento(x, y):
    try:
        lado_celdas = 15
        imagen = Image.open(ruta_imagen_original)
        ancho_total, alto_total = imagen.size

        ancho_celda = ancho_total // lado_celdas
        alto_celda = alto_total // lado_celdas

        box = (
            x * ancho_celda,
            y * alto_celda,
            (x + 1) * ancho_celda,
            (y + 1) * alto_celda
        )

        fragmento = imagen.crop(box)

        buffer = io.BytesIO()
        fragmento.save(buffer, format="JPEG")  # puedes devolver JPG aunque el original sea AVIF
        buffer.seek(0)

        return send_file(buffer, mimetype='image/jpeg')

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=2026)