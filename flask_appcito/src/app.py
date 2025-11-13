import os
from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
from datetime import datetime
from dotenv import load_dotenv

# Cargar archivo .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Variables de conexión
MONGO_URI = os.getenv('MONGO_URI')

app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI

try:
    mongo = PyMongo(app)
    sensor_collection = mongo.db.sensor
    print("✅ Conexión a MongoDB establecida correctamente.")
except Exception as e:
    print(f"❌ Error al conectar a MongoDB: {e}")
    mongo = None
    sensor_collection = None


@app.route('/')
def index():
    return "API conectada correctamente."


# 🔹 Endpoint para insertar datos (POST)
@app.route('/insert', methods=['POST'])
def insert_data():
    if sensor_collection is not None:
        try:
            data = request.get_json()

            # Validación básica
            if not data or not all(k in data for k in ("ts", "value", "sensor")):
                return jsonify({"error": "Faltan campos en el JSON. Se requieren: ts, value, sensor"}), 400

            # Agregamos una marca de tiempo automática del servidor
            data["fecha_servidor"] = datetime.now()

            result = sensor_collection.insert_one(data)
            return jsonify({
                "mensaje": "✅ Dato agregado exitosamente.",
                "id": str(result.inserted_id)
            }), 201
        except Exception as e:
            return jsonify({"error": f"Error al insertar en la base de datos: {e}"}), 500
    else:
        return jsonify({"error": "La conexión a la base de datos no está establecida."}), 500


# 🔹 Endpoint para obtener los datos (GET)
@app.route('/get_datos', methods=['POST'])
def get_datos():
    if sensor_collection is not None:
        try:
            datos = list(sensor_collection.find())

            # Convertir los campos para que sean serializables
            for d in datos:
                d["_id"] = str(d["_id"])
                if "fecha_servidor" in d:
                    d["fecha_servidor"] = d["fecha_servidor"].strftime("%Y-%m-%d %H:%M:%S")

            return jsonify(datos), 200
        except Exception as e:
            return jsonify({"error": f"Error al obtener los datos: {e}"}), 500
    else:
        return jsonify({"error": "La conexión a la base de datos no está establecida."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
