from flask import Flask, request, jsonify
from model_engine import ModelEngine, MODEL_PATH

app = Flask(__name__)
model = ModelEngine(MODEL_PATH)

THRESHOLD = 0.95

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files["image"]
    input = model.preprocess_input(image)
    output = model.predict(input)
    return jsonify({"cat_probability": float(output[0][0])})


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

if __name__ == "__main__":
    app.run(debug=True)
