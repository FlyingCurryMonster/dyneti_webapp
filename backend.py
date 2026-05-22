import sqlite3
from io import BytesIO
from pathlib import Path

from flask import Flask, request, jsonify
from model_engine import ModelEngine, MODEL_PATH

app = Flask(__name__)
model = ModelEngine(MODEL_PATH)

THRESHOLD = 0.95
DATABASE_PATH = Path("./webapp.sqlite")


def create_webapp_response_table(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS webapp_response (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image BLOB NOT NULL,
            filename TEXT,
            content_type TEXT,
            cat_probability REAL NOT NULL,
            prediction TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.commit()


def ensure_webapp_response_table_exists(db_path=DATABASE_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        create_webapp_response_table(connection)

def save_webapp_response(image_bytes, filename, content_type, cat_probability, prediction, db_path=DATABASE_PATH):
    ensure_webapp_response_table_exists(db_path)

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO webapp_response (image, filename, content_type, cat_probability, prediction, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            (image_bytes, filename, content_type, cat_probability, prediction)
        )
        connection.commit()

ensure_webapp_response_table_exists()

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files["image"]
    image_bytes = image.read()
    input = model.preprocess_input(BytesIO(image_bytes))
    output = model.predict(input)
    cat_probability = float(output[0][0])

    if cat_probability >= THRESHOLD:
        message = "This is an image of a cat"
    elif cat_probability < 1 - THRESHOLD:
        message = "This is an image of a dog"
    else:
        message = "I can't tell if this image is a cat or a dog with high confidence"
    
    save_webapp_response(image_bytes, image.filename, image.content_type, cat_probability, message)
    
    return jsonify({"cat_probability": float(output[0][0]), "prediction": message})


@app.route("/hello")
def hello():
    return jsonify({"message": "hello"})

@app.route("/test_model_engine")
def test_model_engine():
    # test cat image output
    cat_input = model.preprocess_input('./test_images/cat.jpg')
    cat_output = model.predict(cat_input)

    dog_input = model.preprocess_input('./test_images/dog2.webp')
    dog_output = model.predict(dog_input)

    ithaca_cat_input = model.preprocess_input('./test_images/ithaca_cat.jpg')
    ithaca_cat_output = model.predict(ithaca_cat_input)
    return jsonify({
        "cat image cat_probability": float(cat_output[0][0]),
        "dog image cat_probability": float(dog_output[0][0]),
        "ithaca cat image cat_probability": float(ithaca_cat_output[0][0])
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# sink to database

if __name__ == "__main__":
    ensure_webapp_response_table_exists()
    app.run(debug=True)
