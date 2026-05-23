from io import BytesIO
from pathlib import Path
import tomllib

from flask import Flask, request, jsonify, render_template
from model_engine import ModelEngine
from webapp_db import ensure_webapp_response_table_exists, save_webapp_response

PROJECT_ROOT = Path(__file__).resolve().parent

with (PROJECT_ROOT / "config.toml").open("rb") as config_file:
    CONFIG = tomllib.load(config_file)

DATABASE_PATH = (PROJECT_ROOT / CONFIG["paths"]["database"]).resolve()
MODEL_PATH = (PROJECT_ROOT / CONFIG["paths"]["model"]).resolve()
TEST_IMAGES_PATH = (PROJECT_ROOT / CONFIG["paths"]["test_images"]).resolve()
HOST = CONFIG["server"]["host"]
PORT = int(CONFIG["server"]["port"])
DEBUG = bool(CONFIG["server"]["debug"])
THRESHOLD = float(CONFIG["prediction"]["cat_threshold"])

app = Flask(__name__)
model = ModelEngine(str(MODEL_PATH))


@app.route("/")
def index():
    return render_template("index.html")


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
    
    save_webapp_response(image_bytes, image.filename, image.content_type, cat_probability, message, DATABASE_PATH)
    
    return jsonify({"cat_probability": float(output[0][0]), "prediction": message})


@app.route("/hello")
def hello():
    return jsonify({"message": "hello"})

@app.route("/test_model_engine")
def test_model_engine():
    # test cat image output
    cat_input = model.preprocess_input(TEST_IMAGES_PATH / "cat.jpg")
    cat_output = model.predict(cat_input)

    dog_input = model.preprocess_input(TEST_IMAGES_PATH / "dog2.webp")
    dog_output = model.predict(dog_input)

    ithaca_cat_input = model.preprocess_input(TEST_IMAGES_PATH / "ithaca_cat.jpg")
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
    ensure_webapp_response_table_exists(DATABASE_PATH)
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
    )
