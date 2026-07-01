import sqlite3
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()

    conn.execute('''
                 CREATE TABLE IF NOT EXISTS usuarios (
                                                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                         username TEXT NOT NULL,
                                                         password TEXT NOT NULL
                 )
                 ''')

    conn.execute('''
                 CREATE TABLE IF NOT EXISTS expedientes (
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            aseguradora TEXT,
                                                            cliente TEXT,
                                                            juzgado TEXT,
                                                            estado TEXT,
                                                            fecha TEXT
                 )
                 ''')

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return send_file('WebPage.html')

@app.route('/dashboard')
def dashboard():
    return send_file('dashboard.html')


@app.route('/usuarios', methods=['POST'])
def crear_usuario():

    data = request.json

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO usuarios (username, password) VALUES (?, ?)",
        (data['username'], data['password'])
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Usuario creado"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json

    username = data['username']
    password = data['password']

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM usuarios WHERE username=? AND password=?",
        (username, password)
    ).fetchone()

    conn.close()

    if user:
        return jsonify({"message": "Login correcto"})
    else:
        return jsonify({"message": "Credenciales incorrectas"}), 401

@app.route('/expedientes', methods=['GET'])
def obtener_expedientes():
    conn = get_db_connection()

    rows = conn.execute("SELECT * FROM expedientes").fetchall()
    conn.close()

    expedientes = [dict(row) for row in rows]

    return jsonify(expedientes)

@app.route('/expedientes', methods=['POST'])
def crear_expediente():
    data = request.json

    conn = get_db_connection()

    conn.execute("""
                 INSERT INTO expedientes (aseguradora, cliente, juzgado, estado, fecha)
                 VALUES (?, ?, ?, ?, ?)
                 """, (
                     data['aseguradora'],
                     data['cliente'],
                     data['juzgado'],
                     data['estado'],
                     data['fecha']
                 ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Expediente creado"})


@app.route('/expedientes/<int:id>', methods=['PUT'])
def editar_expediente(id):
    data = request.json

    conn = get_db_connection()

    conn.execute("""
                 UPDATE expedientes
                 SET aseguradora = ?, cliente = ?, juzgado = ?, estado = ?, fecha = ?
                 WHERE id = ?
                 """, (
                     data['aseguradora'],
                     data['cliente'],
                     data['juzgado'],
                     data['estado'],
                     data['fecha'],
                     id
                 ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Expediente actualizado"})


@app.route('/expedientes/<int:id>', methods=['DELETE'])
def eliminar_expediente(id):
    conn = get_db_connection()

    conn.execute("DELETE FROM expedientes WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Expediente eliminado"})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

