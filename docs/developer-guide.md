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

## Prediction Logic

The tflite model is a binary classifier trained on images of dogs and cats.
We expect the model to have nearly determnistic prediction accuracy, so its necessary to use a threshold to filter out examples not seen in the training data.
The app uses a threshold paramter, which requires the model to have at least 97.5% proability that the image is a cat or a dog.

The backend reads the threshold from `config.toml`:

```toml
cat_threshold = 0.975
```
If the threshold isn't reached the backend returns the message:

```text
I can't tell if this image is a cat or a dog with high confidence
```

## ModelEngine

`backend.py` reads the model path from `config.toml` and loads an instance of
`ModelEngine`.  
`ModelEngine` is a wrapper around the TFLite `Interpreter` that handles model loading, input preprocessing, and prediction.

```python
Interpreter(model_path=self.model_path)
```

`ModelEngine.preprocess_input()`:

- opens the image with Pillow
- resizes the image to the model input height and width
- converts it to the model input dtype
- adds the batch dimension
- rescales image values when `rescale=True`.  By default `rescale=True`.

The scaling value is inferred from the PIL Image object using `pil_scale_value`.

`model_engine.py` can also be ran as a standalone script to check its outputs against the test images.

## Database Contract

SQLite persistence is handled by `webapp_db.py`.

The database path is configured in `config.toml`. The current default is:

```text
instance/webapp.sqlite
```

The table name is:

```text
webapp_response
```

Schema:

```sql
CREATE TABLE IF NOT EXISTS webapp_response (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image BLOB NOT NULL,
    filename TEXT,
    content_type TEXT,
    cat_probability REAL NOT NULL,
    prediction TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

Each successful prediction saves:

- original image bytes
- uploaded filename
- uploaded content type
- cat probability
- prediction message
- creation timestamp

Useful verification query:

```sql
SELECT
    id,
    filename,
    content_type,
    length(image),
    cat_probability,
    prediction,
    created_at
FROM webapp_response;
```

`length(image)` is a quick way to confirm that image bytes were actually saved.  A tool like dbeaver is convenient to view the images.  Images are saved to the table upon prediction submission.

## Browser Flow

The frontend flow is implemented in `static/app.js`:

1. `navigator.mediaDevices.getUserMedia()` starts the camera.
2. The camera frame is drawn into a canvas.
3. The canvas is converted to a JPEG blob.
4. The blob is sent to `/predict` as `FormData` with field name `image`.
5. The JSON response updates the prediction display.

## Local Smoke Checks

Check the health endpoint:

```sh
curl http://127.0.0.1:5000/health
```

Check prediction without the browser:

```sh
curl -X POST -F "image=@test_images/cat.jpg" http://127.0.0.1:5000/predict
```

Check sample model outputs:

```sh
curl http://127.0.0.1:5000/test_model_engine
```

Run the standalone model check:

```sh
uv run python model_engine.py
```

## Troubleshooting

### `uv` cache is not writable

The helper scripts should create the UV cache directory. They set `UV_CACHE_DIR` to a project-local cache by
default:

```sh
./install.sh
./start_app.sh
```

If needed, choose a different project-local cache:

```sh
RNB_WEBAPP_UV_CACHE_DIR=.uv-cache-dev ./install.sh
RNB_WEBAPP_UV_CACHE_DIR=.uv-cache-dev ./start_app.sh
```

### `tflite-runtime` fails with NumPy ABI errors

If imports fail with an error like `_ARRAY_API not found` or a NumPy 1.x vs 2.x
ABI warning, verify that the environment is using `numpy<2`.

The dependency pin is already in `pyproject.toml`:

```toml
"numpy<2"
```

### Camera access fails

The browser must allow camera access for the page. If the UI reports `Camera
blocked`, reset the browser permission for `http://127.0.0.1:5000` and reload.

### `/predict` returns HTTP 400

Confirm the request includes a multipart file field named `image`:

```sh
curl -X POST -F "image=@test_images/cat.jpg" http://127.0.0.1:5000/predict
```