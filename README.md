# Dyneti Webapp

A small Flask web application for running a local cat-vs-dog image classifier.
The app lets a user capture a photo from their webcam, send it to a TensorFlow
Lite model, and view the model's prediction in the browser. Each prediction is
stored in a local SQLite database with the uploaded image bytes and model output.

## Quick Start

Clone the source code and enter the project directory:

```sh
git clone https://github.com/FlyingCurryMonster/dyneti_webapp.git
cd dyneti_webapp
```

Install the project dependencies:

```sh
./install.sh
```

Run the web app:

```sh
./start_app.sh
```

Then open:

```text
http://127.0.0.1:5000
```

Runtime paths, server settings, debug mode, and the prediction threshold are
defined in `config.toml`.

## Documentation

- [End User Guide](docs/end-user-guide.md): how to use the web app and interpret
  predictions.
- [Developer Guide](docs/developer-guide.md): setup, architecture, API contract,
  database details, model behavior, and troubleshooting.

## Project Structure

```text
config.toml            Runtime paths, server settings, and prediction threshold
install.sh             Dependency install helper with project-local uv cache
start_app.sh           App startup helper
backend.py             Flask routes and app startup
model_engine.py        TFLite model loading, preprocessing, and inference
webapp_db.py           SQLite table creation and prediction persistence
model.tflite           Local cat-vs-dog model
templates/index.html   Browser UI template
static/app.js          Webcam capture and prediction request logic
static/style.css       Page styling
test_images/           Sample images for local checks
```

## Current Scope

The app currently classifies webcam images as cat, dog, or uncertain. It is a
local development app, not a production deployment. Captured images and
prediction outputs with user feedback are saved in `instance/webapp.sqlite` on
the machine running the app.
