from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import pymssql
import hashlib
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random

codigos_recuperacion = {}  # {correo: codigo}

app = Flask(__name__)
CORS(app)

app.secret_key = 'your_secret_key'  # Replace with a strong, random secret key

# Database configuration
server = "localhost"
port = 1433
database = "master"
username = "sa"
password = "YourPassword123!"

# Database connection function
@app.route('/boletousuario/<int:id>', methods=['GET'])
def count_boletos_usuario(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute('SELECT COUNT(*) AS cantidad '
                       'FROM Boleto WHERE idUsuario = %s', (id,))
        row = cursor.fetchone()
        conn.close()
        return jsonify({'cantidad': row['cantidad']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_connection():
    try:
        conn = pymssql.connect(
            server=server, port=port, database=database, user=username, password=password)
        return conn
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return None


# Metodos para recuperacion de contrasena
def enviar_correo(destinatario, asunto, cuerpo):
    message = Mail(
        from_email='rerreza@hotmail.es',  # Tu correo verificado
        to_emails=destinatario,
        subject=asunto,
        plain_text_content=cuerpo
    )
    try:
        # Sustituye tu API Key aquí
        sg = SendGridAPIClient(
            '')
        response = sg.send(message)
        print(f'Correo enviado: {response.status_code}')
    except Exception as e:
        print(f'Error enviando correo: {e}')

# Funciones para recuperar contrasena


@app.route('/recuperar', methods=['POST'])
def solicitar_recuperacion():
    data = request.json
    correo = data.get('correo')

    if not correo:
        return jsonify({'error': 'Correo requerido'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.idUsuario 
            FROM Usuario u 
            INNER JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
            WHERE u.contacto = %s
        ''', (correo,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Correo no encontrado'}), 404

        # Generar código
        codigo = random.randint(100000, 999999)

        # Guardar en memoria temporal
        codigos_recuperacion[correo] = codigo

        # Enviar correo
        enviar_correo(correo, 'Recuperación de Contraseña',
                      f'Tu código de recuperación es: {codigo}')

        return jsonify({'mensaje': 'Correo enviado con el código de recuperación'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/validarcodigo', methods=['POST'])
def validar_codigo():
    data = request.json
    correo = data.get('correo')
    codigo = data.get('codigo')
    nueva_contrasena = data.get('nuevaContrasena')

    if not correo or not codigo or not nueva_contrasena:
        return jsonify({'error': 'Correo, código y nueva contraseña requeridos'}), 400

    # Validar código
    if codigos_recuperacion.get(correo) != int(codigo):
        return jsonify({'error': 'Código incorrecto'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Buscar idUsuario
        cursor.execute('''
            SELECT u.idUsuario 
            FROM Usuario u 
            INNER JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
            WHERE u.contacto = %s
        ''', (correo,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Correo no encontrado'}), 404

        idUsuario = user[0]

        # Actualizar contraseña
        hashed_password = hashlib.sha1(nueva_contrasena.encode()).hexdigest()
        cursor.execute('UPDATE UsuarioNormal SET contrasena = %s WHERE idUsuario = %s',
                       (hashed_password, idUsuario))
        conn.commit()

        # Eliminar el código una vez usado
        del codigos_recuperacion[correo]

        return jsonify({'mensaje': 'Contraseña actualizada correctamente'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# Metodos para el login
def verify_password(stored_password_hash, provided_password):
    hashed_provided_password = hashlib.sha1(
        provided_password.encode()).hexdigest()
    return stored_password_hash == hashed_provided_password


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Se requiere usuario y contraseña'}), 400

    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)

            # Buscar usuario y su contraseña usando JOIN
            cursor.execute('''
                SELECT u.idUsuario, u.usuario, un.contrasena
                FROM Usuario u
                JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
                WHERE u.usuario = %s
            ''', (username,))
            user = cursor.fetchone()

            if user and verify_password(user['contrasena'], password):
                session['username'] = username
                session['idUsuario'] = user['idUsuario']
                return jsonify({'mensaje': 'Autenticación exitosa', 'idUsuario': user['idUsuario'], 'username': username}), 200
            else:
                return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

        except Exception as e:
            return jsonify({'error': f'Error en BD {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


# Metodos para fetch y manejo de errores

def fetch_one_usuario(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT 
          u.idUsuario, 
          u.usuario, 
          u.idEvento,
          u.contacto,  -- Aquí puede ser correo o nombre de red social
          un.contrasena,
          CASE 
            WHEN un.idUsuario IS NOT NULL THEN 'Normal'
            WHEN ur.idUsuario IS NOT NULL THEN 'Red'
            ELSE 'Desconocido'
          END AS tipoUsuario
        FROM Usuario u
        LEFT JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
        LEFT JOIN UsuarioRed ur ON u.idUsuario = ur.idUsuario
        WHERE u.idUsuario = %s
    ''', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_boleto(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Boleto WHERE idBoleto = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_evento(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Evento WHERE idEvento = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_imagen(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Imagen WHERE idImagen = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_casilla(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Casilla WHERE idCasilla = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_pregunta(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Pregunta WHERE idPregunta = %s', (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        'idPregunta': row[0],
        'pregunta': row[1],
        'options': [
            {'option': 'A', 'text': row[2]},
            {'option': 'B', 'text': row[3]},
            {'option': 'C', 'text': row[4]},
            {'option': 'D', 'text': row[5]},
        ],
        # Si 'respuesta' es 'opcionD', se extrae 'D'
        'correctOption': row[6][-1],
        'timer': '00:30'
    }


def fetch_one_intento_correcto(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        'SELECT * FROM IntentoCorrecto WHERE idCorrecto = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_intento_incorrecto(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        'SELECT * FROM IntentoIncorrecto WHERE idIncorrecto = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


# Metodos para Usuario
@app.route('/usuario', methods=['GET'])
def get_usuarios():
    try:
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute('''
            SELECT 
              u.idUsuario, 
              u.usuario, 
              u.idEvento,
              u.contacto,  -- Puede ser correo o nombre de la red social
              un.contrasena,
              CASE 
                WHEN un.idUsuario IS NOT NULL THEN 'Normal'
                WHEN ur.idUsuario IS NOT NULL THEN 'Red'
                ELSE 'Desconocido'
              END AS tipoUsuario
            FROM Usuario u
            LEFT JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
            LEFT JOIN UsuarioRed ur ON u.idUsuario = ur.idUsuario
        ''')
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/usuariored', methods=['GET'])
def get_usuarios_red():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT 
          u.idUsuario, 
          u.usuario, 
          u.contacto,  -- contacto contiene el nombre de la red social
        FROM Usuario u
        INNER JOIN UsuarioRed ur ON u.idUsuario = ur.idUsuario
    ''')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/usuarionormal', methods=['GET'])
def get_usuarios_normal():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT 
          u.idUsuario, 
          u.usuario, 
          u.contacto AS correo,  -- contacto ahora guarda el correo para normales
          un.contrasena
        FROM Usuario u
        INNER JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
    ''')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/usuario/<int:id>', methods=['GET'])
def get_one_usuario(id):
    usuario = fetch_one_usuario(id)
    if usuario:
        return jsonify(usuario)
    else:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404


@app.route('/usuarionormal', methods=['POST'])
def create_usuario_normal():
    data = request.json
    usuario = data['usuario']
    correo = data['correo']
    contrasena = data['contrasena']

    # Actualizar contraseña
    hashed_password = hashlib.sha1(contrasena.encode()).hexdigest()

    conn = get_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        # Buscar evento en curso automáticamente
        cursor.execute('''
            SELECT TOP 1 idEvento 
            FROM Evento 
            WHERE fechaInicio <= GETDATE() AND fechaFinal >= GETDATE()
            ORDER BY fechaInicio DESC
        ''')
        evento = cursor.fetchone()

        if not evento:
            return jsonify({'error': 'No hay evento en curso'}), 400

        idEvento = evento['idEvento']

        # Insertar en Usuario con el correo como contacto
        cursor.execute(
            'INSERT INTO Usuario (usuario, idEvento, contacto) VALUES (%s, %s, %s)', (usuario, idEvento, correo))
        conn.commit()

        cursor.execute('SELECT SCOPE_IDENTITY() as idUsuario')
        idUsuario = cursor.fetchone()['idUsuario']

        # Insertar en UsuarioNormal (solo contrasena ahora)
        cursor.execute('INSERT INTO UsuarioNormal (idUsuario, contrasena) VALUES (%s, %s)',
                       (idUsuario, hashed_password))
        conn.commit()

        return jsonify({'mensaje': 'Usuario normal creado', 'idUsuario': idUsuario}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/usuariored', methods=['POST'])
def create_usuario_red():
    data = request.json
    nombre = data['usuario']
    contacto = data['contacto']

    conn = get_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        # Buscar el evento en curso
        cursor.execute('''
            SELECT TOP 1 idEvento 
            FROM Evento 
            WHERE fechaInicio <= GETDATE() AND fechaFinal >= GETDATE()
            ORDER BY fechaInicio DESC
        ''')
        evento = cursor.fetchone()

        if not evento:
            return jsonify({'error': 'No hay evento en curso'}), 400

        idEvento = evento['idEvento']

        # Verificar si el usuario ya existe
        cursor.execute(
            'SELECT idUsuario FROM Usuario WHERE usuario = %s', (nombre,))
        existing = cursor.fetchone()

        if existing:
            idUsuario = existing['idUsuario']
            mensaje = 'Usuario ya existe'
        else:
            # Insertar en Usuario con contacto = nombre de red social
            cursor.execute(
                'INSERT INTO Usuario (usuario, idEvento, contacto) VALUES (%s, %s, %s)', (nombre, idEvento, contacto))
            conn.commit()

            cursor.execute('SELECT SCOPE_IDENTITY() AS idUsuario')
            idUsuario = cursor.fetchone()['idUsuario']

            # Insertar en UsuarioRed (solo tokenRed si se envía)
            cursor.execute('INSERT INTO UsuarioRed (idUsuario) VALUES (%s)',
                           (idUsuario))
            conn.commit()

            mensaje = 'Usuario red creado'

        return jsonify({'mensaje': mensaje, 'idUsuario': idUsuario}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/usuario/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.json
    usuario = data['usuario']
    idEvento = data['idEvento']
    tipo = data['tipoUsuario']

    # Validar si el usuario existe
    existing = fetch_one_usuario(id)
    if not existing:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404

    # Validar evento
    evento = fetch_one_evento(idEvento)
    if not evento:
        return jsonify({'mensaje': 'El evento especificado no existe'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if tipo == 'Normal':
            correo = data['contacto']
            contrasena = data['contrasena']

            # Actualizar Usuario con contacto = correo
            cursor.execute('UPDATE Usuario SET usuario = %s, idEvento = %s, contacto = %s WHERE idUsuario = %s',
                           (usuario, idEvento, correo, id))

            # Ver si ya existía en UsuarioNormal
            cursor.execute(
                'SELECT * FROM UsuarioNormal WHERE idUsuario = %s', (id,))
            if cursor.fetchone():
                cursor.execute('UPDATE UsuarioNormal SET contrasena = %s WHERE idUsuario = %s',
                               (contrasena, id))
            else:
                cursor.execute('INSERT INTO UsuarioNormal (idUsuario, contrasena) VALUES (%s, %s)',
                               (id, contrasena))

            # Asegurarse que no exista en UsuarioRed
            cursor.execute(
                'DELETE FROM UsuarioRed WHERE idUsuario = %s', (id,))

        elif tipo == 'Red':
            redSocial = data['contacto']

            # Actualizar Usuario con contacto = redSocial
            cursor.execute('UPDATE Usuario SET usuario = %s, idEvento = %s, contacto = %s WHERE idUsuario = %s',
                           (usuario, idEvento, redSocial, id))

            # Ver si ya existía en UsuarioRed
            cursor.execute(
                'SELECT * FROM UsuarioRed WHERE idUsuario = %s', (id,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO UsuarioRed (idUsuario) VALUES (%s, %s)',
                               (id))

            # Asegurarse que no exista en UsuarioNormal
            cursor.execute(
                'DELETE FROM UsuarioNormal WHERE idUsuario = %s', (id,))
        else:
            conn.rollback()
            return jsonify({'mensaje': 'Tipo de usuario inválido'}), 400

        conn.commit()
        return jsonify({'mensaje': 'Usuario actualizado'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/usuario/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    existing = fetch_one_usuario(id)
    if not existing:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Borrar de tablas hijas primero
        cursor.execute('DELETE FROM UsuarioNormal WHERE idUsuario = %s', (id,))
        cursor.execute('DELETE FROM UsuarioRed WHERE idUsuario = %s', (id,))
        cursor.execute('DELETE FROM Usuario WHERE idUsuario = %s', (id,))

        conn.commit()
        return jsonify({'mensaje': 'Usuario eliminado'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# Metodos para Boleto
@app.route('/boleto', methods=['GET'])
def get_boletos():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Boleto')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/boleto/<int:id>', methods=['GET'])
def get_one_boleto(id):
    data = fetch_one_boleto(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/boleto', methods=['POST'])
def create_boleto():
    data = request.json
    tipo = data['tipo']
    idUsuario = data['idUsuario']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Boleto (tipo, idUsuario) VALUES (%s, %s)', (tipo, idUsuario))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Boleto creado'}), 201


@app.route('/boleto/<int:id>', methods=['PUT'])
def update_boleto(id):
    data = request.json
    tipo = data['tipo']
    idUsuario = data['idUsuario']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE Boleto SET tipo = %s, idUsuario = %s WHERE idBoleto = %s', (tipo, idUsuario, id))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Boleto actualizado'})


@app.route('/boleto/<int:id>', methods=['DELETE'])
def delete_boleto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Boleto WHERE idBoleto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Boleto eliminado'})


# Metodos para Evento
@app.route('/evento', methods=['GET'])
def get_eventos():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Evento')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/evento/<int:id>', methods=['GET'])
def get_one_evento(id):
    data = fetch_one_evento(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/evento', methods=['POST'])
def create_evento():
    data = request.json
    fechaInicio = data['fechaInicio']
    fechaFinal = data['fechaFinal']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO Evento (fechaInicio, fechaFinal) VALUES (%s, %s)', (fechaInicio, fechaFinal))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Evento creado'}), 201


@app.route('/evento/<int:id>', methods=['PUT'])
def update_evento(id):
    data = request.json
    fechaInicio = data['fechaInicio']
    fechaFinal = data['fechaFinal']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Evento SET fechaInicio = %s, fechaFinal = %s WHERE idEvento = %s',
                   (fechaInicio, fechaFinal, id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Evento actualizado'})


@app.route('/evento/<int:id>', methods=['DELETE'])
def delete_evento(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Evento WHERE idEvento = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Evento eliminado'})


# Metodos para Imagen
@app.route('/imagen', methods=['GET'])
def get_imagenes():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Imagen')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/imagen/<int:id>', methods=['GET'])
def get_one_imagen(id):
    data = fetch_one_imagen(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/imagen', methods=['POST'])
def create_imagen():
    data = request.json
    url = data['URL']
    estado = data['estado']
    respuesta = data['respuesta']
    idEvento = data['idEvento']
    idUsuario = data.get('idUsuario')  # Optional field, can be NULL
    # Check if the event exists using the helper function
    evento = fetch_one_evento(idEvento)
    if not evento:
        return jsonify({'mensaje': 'El evento especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Imagen (URL, estado, respuesta, idEvento, idUsuario) VALUES (%s, %s, %s, %s, %s)',
                       (url, estado, respuesta, idEvento, idUsuario))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Imagen creada'}), 201


@app.route('/imagen/<int:id>', methods=['PUT'])
def update_imagen(id):
    data = request.json
    url = data['URL']
    estado = data['estado']
    respuesta = data['respuesta']
    idEvento = data['idEvento']
    idUsuario = data.get('idUsuario')  # Optional field, can be NULL
    # Check if the event exists using the helper function
    evento = fetch_one_evento(idEvento)
    if not evento:
        return jsonify({'mensaje': 'El evento especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE Imagen SET URL = %s, estado = %s, respuesta = %s, idEvento = %s, idUsuario = %s WHERE idImagen = %s',
                       (url, estado, respuesta, idEvento, idUsuario, id))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Imagen actualizada'})


@app.route('/imagen/<int:id>', methods=['DELETE'])
def delete_imagen(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Imagen WHERE idImagen = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Imagen eliminada'})


# Metodos para Casilla
@app.route('/casilla', methods=['GET'])
def get_casillas():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Casilla')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/casilla/<int:id>', methods=['GET'])
def get_one_casilla(id):
    data = fetch_one_casilla(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/casilla', methods=['POST'])
def create_casilla():
    data = request.json
    idImagen = data['idImagen']
    coordenadaX = data['coordenadaX']
    coordenadaY = data['coordenadaY']
    idPregunta = data['idPregunta']
    # Check if the image exists using the helper function
    imagen = fetch_one_imagen(idImagen)
    if not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        # Check if the question exists using the helper function
        pregunta = fetch_one_pregunta(idPregunta)
        if not pregunta:
            return jsonify({'mensaje': 'La pregunta especificada no existe'}), 400
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Casilla (idImagen, coordenadaX, coordenadaY, idPregunta) VALUES (%s, %s, %s, %s)',
                           (idImagen, coordenadaX, coordenadaY, idPregunta))
            conn.commit()
            conn.close()
            return jsonify({'mensaje': 'Casilla creada'}), 201


@app.route('/casilla/<int:id>', methods=['PUT'])
def update_casilla(id):
    data = request.json
    idImagen = data['idImagen']
    coordenadaX = data['coordenadaX']
    coordenadaY = data['coordenadaY']
    idPregunta = data['idPregunta']
    # Check if the image exists using the helper function
    imagen = fetch_one_imagen(idImagen)
    if not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        # Check if the question exists using the helper function
        pregunta = fetch_one_pregunta(idPregunta)
        if not pregunta:
            return jsonify({'mensaje': 'La pregunta especificada no existe'}), 400
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE Casilla SET idImagen = %s, coordenadaX = %s, coordenadaY = %s, idPregunta = %s WHERE idCasilla = %s',
                           (idImagen, coordenadaX, coordenadaY, idPregunta, id))
            conn.commit()
            conn.close()
            return jsonify({'mensaje': 'Casilla actualizada'})


@app.route('/casilla/<int:id>', methods=['DELETE'])
def delete_casilla(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Casilla WHERE idCasilla = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Casilla eliminada'})


# Metodos para Pregunta
@app.route('/pregunta', methods=['GET'])
def get_preguntas():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Pregunta')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/pregunta/<int:id>', methods=['GET'])
def get_one_pregunta(id):
    data = fetch_one_pregunta(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/pregunta', methods=['POST'])
def create_pregunta():
    data = request.json
    pregunta = data['pregunta']
    opcionA = data.get('opcionA')
    opcionB = data.get('opcionB')
    opcionC = data.get('opcionC')
    opcionD = data.get('opcionD')
    respuesta = data['respuesta']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES (%s, %s, %s, %s, %s, %s)',
                   (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta creada'}), 201


@app.route('/pregunta/<int:id>', methods=['PUT'])
def update_pregunta(id):
    data = request.json
    pregunta = data['pregunta']
    # se utiliza data.get() porque pueden ser NULL
    opcionA = data.get('opcionA')
    opcionB = data.get('opcionB')
    opcionC = data.get('opcionC')
    opcionD = data.get('opcionD')
    respuesta = data['respuesta']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Pregunta SET pregunta = %s, opcionA = %s, opcionB = %s, opcionC = %s, opcionD = %s, respuesta = %s WHERE idPregunta = %s',
                   (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta, id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta actualizada'})


@app.route('/pregunta/<int:id>', methods=['DELETE'])
def delete_pregunta(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Pregunta WHERE idPregunta = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta eliminada'})


# Metodos para IntentoCorrecto
@app.route('/intentoCorrecto', methods=['GET'])
def get_intentos_correctos():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM IntentoCorrecto')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/intentoCorrecto/<int:id>', methods=['GET'])
def get_one_intento_correcto(id):
    data = fetch_one_intento_correcto(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/intentoCorrecto', methods=['POST'])
def create_intento_correcto():
    data = request.json
    idUsuario = data['idUsuario']
    idCasilla = data['idCasilla']
    idImagen = data['idImagen']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    casilla = fetch_one_casilla(idCasilla)
    imagen = fetch_one_imagen(idImagen)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    elif not casilla:
        return jsonify({'mensaje': 'La casilla especificada no existe'}), 400
    elif not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO IntentoCorrecto (idUsuario, idCasilla, idImagen) VALUES (%s, %s, %s)',
                       (idUsuario, idCasilla, idImagen))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'IntentoCorrecto registrado'}), 201


@app.route('/intentoCorrecto/<int:id>', methods=['DELETE'])
def delete_intento_correcto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM IntentoCorrecto WHERE idCorrecto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'IntentoCorrecto eliminado'})

# Metodos para IntentoIncorrecto


@app.route('/intentoIncorrecto', methods=['GET'])
def get_intento_incorrecto():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM IntentoIncorrecto')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/intentoIncorrecto/<int:id>', methods=['GET'])
def get_one_intento_incorrecto(id):
    data = fetch_one_intento_incorrecto(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/intentoIncorrecto', methods=['POST'])
def create_intento_incorrecto():
    data = request.json
    opcionElegida = data['opcionElegida']
    idUsuario = data['idUsuario']
    idCasilla = data['idCasilla']
    idImagen = data['idImagen']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    casilla = fetch_one_casilla(idCasilla)
    imagen = fetch_one_imagen(idImagen)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    elif not casilla:
        return jsonify({'mensaje': 'La casilla especificada no existe'}), 400
    elif not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO IntentoIncorrecto (opcionElegida, idUsuario, idCasilla, idImagen) VALUES (%s, %s, %s, %s)',
                       (opcionElegida, idUsuario, idCasilla, idImagen))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'IntentoIncorrecto registrado'}), 201


@app.route('/intentoIncorrecto/<int:id>', methods=['DELETE'])
def delete_intento_incorrecto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM IntentoIncorrecto WHERE idIncorrecto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'IntentoIncorrecto eliminado'})


if __name__ == '__main__':
    app.run(debug=True, port=2025)

app = Flask(__name__)
CORS(app)

app.secret_key = 'your_secret_key'  # Replace with a strong, random secret key

# Database configuration
server = "localhost"
port = 1433
database = "master"
username = "sa"
password = "YourPassword123!"

# Database connection function


def get_connection():
    try:
        conn = pymssql.connect(
            server=server, port=port, database=database, user=username, password=password)
        return conn
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return None


# Metodos para recuperacion de contrasena
def enviar_correo(destinatario, asunto, cuerpo):
    message = Mail(
        from_email='rerreza@hotmail.es',  # Tu correo verificado
        to_emails=destinatario,
        subject=asunto,
        plain_text_content=cuerpo
    )
    try:
        # Sustituye tu API Key aquí
        sg = SendGridAPIClient(
            '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')
        response = sg.send(message)
        print(f'Correo enviado: {response.status_code}')
    except Exception as e:
        print(f'Error enviando correo: {e}')


@app.route('/recuperar', methods=['POST'])
def solicitar_recuperacion():
    data = request.json
    correo = data.get('contacto')

    if not correo:
        return jsonify({'error': 'Correo requerido'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Buscar usuario por correo (contacto)
        cursor.execute('''
            SELECT u.idUsuario 
            FROM Usuario u 
            INNER JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
            WHERE u.contacto = %s
        ''', (correo,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Correo no encontrado'}), 404

        # Generar código aleatorio
        codigo = random.randint(100000, 999999)

        # Enviar correo con el código
        enviar_correo(correo, 'Recuperación de Contraseña',
                      f'Tu código de recuperación es: {codigo}')

        # Puedes guardar el código temporalmente en una variable, o en BD para validarlo
        return jsonify({'mensaje': 'Correo enviado con el código de recuperación'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Metodos para el login


def verify_password(stored_password_hash, provided_password):
    hashed_provided_password = hashlib.sha1(
        provided_password.encode()).hexdigest()
    return stored_password_hash == hashed_provided_password


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Se requiere usuario y contraseña'}), 400

    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)

            # Buscar usuario y su contraseña usando JOIN
            cursor.execute('''
                SELECT u.idUsuario, u.usuario, un.contrasena
                FROM Usuario u
                JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
                WHERE u.usuario = %s
            ''', (username,))
            user = cursor.fetchone()

            if user and verify_password(user['contrasena'], password):
                session['username'] = username
                session['idUsuario'] = user['idUsuario']
                return jsonify({'mensaje': 'Autenticación exitosa', 'idUsuario': user['idUsuario'], 'username': username}), 200
            else:
                return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

        except Exception as e:
            return jsonify({'error': f'Error en BD {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


# Metodos para fetch y manejo de errores

def fetch_one_usuario(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT 
          u.idUsuario, 
          u.usuario, 
          u.idEvento,
          u.contacto,  -- Aquí puede ser correo o nombre de red social
          un.contrasena,
          CASE 
            WHEN un.idUsuario IS NOT NULL THEN 'Normal'
            WHEN ur.idUsuario IS NOT NULL THEN 'Red'
            ELSE 'Desconocido'
          END AS tipoUsuario
        FROM Usuario u
        LEFT JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
        LEFT JOIN UsuarioRed ur ON u.idUsuario = ur.idUsuario
        WHERE u.idUsuario = %s
    ''', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_boleto(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Boleto WHERE idBoleto = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_evento(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Evento WHERE idEvento = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_imagen(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Imagen WHERE idImagen = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_casilla(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Casilla WHERE idCasilla = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_pregunta(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Pregunta WHERE idPregunta = %s', (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        'idPregunta': row[0],
        'pregunta': row[1],
        'options': [
            {'option': 'A', 'text': row[2]},
            {'option': 'B', 'text': row[3]},
            {'option': 'C', 'text': row[4]},
            {'option': 'D', 'text': row[5]},
        ],
        # Si 'respuesta' es 'opcionD', se extrae 'D'
        'correctOption': row[6][-1],
        'timer': '00:30'
    }


def fetch_one_intento_correcto(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        'SELECT * FROM IntentoCorrecto WHERE idCorrecto = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_intento_incorrecto(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        'SELECT * FROM IntentoIncorrecto WHERE idIncorrecto = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


# Metodos para Usuario
@app.route('/usuario', methods=['GET'])
def get_usuarios():
    try:
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute('''
            SELECT 
              u.idUsuario, 
              u.usuario, 
              u.idEvento,
              u.contacto,  -- Puede ser correo o nombre de la red social
              un.contrasena,
              CASE 
                WHEN un.idUsuario IS NOT NULL THEN 'Normal'
                WHEN ur.idUsuario IS NOT NULL THEN 'Red'
                ELSE 'Desconocido'
              END AS tipoUsuario
            FROM Usuario u
            LEFT JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
            LEFT JOIN UsuarioRed ur ON u.idUsuario = ur.idUsuario
        ''')
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/usuariored', methods=['GET'])
def get_usuarios_red():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT 
          u.idUsuario, 
          u.usuario, 
          u.contacto,  -- contacto contiene el nombre de la red social
        FROM Usuario u
        INNER JOIN UsuarioRed ur ON u.idUsuario = ur.idUsuario
    ''')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/usuarionormal', methods=['GET'])
def get_usuarios_normal():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT 
          u.idUsuario, 
          u.usuario, 
          u.contacto AS correo,  -- contacto ahora guarda el correo para normales
          un.contrasena
        FROM Usuario u
        INNER JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
    ''')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/usuario/<int:id>', methods=['GET'])
def get_one_usuario(id):
    usuario = fetch_one_usuario(id)
    if usuario:
        return jsonify(usuario)
    else:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404


@app.route('/usuarionormal', methods=['POST'])
def create_usuario_normal():
    data = request.json
    usuario = data['usuario']
    correo = data['correo']
    contrasena = data['contrasena']

    conn = get_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        # Buscar evento en curso automáticamente
        cursor.execute('''
            SELECT TOP 1 idEvento 
            FROM Evento 
            WHERE fechaInicio <= GETDATE() AND fechaFinal >= GETDATE()
            ORDER BY fechaInicio DESC
        ''')
        evento = cursor.fetchone()

        if not evento:
            return jsonify({'error': 'No hay evento en curso'}), 400

        idEvento = evento['idEvento']

        # Insertar en Usuario con el correo como contacto
        cursor.execute(
            'INSERT INTO Usuario (usuario, idEvento, contacto) VALUES (%s, %s, %s)', (usuario, idEvento, correo))
        conn.commit()

        cursor.execute('SELECT SCOPE_IDENTITY() as idUsuario')
        idUsuario = cursor.fetchone()['idUsuario']

        # Insertar en UsuarioNormal (solo contrasena ahora)
        cursor.execute('INSERT INTO UsuarioNormal (idUsuario, contrasena) VALUES (%s, %s)',
                       (idUsuario, contrasena))
        conn.commit()

        return jsonify({'mensaje': 'Usuario normal creado', 'idUsuario': idUsuario}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/usuariored', methods=['POST'])
def create_usuario_red():
    data = request.json
    nombre = data['usuario']
    contacto = data['contacto']

    conn = get_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        # Buscar el evento en curso
        cursor.execute('''
            SELECT TOP 1 idEvento 
            FROM Evento 
            WHERE fechaInicio <= GETDATE() AND fechaFinal >= GETDATE()
            ORDER BY fechaInicio DESC
        ''')
        evento = cursor.fetchone()

        if not evento:
            return jsonify({'error': 'No hay evento en curso'}), 400

        idEvento = evento['idEvento']

        # Verificar si el usuario ya existe
        cursor.execute(
            'SELECT idUsuario FROM Usuario WHERE usuario = %s', (nombre,))
        existing = cursor.fetchone()

        if existing:
            idUsuario = existing['idUsuario']
            mensaje = 'Usuario ya existe'
        else:
            # Insertar en Usuario con contacto = nombre de red social
            cursor.execute(
                'INSERT INTO Usuario (usuario, idEvento, contacto) VALUES (%s, %s, %s)', (nombre, idEvento, contacto))
            conn.commit()

            cursor.execute('SELECT SCOPE_IDENTITY() AS idUsuario')
            idUsuario = cursor.fetchone()['idUsuario']

            # Insertar en UsuarioRed (solo tokenRed si se envía)
            cursor.execute('INSERT INTO UsuarioRed (idUsuario) VALUES (%s)',
                           (idUsuario))
            conn.commit()

            mensaje = 'Usuario red creado'

        return jsonify({'mensaje': mensaje, 'idUsuario': idUsuario}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/usuario/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.json
    usuario = data['usuario']
    idEvento = data['idEvento']
    tipo = data['tipoUsuario']

    # Validar si el usuario existe
    existing = fetch_one_usuario(id)
    if not existing:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404

    # Validar evento
    evento = fetch_one_evento(idEvento)
    if not evento:
        return jsonify({'mensaje': 'El evento especificado no existe'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if tipo == 'Normal':
            correo = data['contacto']
            contrasena = data['contrasena']

            # Actualizar Usuario con contacto = correo
            cursor.execute('UPDATE Usuario SET usuario = %s, idEvento = %s, contacto = %s WHERE idUsuario = %s',
                           (usuario, idEvento, correo, id))

            # Ver si ya existía en UsuarioNormal
            cursor.execute(
                'SELECT * FROM UsuarioNormal WHERE idUsuario = %s', (id,))
            if cursor.fetchone():
                cursor.execute('UPDATE UsuarioNormal SET contrasena = %s WHERE idUsuario = %s',
                               (contrasena, id))
            else:
                cursor.execute('INSERT INTO UsuarioNormal (idUsuario, contrasena) VALUES (%s, %s)',
                               (id, contrasena))

            # Asegurarse que no exista en UsuarioRed
            cursor.execute(
                'DELETE FROM UsuarioRed WHERE idUsuario = %s', (id,))

        elif tipo == 'Red':
            redSocial = data['contacto']

            # Actualizar Usuario con contacto = redSocial
            cursor.execute('UPDATE Usuario SET usuario = %s, idEvento = %s, contacto = %s WHERE idUsuario = %s',
                           (usuario, idEvento, redSocial, id))

            # Ver si ya existía en UsuarioRed
            cursor.execute(
                'SELECT * FROM UsuarioRed WHERE idUsuario = %s', (id,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO UsuarioRed (idUsuario) VALUES (%s, %s)',
                               (id))

            # Asegurarse que no exista en UsuarioNormal
            cursor.execute(
                'DELETE FROM UsuarioNormal WHERE idUsuario = %s', (id,))
        else:
            conn.rollback()
            return jsonify({'mensaje': 'Tipo de usuario inválido'}), 400

        conn.commit()
        return jsonify({'mensaje': 'Usuario actualizado'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/usuario/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    existing = fetch_one_usuario(id)
    if not existing:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Borrar de tablas hijas primero
        cursor.execute('DELETE FROM UsuarioNormal WHERE idUsuario = %s', (id,))
        cursor.execute('DELETE FROM UsuarioRed WHERE idUsuario = %s', (id,))
        cursor.execute('DELETE FROM Usuario WHERE idUsuario = %s', (id,))

        conn.commit()
        return jsonify({'mensaje': 'Usuario eliminado'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# Metodos para Boleto
@app.route('/boleto', methods=['GET'])
def get_boletos():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Boleto')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/boleto/<int:id>', methods=['GET'])
def get_one_boleto(id):
    data = fetch_one_boleto(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/boleto', methods=['POST'])
def create_boleto():
    data = request.json
    tipo = data['tipo']
    idUsuario = data['idUsuario']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Boleto (tipo, idUsuario) VALUES (%s, %s)', (tipo, idUsuario))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Boleto creado'}), 201


@app.route('/boleto/<int:id>', methods=['PUT'])
def update_boleto(id):
    data = request.json
    tipo = data['tipo']
    idUsuario = data['idUsuario']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE Boleto SET tipo = %s, idUsuario = %s WHERE idBoleto = %s', (tipo, idUsuario, id))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Boleto actualizado'})


@app.route('/boleto/<int:id>', methods=['DELETE'])
def delete_boleto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Boleto WHERE idBoleto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Boleto eliminado'})


# Metodos para Evento
@app.route('/evento', methods=['GET'])
def get_eventos():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Evento')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/evento/<int:id>', methods=['GET'])
def get_one_evento(id):
    data = fetch_one_evento(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/evento', methods=['POST'])
def create_evento():
    data = request.json
    fechaInicio = data['fechaInicio']
    fechaFinal = data['fechaFinal']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO Evento (fechaInicio, fechaFinal) VALUES (%s, %s)', (fechaInicio, fechaFinal))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Evento creado'}), 201


@app.route('/evento/<int:id>', methods=['PUT'])
def update_evento(id):
    data = request.json
    fechaInicio = data['fechaInicio']
    fechaFinal = data['fechaFinal']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Evento SET fechaInicio = %s, fechaFinal = %s WHERE idEvento = %s',
                   (fechaInicio, fechaFinal, id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Evento actualizado'})


@app.route('/evento/<int:id>', methods=['DELETE'])
def delete_evento(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Evento WHERE idEvento = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Evento eliminado'})


# Metodos para Imagen
@app.route('/imagen', methods=['GET'])
def get_imagenes():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Imagen')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/imagen/<int:id>', methods=['GET'])
def get_one_imagen(id):
    data = fetch_one_imagen(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/imagen', methods=['POST'])
def create_imagen():
    data = request.json
    url = data['URL']
    estado = data['estado']
    respuesta = data['respuesta']
    idEvento = data['idEvento']
    idUsuario = data.get('idUsuario')  # Optional field, can be NULL
    # Check if the event exists using the helper function
    evento = fetch_one_evento(idEvento)
    if not evento:
        return jsonify({'mensaje': 'El evento especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Imagen (URL, estado, respuesta, idEvento, idUsuario) VALUES (%s, %s, %s, %s, %s)',
                       (url, estado, respuesta, idEvento, idUsuario))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Imagen creada'}), 201


@app.route('/imagen/<int:id>', methods=['PUT'])
def update_imagen(id):
    data = request.json
    url = data['URL']
    estado = data['estado']
    respuesta = data['respuesta']
    idEvento = data['idEvento']
    idUsuario = data.get('idUsuario')  # Optional field, can be NULL
    # Check if the event exists using the helper function
    evento = fetch_one_evento(idEvento)
    if not evento:
        return jsonify({'mensaje': 'El evento especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE Imagen SET URL = %s, estado = %s, respuesta = %s, idEvento = %s, idUsuario = %s WHERE idImagen = %s',
                       (url, estado, respuesta, idEvento, idUsuario, id))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Imagen actualizada'})


@app.route('/imagen/<int:id>', methods=['DELETE'])
def delete_imagen(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Imagen WHERE idImagen = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Imagen eliminada'})


# Metodos para Casilla
@app.route('/casilla', methods=['GET'])
def get_casillas():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Casilla')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/casilla/<int:id>', methods=['GET'])
def get_one_casilla(id):
    data = fetch_one_casilla(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/casilla', methods=['POST'])
def create_casilla():
    data = request.json
    idImagen = data['idImagen']
    coordenadaX = data['coordenadaX']
    coordenadaY = data['coordenadaY']
    idPregunta = data['idPregunta']
    # Check if the image exists using the helper function
    imagen = fetch_one_imagen(idImagen)
    if not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        # Check if the question exists using the helper function
        pregunta = fetch_one_pregunta(idPregunta)
        if not pregunta:
            return jsonify({'mensaje': 'La pregunta especificada no existe'}), 400
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Casilla (idImagen, coordenadaX, coordenadaY, idPregunta) VALUES (%s, %s, %s, %s)',
                           (idImagen, coordenadaX, coordenadaY, idPregunta))
            conn.commit()
            conn.close()
            return jsonify({'mensaje': 'Casilla creada'}), 201


@app.route('/casilla/<int:id>', methods=['PUT'])
def update_casilla(id):
    data = request.json
    idImagen = data['idImagen']
    coordenadaX = data['coordenadaX']
    coordenadaY = data['coordenadaY']
    idPregunta = data['idPregunta']
    # Check if the image exists using the helper function
    imagen = fetch_one_imagen(idImagen)
    if not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        # Check if the question exists using the helper function
        pregunta = fetch_one_pregunta(idPregunta)
        if not pregunta:
            return jsonify({'mensaje': 'La pregunta especificada no existe'}), 400
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE Casilla SET idImagen = %s, coordenadaX = %s, coordenadaY = %s, idPregunta = %s WHERE idCasilla = %s',
                           (idImagen, coordenadaX, coordenadaY, idPregunta, id))
            conn.commit()
            conn.close()
            return jsonify({'mensaje': 'Casilla actualizada'})


@app.route('/casilla/<int:id>', methods=['DELETE'])
def delete_casilla(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Casilla WHERE idCasilla = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Casilla eliminada'})


# Metodos para Pregunta
@app.route('/pregunta', methods=['GET'])
def get_preguntas():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Pregunta')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/pregunta/<int:id>', methods=['GET'])
def get_one_pregunta(id):
    data = fetch_one_pregunta(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/pregunta', methods=['POST'])
def create_pregunta():
    data = request.json
    pregunta = data['pregunta']
    opcionA = data.get('opcionA')
    opcionB = data.get('opcionB')
    opcionC = data.get('opcionC')
    opcionD = data.get('opcionD')
    respuesta = data['respuesta']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES (%s, %s, %s, %s, %s, %s)',
                   (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta creada'}), 201


@app.route('/pregunta/<int:id>', methods=['PUT'])
def update_pregunta(id):
    data = request.json
    pregunta = data['pregunta']
    # se utiliza data.get() porque pueden ser NULL
    opcionA = data.get('opcionA')
    opcionB = data.get('opcionB')
    opcionC = data.get('opcionC')
    opcionD = data.get('opcionD')
    respuesta = data['respuesta']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Pregunta SET pregunta = %s, opcionA = %s, opcionB = %s, opcionC = %s, opcionD = %s, respuesta = %s WHERE idPregunta = %s',
                   (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta, id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta actualizada'})


@app.route('/pregunta/<int:id>', methods=['DELETE'])
def delete_pregunta(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Pregunta WHERE idPregunta = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta eliminada'})


# Metodos para IntentoCorrecto
@app.route('/intentoCorrecto', methods=['GET'])
def get_intentos_correctos():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM IntentoCorrecto')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/intentoCorrecto/<int:id>', methods=['GET'])
def get_one_intento_correcto(id):
    data = fetch_one_intento_correcto(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/intentoCorrecto', methods=['POST'])
def create_intento_correcto():
    data = request.json
    idUsuario = data['idUsuario']
    idCasilla = data['idCasilla']
    idImagen = data['idImagen']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    casilla = fetch_one_casilla(idCasilla)
    imagen = fetch_one_imagen(idImagen)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    elif not casilla:
        return jsonify({'mensaje': 'La casilla especificada no existe'}), 400
    elif not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO IntentoCorrecto (idUsuario, idCasilla, idImagen) VALUES (%s, %s, %s)',
                       (idUsuario, idCasilla, idImagen))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'IntentoCorrecto registrado'}), 201


@app.route('/intentoCorrecto/<int:id>', methods=['DELETE'])
def delete_intento_correcto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM IntentoCorrecto WHERE idCorrecto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'IntentoCorrecto eliminado'})

# Metodos para IntentoIncorrecto


@app.route('/intentoIncorrecto', methods=['GET'])
def get_intento_incorrecto():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM IntentoIncorrecto')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/intentoIncorrecto/<int:id>', methods=['GET'])
def get_one_intento_incorrecto(id):
    data = fetch_one_intento_incorrecto(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/intentoIncorrecto', methods=['POST'])
def create_intento_incorrecto():
    data = request.json
    opcionElegida = data['opcionElegida']
    idUsuario = data['idUsuario']
    idCasilla = data['idCasilla']
    idImagen = data['idImagen']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    casilla = fetch_one_casilla(idCasilla)
    imagen = fetch_one_imagen(idImagen)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    elif not casilla:
        return jsonify({'mensaje': 'La casilla especificada no existe'}), 400
    elif not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO IntentoIncorrecto (opcionElegida, idUsuario, idCasilla, idImagen) VALUES (%s, %s, %s, %s)',
                       (opcionElegida, idUsuario, idCasilla, idImagen))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'IntentoIncorrecto registrado'}), 201


@app.route('/intentoIncorrecto/<int:id>', methods=['DELETE'])
def delete_intento_incorrecto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM IntentoIncorrecto WHERE idIncorrecto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'IntentoIncorrecto eliminado'})


if __name__ == '__main__':
    app.run(debug=True, port=2025)

codigos_recuperacion = {}  # {correo: codigo}

app = Flask(__name__)
CORS(app)

app.secret_key = 'your_secret_key'  # Replace with a strong, random secret key

# Database configuration
server = "localhost"
port = 1433
database = "master"
username = "sa"
password = "YourPassword123!"

# Database connection function


def get_connection():
    try:
        conn = pymssql.connect(
            server=server, port=port, database=database, user=username, password=password)
        return conn
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return None


# Metodos para recuperacion de contrasena
def enviar_correo(destinatario, asunto, cuerpo):
    message = Mail(
        from_email='rerreza@hotmail.es',  # Tu correo verificado
        to_emails=destinatario,
        subject=asunto,
        plain_text_content=cuerpo
    )
    try:
        # Sustituye tu API Key aquí
        sg = SendGridAPIClient(
            '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')
        response = sg.send(message)
        print(f'Correo enviado: {response.status_code}')
    except Exception as e:
        print(f'Error enviando correo: {e}')

# Funciones para recuperar contrasena


@app.route('/recuperar', methods=['POST'])
def solicitar_recuperacion():
    data = request.json
    correo = data.get('correo')

    if not correo:
        return jsonify({'error': 'Correo requerido'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.idUsuario 
            FROM Usuario u 
            INNER JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
            WHERE u.contacto = %s
        ''', (correo,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Correo no encontrado'}), 404

        # Generar código
        codigo = random.randint(100000, 999999)

        # Guardar en memoria temporal
        codigos_recuperacion[correo] = codigo

        # Enviar correo
        enviar_correo(correo, 'Recuperación de Contraseña',
                      f'Tu código de recuperación es: {codigo}')

        return jsonify({'mensaje': 'Correo enviado con el código de recuperación'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/validarcodigo', methods=['POST'])
def validar_codigo():
    data = request.json
    correo = data.get('correo')
    codigo = data.get('codigo')
    nueva_contrasena = data.get('nuevaContrasena')

    if not correo or not codigo or not nueva_contrasena:
        return jsonify({'error': 'Correo, código y nueva contraseña requeridos'}), 400

    # Validar código
    if codigos_recuperacion.get(correo) != int(codigo):
        return jsonify({'error': 'Código incorrecto'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Buscar idUsuario
        cursor.execute('''
            SELECT u.idUsuario 
            FROM Usuario u 
            INNER JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
            WHERE u.contacto = %s
        ''', (correo,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Correo no encontrado'}), 404

        idUsuario = user[0]

        # Actualizar contraseña
        hashed_password = hashlib.sha1(nueva_contrasena.encode()).hexdigest()
        cursor.execute('UPDATE UsuarioNormal SET contrasena = %s WHERE idUsuario = %s',
                       (hashed_password, idUsuario))
        conn.commit()

        # Eliminar el código una vez usado
        del codigos_recuperacion[correo]

        return jsonify({'mensaje': 'Contraseña actualizada correctamente'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# Metodos para el login
def verify_password(stored_password_hash, provided_password):
    hashed_provided_password = hashlib.sha1(
        provided_password.encode()).hexdigest()
    return stored_password_hash == hashed_provided_password


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Se requiere usuario y contraseña'}), 400

    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)

            # Buscar usuario y su contraseña usando JOIN
            cursor.execute('''
                SELECT u.idUsuario, u.usuario, un.contrasena
                FROM Usuario u
                JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
                WHERE u.usuario = %s
            ''', (username,))
            user = cursor.fetchone()

            if user and verify_password(user['contrasena'], password):
                session['username'] = username
                session['idUsuario'] = user['idUsuario']
                return jsonify({'mensaje': 'Autenticación exitosa', 'idUsuario': user['idUsuario'], 'username': username}), 200
            else:
                return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

        except Exception as e:
            return jsonify({'error': f'Error en BD {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


# Metodos para fetch y manejo de errores

def fetch_one_usuario(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT 
          u.idUsuario, 
          u.usuario, 
          u.idEvento,
          u.contacto,  -- Aquí puede ser correo o nombre de red social
          un.contrasena,
          CASE 
            WHEN un.idUsuario IS NOT NULL THEN 'Normal'
            WHEN ur.idUsuario IS NOT NULL THEN 'Red'
            ELSE 'Desconocido'
          END AS tipoUsuario
        FROM Usuario u
        LEFT JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
        LEFT JOIN UsuarioRed ur ON u.idUsuario = ur.idUsuario
        WHERE u.idUsuario = %s
    ''', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_boleto(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Boleto WHERE idBoleto = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_evento(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Evento WHERE idEvento = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_imagen(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Imagen WHERE idImagen = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_casilla(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Casilla WHERE idCasilla = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_pregunta(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Pregunta WHERE idPregunta = %s', (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        'idPregunta': row[0],
        'pregunta': row[1],
        'options': [
            {'option': 'A', 'text': row[2]},
            {'option': 'B', 'text': row[3]},
            {'option': 'C', 'text': row[4]},
            {'option': 'D', 'text': row[5]},
        ],
        # Si 'respuesta' es 'opcionD', se extrae 'D'
        'correctOption': row[6][-1],
        'timer': '00:30'
    }


def fetch_one_intento_correcto(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        'SELECT * FROM IntentoCorrecto WHERE idCorrecto = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_intento_incorrecto(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        'SELECT * FROM IntentoIncorrecto WHERE idIncorrecto = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


# Metodos para Usuario
@app.route('/usuario', methods=['GET'])
def get_usuarios():
    try:
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute('''
            SELECT 
              u.idUsuario, 
              u.usuario, 
              u.idEvento,
              u.contacto,  -- Puede ser correo o nombre de la red social
              un.contrasena,
              CASE 
                WHEN un.idUsuario IS NOT NULL THEN 'Normal'
                WHEN ur.idUsuario IS NOT NULL THEN 'Red'
                ELSE 'Desconocido'
              END AS tipoUsuario
            FROM Usuario u
            LEFT JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
            LEFT JOIN UsuarioRed ur ON u.idUsuario = ur.idUsuario
        ''')
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/usuariored', methods=['GET'])
def get_usuarios_red():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT 
          u.idUsuario, 
          u.usuario, 
          u.contacto,  -- contacto contiene el nombre de la red social
        FROM Usuario u
        INNER JOIN UsuarioRed ur ON u.idUsuario = ur.idUsuario
    ''')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/usuarionormal', methods=['GET'])
def get_usuarios_normal():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT 
          u.idUsuario, 
          u.usuario, 
          u.contacto AS correo,  -- contacto ahora guarda el correo para normales
          un.contrasena
        FROM Usuario u
        INNER JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
    ''')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/usuario/<int:id>', methods=['GET'])
def get_one_usuario(id):
    usuario = fetch_one_usuario(id)
    if usuario:
        return jsonify(usuario)
    else:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404


@app.route('/usuarionormal', methods=['POST'])
def create_usuario_normal():
    data = request.json
    usuario = data['usuario']
    correo = data['correo']
    contrasena = data['contrasena']

    conn = get_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        # Buscar evento en curso automáticamente
        cursor.execute('''
            SELECT TOP 1 idEvento 
            FROM Evento 
            WHERE fechaInicio <= GETDATE() AND fechaFinal >= GETDATE()
            ORDER BY fechaInicio DESC
        ''')
        evento = cursor.fetchone()

        if not evento:
            return jsonify({'error': 'No hay evento en curso'}), 400

        idEvento = evento['idEvento']

        # Insertar en Usuario con el correo como contacto
        cursor.execute(
            'INSERT INTO Usuario (usuario, idEvento, contacto) VALUES (%s, %s, %s)', (usuario, idEvento, correo))
        conn.commit()

        cursor.execute('SELECT SCOPE_IDENTITY() as idUsuario')
        idUsuario = cursor.fetchone()['idUsuario']

        # Insertar en UsuarioNormal (solo contrasena ahora)
        cursor.execute('INSERT INTO UsuarioNormal (idUsuario, contrasena) VALUES (%s, %s)',
                       (idUsuario, contrasena))
        conn.commit()

        return jsonify({'mensaje': 'Usuario normal creado', 'idUsuario': idUsuario}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/usuariored', methods=['POST'])
def create_usuario_red():
    data = request.json
    nombre = data['usuario']
    contacto = data['contacto']

    conn = get_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        # Buscar el evento en curso
        cursor.execute('''
            SELECT TOP 1 idEvento 
            FROM Evento 
            WHERE fechaInicio <= GETDATE() AND fechaFinal >= GETDATE()
            ORDER BY fechaInicio DESC
        ''')
        evento = cursor.fetchone()

        if not evento:
            return jsonify({'error': 'No hay evento en curso'}), 400

        idEvento = evento['idEvento']

        # Verificar si el usuario ya existe
        cursor.execute(
            'SELECT idUsuario FROM Usuario WHERE usuario = %s', (nombre,))
        existing = cursor.fetchone()

        if existing:
            idUsuario = existing['idUsuario']
            mensaje = 'Usuario ya existe'
        else:
            # Insertar en Usuario con contacto = nombre de red social
            cursor.execute(
                'INSERT INTO Usuario (usuario, idEvento, contacto) VALUES (%s, %s, %s)', (nombre, idEvento, contacto))
            conn.commit()

            cursor.execute('SELECT SCOPE_IDENTITY() AS idUsuario')
            idUsuario = cursor.fetchone()['idUsuario']

            # Insertar en UsuarioRed (solo tokenRed si se envía)
            cursor.execute('INSERT INTO UsuarioRed (idUsuario) VALUES (%s)',
                           (idUsuario))
            conn.commit()

            mensaje = 'Usuario red creado'

        return jsonify({'mensaje': mensaje, 'idUsuario': idUsuario}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/usuario/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.json
    usuario = data['usuario']
    idEvento = data['idEvento']
    tipo = data['tipoUsuario']

    # Validar si el usuario existe
    existing = fetch_one_usuario(id)
    if not existing:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404

    # Validar evento
    evento = fetch_one_evento(idEvento)
    if not evento:
        return jsonify({'mensaje': 'El evento especificado no existe'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if tipo == 'Normal':
            correo = data['contacto']
            contrasena = data['contrasena']

            # Actualizar Usuario con contacto = correo
            cursor.execute('UPDATE Usuario SET usuario = %s, idEvento = %s, contacto = %s WHERE idUsuario = %s',
                           (usuario, idEvento, correo, id))

            # Ver si ya existía en UsuarioNormal
            cursor.execute(
                'SELECT * FROM UsuarioNormal WHERE idUsuario = %s', (id,))
            if cursor.fetchone():
                cursor.execute('UPDATE UsuarioNormal SET contrasena = %s WHERE idUsuario = %s',
                               (contrasena, id))
            else:
                cursor.execute('INSERT INTO UsuarioNormal (idUsuario, contrasena) VALUES (%s, %s)',
                               (id, contrasena))

            # Asegurarse que no exista en UsuarioRed
            cursor.execute(
                'DELETE FROM UsuarioRed WHERE idUsuario = %s', (id,))

        elif tipo == 'Red':
            redSocial = data['contacto']

            # Actualizar Usuario con contacto = redSocial
            cursor.execute('UPDATE Usuario SET usuario = %s, idEvento = %s, contacto = %s WHERE idUsuario = %s',
                           (usuario, idEvento, redSocial, id))

            # Ver si ya existía en UsuarioRed
            cursor.execute(
                'SELECT * FROM UsuarioRed WHERE idUsuario = %s', (id,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO UsuarioRed (idUsuario) VALUES (%s, %s)',
                               (id))

            # Asegurarse que no exista en UsuarioNormal
            cursor.execute(
                'DELETE FROM UsuarioNormal WHERE idUsuario = %s', (id,))
        else:
            conn.rollback()
            return jsonify({'mensaje': 'Tipo de usuario inválido'}), 400

        conn.commit()
        return jsonify({'mensaje': 'Usuario actualizado'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/usuario/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    existing = fetch_one_usuario(id)
    if not existing:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Borrar de tablas hijas primero
        cursor.execute('DELETE FROM UsuarioNormal WHERE idUsuario = %s', (id,))
        cursor.execute('DELETE FROM UsuarioRed WHERE idUsuario = %s', (id,))
        cursor.execute('DELETE FROM Usuario WHERE idUsuario = %s', (id,))

        conn.commit()
        return jsonify({'mensaje': 'Usuario eliminado'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# Metodos para Boleto
@app.route('/boleto', methods=['GET'])
def get_boletos():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Boleto')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/boleto/<int:id>', methods=['GET'])
def get_one_boleto(id):
    data = fetch_one_boleto(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/boleto', methods=['POST'])
def create_boleto():
    data = request.json
    tipo = data['tipo']
    idUsuario = data['idUsuario']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Boleto (tipo, idUsuario) VALUES (%s, %s)', (tipo, idUsuario))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Boleto creado'}), 201


@app.route('/boleto/<int:id>', methods=['PUT'])
def update_boleto(id):
    data = request.json
    tipo = data['tipo']
    idUsuario = data['idUsuario']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE Boleto SET tipo = %s, idUsuario = %s WHERE idBoleto = %s', (tipo, idUsuario, id))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Boleto actualizado'})


@app.route('/boleto/<int:id>', methods=['DELETE'])
def delete_boleto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Boleto WHERE idBoleto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Boleto eliminado'})


# Metodos para Evento
@app.route('/evento', methods=['GET'])
def get_eventos():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Evento')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/evento/<int:id>', methods=['GET'])
def get_one_evento(id):
    data = fetch_one_evento(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/evento', methods=['POST'])
def create_evento():
    data = request.json
    fechaInicio = data['fechaInicio']
    fechaFinal = data['fechaFinal']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO Evento (fechaInicio, fechaFinal) VALUES (%s, %s)', (fechaInicio, fechaFinal))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Evento creado'}), 201


@app.route('/evento/<int:id>', methods=['PUT'])
def update_evento(id):
    data = request.json
    fechaInicio = data['fechaInicio']
    fechaFinal = data['fechaFinal']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Evento SET fechaInicio = %s, fechaFinal = %s WHERE idEvento = %s',
                   (fechaInicio, fechaFinal, id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Evento actualizado'})


@app.route('/evento/<int:id>', methods=['DELETE'])
def delete_evento(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Evento WHERE idEvento = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Evento eliminado'})


# Metodos para Imagen
@app.route('/imagen', methods=['GET'])
def get_imagenes():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Imagen')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/imagen/<int:id>', methods=['GET'])
def get_one_imagen(id):
    data = fetch_one_imagen(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/imagen', methods=['POST'])
def create_imagen():
    data = request.json
    url = data['URL']
    estado = data['estado']
    respuesta = data['respuesta']
    idEvento = data['idEvento']
    idUsuario = data.get('idUsuario')  # Optional field, can be NULL
    # Check if the event exists using the helper function
    evento = fetch_one_evento(idEvento)
    if not evento:
        return jsonify({'mensaje': 'El evento especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Imagen (URL, estado, respuesta, idEvento, idUsuario) VALUES (%s, %s, %s, %s, %s)',
                       (url, estado, respuesta, idEvento, idUsuario))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Imagen creada'}), 201


@app.route('/imagen/<int:id>', methods=['PUT'])
def update_imagen(id):
    data = request.json
    url = data['URL']
    estado = data['estado']
    respuesta = data['respuesta']
    idEvento = data['idEvento']
    idUsuario = data.get('idUsuario')  # Optional field, can be NULL
    # Check if the event exists using the helper function
    evento = fetch_one_evento(idEvento)
    if not evento:
        return jsonify({'mensaje': 'El evento especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE Imagen SET URL = %s, estado = %s, respuesta = %s, idEvento = %s, idUsuario = %s WHERE idImagen = %s',
                       (url, estado, respuesta, idEvento, idUsuario, id))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Imagen actualizada'})


@app.route('/imagen/<int:id>', methods=['DELETE'])
def delete_imagen(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Imagen WHERE idImagen = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Imagen eliminada'})


# Metodos para Casilla
@app.route('/casilla', methods=['GET'])
def get_casillas():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Casilla')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/casilla/<int:id>', methods=['GET'])
def get_one_casilla(id):
    data = fetch_one_casilla(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/casilla', methods=['POST'])
def create_casilla():
    data = request.json
    idImagen = data['idImagen']
    coordenadaX = data['coordenadaX']
    coordenadaY = data['coordenadaY']
    idPregunta = data['idPregunta']
    # Check if the image exists using the helper function
    imagen = fetch_one_imagen(idImagen)
    if not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        # Check if the question exists using the helper function
        pregunta = fetch_one_pregunta(idPregunta)
        if not pregunta:
            return jsonify({'mensaje': 'La pregunta especificada no existe'}), 400
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Casilla (idImagen, coordenadaX, coordenadaY, idPregunta) VALUES (%s, %s, %s, %s)',
                           (idImagen, coordenadaX, coordenadaY, idPregunta))
            conn.commit()
            conn.close()
            return jsonify({'mensaje': 'Casilla creada'}), 201


@app.route('/casilla/<int:id>', methods=['PUT'])
def update_casilla(id):
    data = request.json
    idImagen = data['idImagen']
    coordenadaX = data['coordenadaX']
    coordenadaY = data['coordenadaY']
    idPregunta = data['idPregunta']
    # Check if the image exists using the helper function
    imagen = fetch_one_imagen(idImagen)
    if not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        # Check if the question exists using the helper function
        pregunta = fetch_one_pregunta(idPregunta)
        if not pregunta:
            return jsonify({'mensaje': 'La pregunta especificada no existe'}), 400
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE Casilla SET idImagen = %s, coordenadaX = %s, coordenadaY = %s, idPregunta = %s WHERE idCasilla = %s',
                           (idImagen, coordenadaX, coordenadaY, idPregunta, id))
            conn.commit()
            conn.close()
            return jsonify({'mensaje': 'Casilla actualizada'})


@app.route('/casilla/<int:id>', methods=['DELETE'])
def delete_casilla(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Casilla WHERE idCasilla = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Casilla eliminada'})


# Metodos para Pregunta
@app.route('/pregunta', methods=['GET'])
def get_preguntas():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Pregunta')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/pregunta/<int:id>', methods=['GET'])
def get_one_pregunta(id):
    data = fetch_one_pregunta(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/pregunta', methods=['POST'])
def create_pregunta():
    data = request.json
    pregunta = data['pregunta']
    opcionA = data.get('opcionA')
    opcionB = data.get('opcionB')
    opcionC = data.get('opcionC')
    opcionD = data.get('opcionD')
    respuesta = data['respuesta']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES (%s, %s, %s, %s, %s, %s)',
                   (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta creada'}), 201


@app.route('/pregunta/<int:id>', methods=['PUT'])
def update_pregunta(id):
    data = request.json
    pregunta = data['pregunta']
    # se utiliza data.get() porque pueden ser NULL
    opcionA = data.get('opcionA')
    opcionB = data.get('opcionB')
    opcionC = data.get('opcionC')
    opcionD = data.get('opcionD')
    respuesta = data['respuesta']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Pregunta SET pregunta = %s, opcionA = %s, opcionB = %s, opcionC = %s, opcionD = %s, respuesta = %s WHERE idPregunta = %s',
                   (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta, id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta actualizada'})


@app.route('/pregunta/<int:id>', methods=['DELETE'])
def delete_pregunta(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Pregunta WHERE idPregunta = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta eliminada'})


# Metodos para IntentoCorrecto
@app.route('/intentoCorrecto', methods=['GET'])
def get_intentos_correctos():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM IntentoCorrecto')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/intentoCorrecto/<int:id>', methods=['GET'])
def get_one_intento_correcto(id):
    data = fetch_one_intento_correcto(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/intentoCorrecto', methods=['POST'])
def create_intento_correcto():
    data = request.json
    idUsuario = data['idUsuario']
    idCasilla = data['idCasilla']
    idImagen = data['idImagen']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    casilla = fetch_one_casilla(idCasilla)
    imagen = fetch_one_imagen(idImagen)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    elif not casilla:
        return jsonify({'mensaje': 'La casilla especificada no existe'}), 400
    elif not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO IntentoCorrecto (idUsuario, idCasilla, idImagen) VALUES (%s, %s, %s)',
                       (idUsuario, idCasilla, idImagen))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'IntentoCorrecto registrado'}), 201


@app.route('/intentoCorrecto/<int:id>', methods=['DELETE'])
def delete_intento_correcto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM IntentoCorrecto WHERE idCorrecto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'IntentoCorrecto eliminado'})

# Metodos para IntentoIncorrecto


@app.route('/intentoIncorrecto', methods=['GET'])
def get_intento_incorrecto():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM IntentoIncorrecto')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/intentoIncorrecto/<int:id>', methods=['GET'])
def get_one_intento_incorrecto(id):
    data = fetch_one_intento_incorrecto(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/intentoIncorrecto', methods=['POST'])
def create_intento_incorrecto():
    data = request.json
    opcionElegida = data['opcionElegida']
    idUsuario = data['idUsuario']
    idCasilla = data['idCasilla']
    idImagen = data['idImagen']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    casilla = fetch_one_casilla(idCasilla)
    imagen = fetch_one_imagen(idImagen)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    elif not casilla:
        return jsonify({'mensaje': 'La casilla especificada no existe'}), 400
    elif not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO IntentoIncorrecto (opcionElegida, idUsuario, idCasilla, idImagen) VALUES (%s, %s, %s, %s)',
                       (opcionElegida, idUsuario, idCasilla, idImagen))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'IntentoIncorrecto registrado'}), 201


@app.route('/intentoIncorrecto/<int:id>', methods=['DELETE'])
def delete_intento_incorrecto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM IntentoIncorrecto WHERE idIncorrecto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'IntentoIncorrecto eliminado'})


if __name__ == '__main__':
    app.run(debug=True, port=2025)

app = Flask(__name__)
CORS(app)

app.secret_key = 'your_secret_key'  # Replace with a strong, random secret key

# Database configuration
server = "localhost"
port = 1433
database = "master"
username = "sa"
password = "YourPassword123!"

# Database connection function


def get_connection():
    try:
        conn = pymssql.connect(
            server=server, port=port, database=database, user=username, password=password)
        return conn
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return None


# Metodos para recuperacion de contrasena
def enviar_correo(destinatario, asunto, cuerpo):
    message = Mail(
        from_email='rerreza@hotmail.es',  # Tu correo verificado
        to_emails=destinatario,
        subject=asunto,
        plain_text_content=cuerpo
    )
    try:
        # Sustituye tu API Key aquí
        sg = SendGridAPIClient(
            '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')
        response = sg.send(message)
        print(f'Correo enviado: {response.status_code}')
    except Exception as e:
        print(f'Error enviando correo: {e}')


@app.route('/recuperar', methods=['POST'])
def solicitar_recuperacion():
    data = request.json
    correo = data.get('contacto')

    if not correo:
        return jsonify({'error': 'Correo requerido'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Buscar usuario por correo (contacto)
        cursor.execute('''
            SELECT u.idUsuario 
            FROM Usuario u 
            INNER JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
            WHERE u.contacto = %s
        ''', (correo,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Correo no encontrado'}), 404

        # Generar código aleatorio
        codigo = random.randint(100000, 999999)

        # Enviar correo con el código
        enviar_correo(correo, 'Recuperación de Contraseña',
                      f'Tu código de recuperación es: {codigo}')

        # Puedes guardar el código temporalmente en una variable, o en BD para validarlo
        return jsonify({'mensaje': 'Correo enviado con el código de recuperación'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Metodos para el login


def verify_password(stored_password_hash, provided_password):
    hashed_provided_password = hashlib.sha1(
        provided_password.encode()).hexdigest()
    return stored_password_hash == hashed_provided_password


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Se requiere usuario y contraseña'}), 400

    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)

            # Buscar usuario y su contraseña usando JOIN
            cursor.execute('''
                SELECT u.idUsuario, u.usuario, un.contrasena
                FROM Usuario u
                JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
                WHERE u.usuario = %s
            ''', (username,))
            user = cursor.fetchone()

            if user and verify_password(user['contrasena'], password):
                session['username'] = username
                session['idUsuario'] = user['idUsuario']
                return jsonify({'mensaje': 'Autenticación exitosa', 'idUsuario': user['idUsuario'], 'username': username}), 200
            else:
                return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

        except Exception as e:
            return jsonify({'error': f'Error en BD {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


# Metodos para fetch y manejo de errores

def fetch_one_usuario(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT 
          u.idUsuario, 
          u.usuario, 
          u.idEvento,
          u.contacto,  -- Aquí puede ser correo o nombre de red social
          un.contrasena,
          CASE 
            WHEN un.idUsuario IS NOT NULL THEN 'Normal'
            WHEN ur.idUsuario IS NOT NULL THEN 'Red'
            ELSE 'Desconocido'
          END AS tipoUsuario
        FROM Usuario u
        LEFT JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
        LEFT JOIN UsuarioRed ur ON u.idUsuario = ur.idUsuario
        WHERE u.idUsuario = %s
    ''', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_boleto(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Boleto WHERE idBoleto = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_evento(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Evento WHERE idEvento = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_imagen(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Imagen WHERE idImagen = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_casilla(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Casilla WHERE idCasilla = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_pregunta(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Pregunta WHERE idPregunta = %s', (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        'idPregunta': row[0],
        'pregunta': row[1],
        'options': [
            {'option': 'A', 'text': row[2]},
            {'option': 'B', 'text': row[3]},
            {'option': 'C', 'text': row[4]},
            {'option': 'D', 'text': row[5]},
        ],
        # Si 'respuesta' es 'opcionD', se extrae 'D'
        'correctOption': row[6][-1],
        'timer': '00:30'
    }


def fetch_one_intento_correcto(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        'SELECT * FROM IntentoCorrecto WHERE idCorrecto = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def fetch_one_intento_incorrecto(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        'SELECT * FROM IntentoIncorrecto WHERE idIncorrecto = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    return data


# Metodos para Usuario
@app.route('/usuario', methods=['GET'])
def get_usuarios():
    try:
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute('''
            SELECT 
              u.idUsuario, 
              u.usuario, 
              u.idEvento,
              u.contacto,  -- Puede ser correo o nombre de la red social
              un.contrasena,
              CASE 
                WHEN un.idUsuario IS NOT NULL THEN 'Normal'
                WHEN ur.idUsuario IS NOT NULL THEN 'Red'
                ELSE 'Desconocido'
              END AS tipoUsuario
            FROM Usuario u
            LEFT JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
            LEFT JOIN UsuarioRed ur ON u.idUsuario = ur.idUsuario
        ''')
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/usuariored', methods=['GET'])
def get_usuarios_red():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT 
          u.idUsuario, 
          u.usuario, 
          u.contacto,  -- contacto contiene el nombre de la red social
        FROM Usuario u
        INNER JOIN UsuarioRed ur ON u.idUsuario = ur.idUsuario
    ''')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/usuarionormal', methods=['GET'])
def get_usuarios_normal():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT 
          u.idUsuario, 
          u.usuario, 
          u.contacto AS correo,  -- contacto ahora guarda el correo para normales
          un.contrasena
        FROM Usuario u
        INNER JOIN UsuarioNormal un ON u.idUsuario = un.idUsuario
    ''')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/usuario/<int:id>', methods=['GET'])
def get_one_usuario(id):
    usuario = fetch_one_usuario(id)
    if usuario:
        return jsonify(usuario)
    else:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404


@app.route('/usuarionormal', methods=['POST'])
def create_usuario_normal():
    data = request.json
    usuario = data['usuario']
    correo = data['correo']
    contrasena = data['contrasena']

    conn = get_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        # Buscar evento en curso automáticamente
        cursor.execute('''
            SELECT TOP 1 idEvento 
            FROM Evento 
            WHERE fechaInicio <= GETDATE() AND fechaFinal >= GETDATE()
            ORDER BY fechaInicio DESC
        ''')
        evento = cursor.fetchone()

        if not evento:
            return jsonify({'error': 'No hay evento en curso'}), 400

        idEvento = evento['idEvento']

        # Insertar en Usuario con el correo como contacto
        cursor.execute(
            'INSERT INTO Usuario (usuario, idEvento, contacto) VALUES (%s, %s, %s)', (usuario, idEvento, correo))
        conn.commit()

        cursor.execute('SELECT SCOPE_IDENTITY() as idUsuario')
        idUsuario = cursor.fetchone()['idUsuario']

        # Insertar en UsuarioNormal (solo contrasena ahora)
        cursor.execute('INSERT INTO UsuarioNormal (idUsuario, contrasena) VALUES (%s, %s)',
                       (idUsuario, contrasena))
        conn.commit()

        return jsonify({'mensaje': 'Usuario normal creado', 'idUsuario': idUsuario}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/usuariored', methods=['POST'])
def create_usuario_red():
    data = request.json
    nombre = data['usuario']
    contacto = data['contacto']

    conn = get_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        # Buscar el evento en curso
        cursor.execute('''
            SELECT TOP 1 idEvento 
            FROM Evento 
            WHERE fechaInicio <= GETDATE() AND fechaFinal >= GETDATE()
            ORDER BY fechaInicio DESC
        ''')
        evento = cursor.fetchone()

        if not evento:
            return jsonify({'error': 'No hay evento en curso'}), 400

        idEvento = evento['idEvento']

        # Verificar si el usuario ya existe
        cursor.execute(
            'SELECT idUsuario FROM Usuario WHERE usuario = %s', (nombre,))
        existing = cursor.fetchone()

        if existing:
            idUsuario = existing['idUsuario']
            mensaje = 'Usuario ya existe'
        else:
            # Insertar en Usuario con contacto = nombre de red social
            cursor.execute(
                'INSERT INTO Usuario (usuario, idEvento, contacto) VALUES (%s, %s, %s)', (nombre, idEvento, contacto))
            conn.commit()

            cursor.execute('SELECT SCOPE_IDENTITY() AS idUsuario')
            idUsuario = cursor.fetchone()['idUsuario']

            # Insertar en UsuarioRed (solo tokenRed si se envía)
            cursor.execute('INSERT INTO UsuarioRed (idUsuario) VALUES (%s)',
                           (idUsuario))
            conn.commit()

            mensaje = 'Usuario red creado'

        return jsonify({'mensaje': mensaje, 'idUsuario': idUsuario}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/usuario/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.json
    usuario = data['usuario']
    idEvento = data['idEvento']
    tipo = data['tipoUsuario']

    # Validar si el usuario existe
    existing = fetch_one_usuario(id)
    if not existing:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404

    # Validar evento
    evento = fetch_one_evento(idEvento)
    if not evento:
        return jsonify({'mensaje': 'El evento especificado no existe'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if tipo == 'Normal':
            correo = data['contacto']
            contrasena = data['contrasena']

            # Actualizar Usuario con contacto = correo
            cursor.execute('UPDATE Usuario SET usuario = %s, idEvento = %s, contacto = %s WHERE idUsuario = %s',
                           (usuario, idEvento, correo, id))

            # Ver si ya existía en UsuarioNormal
            cursor.execute(
                'SELECT * FROM UsuarioNormal WHERE idUsuario = %s', (id,))
            if cursor.fetchone():
                cursor.execute('UPDATE UsuarioNormal SET contrasena = %s WHERE idUsuario = %s',
                               (contrasena, id))
            else:
                cursor.execute('INSERT INTO UsuarioNormal (idUsuario, contrasena) VALUES (%s, %s)',
                               (id, contrasena))

            # Asegurarse que no exista en UsuarioRed
            cursor.execute(
                'DELETE FROM UsuarioRed WHERE idUsuario = %s', (id,))

        elif tipo == 'Red':
            redSocial = data['contacto']

            # Actualizar Usuario con contacto = redSocial
            cursor.execute('UPDATE Usuario SET usuario = %s, idEvento = %s, contacto = %s WHERE idUsuario = %s',
                           (usuario, idEvento, redSocial, id))

            # Ver si ya existía en UsuarioRed
            cursor.execute(
                'SELECT * FROM UsuarioRed WHERE idUsuario = %s', (id,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO UsuarioRed (idUsuario) VALUES (%s, %s)',
                               (id))

            # Asegurarse que no exista en UsuarioNormal
            cursor.execute(
                'DELETE FROM UsuarioNormal WHERE idUsuario = %s', (id,))
        else:
            conn.rollback()
            return jsonify({'mensaje': 'Tipo de usuario inválido'}), 400

        conn.commit()
        return jsonify({'mensaje': 'Usuario actualizado'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/usuario/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    existing = fetch_one_usuario(id)
    if not existing:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Borrar de tablas hijas primero
        cursor.execute('DELETE FROM UsuarioNormal WHERE idUsuario = %s', (id,))
        cursor.execute('DELETE FROM UsuarioRed WHERE idUsuario = %s', (id,))
        cursor.execute('DELETE FROM Usuario WHERE idUsuario = %s', (id,))

        conn.commit()
        return jsonify({'mensaje': 'Usuario eliminado'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# Metodos para Boleto
@app.route('/boleto', methods=['GET'])
def get_boletos():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Boleto')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/boleto/<int:id>', methods=['GET'])
def get_one_boleto(id):
    data = fetch_one_boleto(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/boleto', methods=['POST'])
def create_boleto():
    data = request.json
    tipo = data['tipo']
    idUsuario = data['idUsuario']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Boleto (tipo, idUsuario) VALUES (%s, %s)', (tipo, idUsuario))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Boleto creado'}), 201


@app.route('/boleto/<int:id>', methods=['PUT'])
def update_boleto(id):
    data = request.json
    tipo = data['tipo']
    idUsuario = data['idUsuario']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE Boleto SET tipo = %s, idUsuario = %s WHERE idBoleto = %s', (tipo, idUsuario, id))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Boleto actualizado'})


@app.route('/boleto/<int:id>', methods=['DELETE'])
def delete_boleto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Boleto WHERE idBoleto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Boleto eliminado'})


# Metodos para Evento
@app.route('/evento', methods=['GET'])
def get_eventos():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Evento')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/evento/<int:id>', methods=['GET'])
def get_one_evento(id):
    data = fetch_one_evento(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/evento', methods=['POST'])
def create_evento():
    data = request.json
    fechaInicio = data['fechaInicio']
    fechaFinal = data['fechaFinal']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO Evento (fechaInicio, fechaFinal) VALUES (%s, %s)', (fechaInicio, fechaFinal))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Evento creado'}), 201


@app.route('/evento/<int:id>', methods=['PUT'])
def update_evento(id):
    data = request.json
    fechaInicio = data['fechaInicio']
    fechaFinal = data['fechaFinal']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Evento SET fechaInicio = %s, fechaFinal = %s WHERE idEvento = %s',
                   (fechaInicio, fechaFinal, id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Evento actualizado'})


@app.route('/evento/<int:id>', methods=['DELETE'])
def delete_evento(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Evento WHERE idEvento = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Evento eliminado'})


# Metodos para Imagen
@app.route('/imagen', methods=['GET'])
def get_imagenes():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Imagen')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/imagen/<int:id>', methods=['GET'])
def get_one_imagen(id):
    data = fetch_one_imagen(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/imagen', methods=['POST'])
def create_imagen():
    data = request.json
    url = data['URL']
    estado = data['estado']
    respuesta = data['respuesta']
    idEvento = data['idEvento']
    idUsuario = data.get('idUsuario')  # Optional field, can be NULL
    # Check if the event exists using the helper function
    evento = fetch_one_evento(idEvento)
    if not evento:
        return jsonify({'mensaje': 'El evento especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Imagen (URL, estado, respuesta, idEvento, idUsuario) VALUES (%s, %s, %s, %s, %s)',
                       (url, estado, respuesta, idEvento, idUsuario))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Imagen creada'}), 201


@app.route('/imagen/<int:id>', methods=['PUT'])
def update_imagen(id):
    data = request.json
    url = data['URL']
    estado = data['estado']
    respuesta = data['respuesta']
    idEvento = data['idEvento']
    idUsuario = data.get('idUsuario')  # Optional field, can be NULL
    # Check if the event exists using the helper function
    evento = fetch_one_evento(idEvento)
    if not evento:
        return jsonify({'mensaje': 'El evento especificado no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE Imagen SET URL = %s, estado = %s, respuesta = %s, idEvento = %s, idUsuario = %s WHERE idImagen = %s',
                       (url, estado, respuesta, idEvento, idUsuario, id))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Imagen actualizada'})


@app.route('/imagen/<int:id>', methods=['DELETE'])
def delete_imagen(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Imagen WHERE idImagen = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Imagen eliminada'})


# Metodos para Casilla
@app.route('/casilla', methods=['GET'])
def get_casillas():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Casilla')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/casilla/<int:id>', methods=['GET'])
def get_one_casilla(id):
    data = fetch_one_casilla(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/casilla', methods=['POST'])
def create_casilla():
    data = request.json
    idImagen = data['idImagen']
    coordenadaX = data['coordenadaX']
    coordenadaY = data['coordenadaY']
    idPregunta = data['idPregunta']
    # Check if the image exists using the helper function
    imagen = fetch_one_imagen(idImagen)
    if not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        # Check if the question exists using the helper function
        pregunta = fetch_one_pregunta(idPregunta)
        if not pregunta:
            return jsonify({'mensaje': 'La pregunta especificada no existe'}), 400
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Casilla (idImagen, coordenadaX, coordenadaY, idPregunta) VALUES (%s, %s, %s, %s)',
                           (idImagen, coordenadaX, coordenadaY, idPregunta))
            conn.commit()
            conn.close()
            return jsonify({'mensaje': 'Casilla creada'}), 201


@app.route('/casilla/<int:id>', methods=['PUT'])
def update_casilla(id):
    data = request.json
    idImagen = data['idImagen']
    coordenadaX = data['coordenadaX']
    coordenadaY = data['coordenadaY']
    idPregunta = data['idPregunta']
    # Check if the image exists using the helper function
    imagen = fetch_one_imagen(idImagen)
    if not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        # Check if the question exists using the helper function
        pregunta = fetch_one_pregunta(idPregunta)
        if not pregunta:
            return jsonify({'mensaje': 'La pregunta especificada no existe'}), 400
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE Casilla SET idImagen = %s, coordenadaX = %s, coordenadaY = %s, idPregunta = %s WHERE idCasilla = %s',
                           (idImagen, coordenadaX, coordenadaY, idPregunta, id))
            conn.commit()
            conn.close()
            return jsonify({'mensaje': 'Casilla actualizada'})


@app.route('/casilla/<int:id>', methods=['DELETE'])
def delete_casilla(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Casilla WHERE idCasilla = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Casilla eliminada'})


# Metodos para Pregunta
@app.route('/pregunta', methods=['GET'])
def get_preguntas():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Pregunta')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/pregunta/<int:id>', methods=['GET'])
def get_one_pregunta(id):
    data = fetch_one_pregunta(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/pregunta', methods=['POST'])
def create_pregunta():
    data = request.json
    pregunta = data['pregunta']
    opcionA = data.get('opcionA')
    opcionB = data.get('opcionB')
    opcionC = data.get('opcionC')
    opcionD = data.get('opcionD')
    respuesta = data['respuesta']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES (%s, %s, %s, %s, %s, %s)',
                   (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta creada'}), 201


@app.route('/pregunta/<int:id>', methods=['PUT'])
def update_pregunta(id):
    data = request.json
    pregunta = data['pregunta']
    # se utiliza data.get() porque pueden ser NULL
    opcionA = data.get('opcionA')
    opcionB = data.get('opcionB')
    opcionC = data.get('opcionC')
    opcionD = data.get('opcionD')
    respuesta = data['respuesta']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Pregunta SET pregunta = %s, opcionA = %s, opcionB = %s, opcionC = %s, opcionD = %s, respuesta = %s WHERE idPregunta = %s',
                   (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta, id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta actualizada'})


@app.route('/pregunta/<int:id>', methods=['DELETE'])
def delete_pregunta(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Pregunta WHERE idPregunta = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta eliminada'})


# Metodos para IntentoCorrecto
@app.route('/intentoCorrecto', methods=['GET'])
def get_intentos_correctos():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM IntentoCorrecto')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/intentoCorrecto/<int:id>', methods=['GET'])
def get_one_intento_correcto(id):
    data = fetch_one_intento_correcto(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/intentoCorrecto', methods=['POST'])
def create_intento_correcto():
    data = request.json
    idUsuario = data['idUsuario']
    idCasilla = data['idCasilla']
    idImagen = data['idImagen']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    casilla = fetch_one_casilla(idCasilla)
    imagen = fetch_one_imagen(idImagen)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    elif not casilla:
        return jsonify({'mensaje': 'La casilla especificada no existe'}), 400
    elif not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO IntentoCorrecto (idUsuario, idCasilla, idImagen) VALUES (%s, %s, %s)',
                       (idUsuario, idCasilla, idImagen))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'IntentoCorrecto registrado'}), 201


@app.route('/intentoCorrecto/<int:id>', methods=['DELETE'])
def delete_intento_correcto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM IntentoCorrecto WHERE idCorrecto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'IntentoCorrecto eliminado'})

# Metodos para IntentoIncorrecto


@app.route('/intentoIncorrecto', methods=['GET'])
def get_intento_incorrecto():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM IntentoIncorrecto')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


@app.route('/intentoIncorrecto/<int:id>', methods=['GET'])
def get_one_intento_incorrecto(id):
    data = fetch_one_intento_incorrecto(id)
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404


@app.route('/intentoIncorrecto', methods=['POST'])
def create_intento_incorrecto():
    data = request.json
    opcionElegida = data['opcionElegida']
    idUsuario = data['idUsuario']
    idCasilla = data['idCasilla']
    idImagen = data['idImagen']
    # Check if the user exists using the helper function
    usuario = fetch_one_usuario(idUsuario)
    casilla = fetch_one_casilla(idCasilla)
    imagen = fetch_one_imagen(idImagen)
    if not usuario:
        return jsonify({'mensaje': 'El usuario especificado no existe'}), 400
    elif not casilla:
        return jsonify({'mensaje': 'La casilla especificada no existe'}), 400
    elif not imagen:
        return jsonify({'mensaje': 'La imagen especificada no existe'}), 400
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO IntentoIncorrecto (opcionElegida, idUsuario, idCasilla, idImagen) VALUES (%s, %s, %s, %s)',
                       (opcionElegida, idUsuario, idCasilla, idImagen))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'IntentoIncorrecto registrado'}), 201


@app.route('/intentoIncorrecto/<int:id>', methods=['DELETE'])
def delete_intento_incorrecto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM IntentoIncorrecto WHERE idIncorrecto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'IntentoIncorrecto eliminado'})



if __name__ == '__main__':
    app.run(debug=True, port=2025)
