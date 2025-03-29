from flask import Flask, request, jsonify
from flask_cors import CORS
import pymssql

app = Flask(__name__)
CORS(app)

# Database configuration
server = "localhost"
port = 1433
database = "master"
username = "sa"
password = "YourPassword123!"

# Database connection function
def get_connection():
    return pymssql.connect(server=server, port=port, user=username, password=password, database=database)

# Metodos para Usuario
@app.route('/usuario', methods=['GET'])
def get_usuarios():
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Usuario')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)
@app.route('/usuario/<int:id>', methods=['GET'])
def get_one_usuario(id):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Usuario WHERE id = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404

@app.route('/usuario', methods=['POST'])
def create_usuario():
    data = request.json
    usuario = data['usuario']
    idEvento = data['idEvento']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Usuario (usuario, idEvento) VALUES (%s, %s)', (usuario, idEvento))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Usuario creado'}), 201

@app.route('/usuario/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.json
    usuario = data['usuario']
    idEvento = data['idEvento']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Usuario SET usuario = %s, idEvento = %s WHERE idUsuario = %s', (usuario, idEvento, id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Usuario actualizado'})

@app.route('/usuario/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Usuario WHERE idUsuario = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Usuario eliminado'})

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
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Boleto WHERE id = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404

@app.route('/boleto', methods=['POST'])
def create_boleto():
    data = request.json
    tipo = data['tipo']
    idUsuario = data['idUsuario']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Boleto (tipo, idUsuario) VALUES (%s, %s)', (tipo, idUsuario))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Boleto creado'}), 201

@app.route('/boleto/<int:id>', methods=['PUT'])
def update_boleto(id):
    data = request.json
    tipo = data['tipo']
    idUsuario = data['idUsuario']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Boleto SET tipo = %s, idUsuario = %s WHERE idBoleto = %s', (tipo, idUsuario, id))
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
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Evento WHERE id = %s', (id,))
    data = cursor.fetchone()
    conn.close()
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
    cursor.execute('INSERT INTO Evento (fechaInicio, fechaFinal) VALUES (%s, %s)', (fechaInicio, fechaFinal))
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
    cursor.execute('UPDATE Evento SET fechaInicio = %s, fechaFinal = %s WHERE idEvento = %s', (fechaInicio, fechaFinal, id))
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
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Imagen WHERE id = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404

@app.route('/imagen', methods=['POST'])
def create_imagen():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Imagen (URL, estado, respuesta, idEvento, idUsuario) VALUES (%s, %s, %s, %s, %s)',
                   (data['URL'], data['estado'], data['respuesta'], data['idEvento'], data['idUsuario']))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Imagen creada'}), 201

@app.route('/imagen/<int:id>', methods=['PUT'])
def update_imagen(id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Imagen SET URL = %s, estado = %s, respuesta = %s, idEvento = %s, idUsuario = %s WHERE idImagen = %s',
                   (data['URL'], data['estado'], data['respuesta'], data['idEvento'], data['idUsuario'], id))
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
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Casilla WHERE id = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404

@app.route('/casilla', methods=['POST'])
def create_casilla():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Casilla (idImagen, coordenadaX, coordenadaY, idPregunta) VALUES (%s, %s, %s, %s)',
                   (data['idImagen'], data['coordenadaX'], data['coordenadaY'], data['idPregunta']))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Casilla creada'}), 201

@app.route('/casilla/<int:id>', methods=['PUT'])
def update_casilla(id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Casilla SET idImagen = %s, coordenadaX = %s, coordenadaY = %s, idPregunta = %s WHERE idCasilla = %s',
                   (data['idImagen'], data['coordenadaX'], data['coordenadaY'], data['idPregunta'], id))
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
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Pregunta WHERE id = %s', (id,))
    data = cursor.fetchone()
    conn.close()
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
    cursor.execute('INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES (%s, %s, %s, %s, %s, %s)', (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Pregunta creada'}), 201

@app.route('/pregunta/<int:id>', methods=['PUT'])
def update_pregunta(id):
    data = request.json
    pregunta = data['pregunta']
    opcionA = data.get('opcionA')
    opcionB = data.get('opcionB')
    opcionC = data.get('opcionC')
    opcionD = data.get('opcionD')
    respuesta = data['respuesta']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Pregunta SET pregunta = %s, opcionA = %s, opcionB = %s, opcionC = %s, opcionD = %s, respuesta = %s WHERE idPregunta = %s', (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta, id))
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
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM IntentoCorrecto WHERE id = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404

@app.route('/intento_correcto', methods=['POST'])
def create_intento_correcto():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO IntentoCorrecto (idUsuario, idCasilla, idImagen) VALUES (%s, %s, %s)',
                   (data['idUsuario'], data['idCasilla'], data['idImagen']))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'IntentoCorrecto registrado'}), 201

@app.route('/intento_correcto/<int:id>', methods=['DELETE'])
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
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM IntentoIncorrecto WHERE id = %s', (id,))
    data = cursor.fetchone()
    conn.close()
    if data:
        return jsonify(data)
    else:
        return jsonify({'mensaje': 'Registro no encontrado'}), 404

@app.route('/intento_incorrecto', methods=['POST'])
def create_intento_incorrecto():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO IntentoIncorrecto (opcionElegida, idUsuario, idCasilla, idImagen) VALUES (%s, %s, %s, %s)',
                   (data['opcionElegida'], data['idUsuario'], data['idCasilla'], data['idImagen']))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'IntentoIncorrecto registrado'}), 201

@app.route('/intento_incorrecto/<int:id>', methods=['DELETE'])
def delete_intento_incorrecto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM IntentoIncorrecto WHERE idIncorrecto = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'IntentoIncorrecto eliminado'})

if __name__ == '__main__':
    app.run(debug=True, port=2025)
