from psycopg2 import connect
from flask import Flask, request, render_template, redirect, url_for
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
import os
from flask_cors import CORS  # Importar flask-cors


app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las solicitudes


model = load_model('model-2.h5')

host = 'orders_database'
port = 5432
dbname = 'liverdb'
user = 'postgres'
password = 'Nano3110'


def get_connection():
    conn = connect(host=host, port=port, dbname=dbname,
                   user=user, password=password)
    return conn


@app.get('/api')
def home():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 + 1")
    result = cur.fetchone()
    print(result)
    return 'Hello, World!'


@app.route('/api/product/<int:id>', methods=['GET'])
def get_product(id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM my_table WHERE id = %s", (str(id),))
        product = cur.fetchone()
    except Exception as e:
        print(f"Error fetching product: {e}")
        product = None
    finally:
        cur.close()
        conn.close()

    if product:
        return {
            'id': product[0],
            'nombre': product[1],
            'url': product[2]
        }
    else:
        return {'error': 'Product not found'}, 404


@app.route('/api/search', methods=['POST'])
def upload_image():
    if request.method == 'POST':
        # Verifica si hay un archivo en la solicitud
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'

        # Guarda la imagen subida
        filepath = os.path.join('static', file.filename)
        file.save(filepath)

        # Realiza la predicción
        prediction = predict_image(filepath)
        return str(prediction)
    return "No file uploaded"


def get_class_indices():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, nombre FROM my_table")
        rows = cur.fetchall()
        class_indices = {row[0]: row[1] for row in rows}
    except Exception as e:
        print(f"Error fetching class indices: {e}")
        class_indices = {}
    finally:
        cur.close()
        conn.close()
    return class_indices

# Función para predecir la clase de la imagen subida
# Función para predecir la clase de la imagen subida


def predict_image(filepath):
    test_image = image.load_img(
        filepath, target_size=(64, 64))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis=0)
    result = model.predict(test_image)
    predicted_class = np.argmax(result, axis=1)[0]
    print(predicted_class)
    return predicted_class


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
