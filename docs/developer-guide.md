# Developer Guide

This guide is for developer support

## Requirements

- Python 3.11 or newer
- `uv`
- a browser with webcam support

The Python dependencies are in `pyproject.toml`:

- `flask`
- `numpy<2`
- `pillow`
- `tflite-runtime`

`tflite-runtime` avoids downloading the entire `tensorflow` library into .venv, but it requires that `numpy<2`.

## Setup

To install the webapp run:

```sh
./install.sh
```

It creates the  environment variable `RNB_WEBAPP_UV_CACHE_DIR` cache directory and installs the
virtual environment with the `uv` package manager. By default,
`RNB_WEBAPP_UV_CACHE_DIR` is `.uv-cache`.

To run the webapp, run:

```sh
./start_app.sh
```

The Flask development server should by default start at:

```text
http://127.0.0.1:5000
```

but the port and server can be configured in `config.toml`.

## Runtime Configuration

Runtime settings live in `config.toml`.

`backend.py` resolves these configs using `tomlib`.  The configurable settings include:
- model_path
- test_images directory
- host and port for the Flask server
- debug mode for the Flask server
- cat threshold for model prediction confidence

## Architecture

The app is split into small modules:

```text
backend.py       Flask app, routes, config loading, and response formatting
model_engine.py  TFLite model loading, image preprocessing, and prediction
webapp_db.py     SQLite table creation and response persistence
```

Frontend assets live in the standard Flask locations:

```text
templates/index.html
static/app.js
static/style.css
```

Project helpers:

```text
install.sh       Runs uv sync with a project-local cache
start_app.sh     Runs uv run python backend.py with a project-local cache
config.toml      Runtime paths, server settings, and prediction threshold
```

The current model file is:

```text
model.tflite
```

## Backend API

### `GET /`

Renders the browser UI from `templates/index.html`.

### `GET /health`

Returns a lightweight health check:

### `POST /predict`

Runs image inference and stores the result in SQLite table.

The request must be `multipart/form-data` with a file field named `image`.

Example:

```sh
curl -X POST -F "image=@test_images/cat.jpg" http://127.0.0.1:5000/predict
```

Successful response shape:

```json
{
  "cat_probability": 0.98,
  "prediction": "This is an image of a cat"
}
```

If the request does not include an `image` file, the endpoint returns HTTP 400:

```json
{
  "error": "No image file provided"
}
```

### `GET /test_model_engine`

Runs model inference against the configured sample image directory and returns
cat probabilities for:

- `cat.jpg`
- `dog2.webp`
- `ithaca_cat.jpg`

This route is useful for checking the model and preprocessing path without using
the browser camera flow.