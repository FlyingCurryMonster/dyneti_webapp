# Developer Guide

This guide is for developers who need to install, run, test, or modify the web
app.

## Requirements

- Python 3.11 or newer
- `uv`
- a browser with webcam support

The Python dependencies are in `pyproject.toml`:

- `flask`
- `numpy<2`
- `pillow`
- `tflite-runtime`

`tflite-runtime` avoids downloading the full `tensorflow` library into `.venv`,
but it requires `numpy<2`.

## Setup

To install the webapp run:

```sh
./install.sh
```

The install script creates the project-local uv cache directory and installs the
virtual environment with the `uv` package manager. By default, the cache
directory is `.uv-cache`.

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

`backend.py` resolves these configs using `tomllib`. The configurable settings
include:

- database path
- model path
- test images directory
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

```json
{
  "status": "ok"
}
```

### `POST /predict`

Runs image inference and stores the result in the `webapp_response` SQLite
table.

The request must be `multipart/form-data` with a file field named `image`.

Example:

```sh
curl -X POST -F "image=@test_images/cat.jpg" http://127.0.0.1:5000/predict
```

Successful response shape:

```json
{
  "id": 1,
  "cat_probability": 0.98,
  "prediction": "This is an image of a cat"
}
```

The `id` is the primary key of the saved `webapp_response` row. The frontend
uses this id when it submits user feedback.

If the request does not include an `image` file, the endpoint returns HTTP 400:

```json
{
  "error": "No image file provided"
}
```

### `POST /feedback`

Stores user feedback for an existing prediction row.

The request body must be JSON. If the model prediction was correct:

```json
{
  "id": 1,
  "correct": true
}
```

If the model prediction was incorrect, `user_label` is required and must be one
of `cat`, `dog`, or `neither`:

```json
{
  "id": 1,
  "correct": false,
  "user_label": "dog"
}
```
If the user does not include the user_label on an incorrect prediction, "correct" is not marked.

Successful response shape:

```json
{
  "status": "ok"
}
```

The endpoint updates the existing prediction row in place. Repeated feedback for
the same prediction id overwrites `user_feedback_correct`, `user_label`, and
`feedback_submitted_at` on that row.

Validation behavior:

- missing JSON body: HTTP 400
- missing `id`: HTTP 400
- missing `correct`: HTTP 400
- non-boolean `correct`: HTTP 400
- `correct: false` without a valid `user_label`: HTTP 400
- unknown prediction id: HTTP 404

### `GET /test_model_engine`

Runs model inference against the configured sample image directory and returns
cat probabilities for:

- `cat.jpg`
- `dog2.webp`
- `ithaca_cat.jpg`

This route is useful for checking the model and preprocessing path without using
the browser camera flow.

## Prediction Logic

The TFLite model is a binary classifier trained on images of dogs and cats. The
threshold is a confidence cutoff used to avoid confident-looking labels when the
model output is ambiguous.

The backend reads the threshold from `config.toml`:

```toml
cat_threshold = 0.975
```

With the current threshold, the backend returns:

- `This is an image of a cat` when `cat_probability >= 0.975`
- `This is an image of a dog` when `cat_probability < 0.025`
- the uncertain message otherwise:

```text
I can't tell if this image is a cat or a dog with high confidence
```

## ModelEngine

`backend.py` reads the model path from `config.toml` and loads an instance of
`ModelEngine`.
`ModelEngine` is a wrapper around the TFLite `Interpreter` that handles model
loading, input preprocessing, and prediction.

```python
Interpreter(model_path=self.model_path)
```

`ModelEngine.preprocess_input()`:

- opens the image with Pillow
- resizes the image to the model input height and width
- converts it to the model input dtype
- adds the batch dimension
- rescales image values when `rescale=True`. By default `rescale=True`.

The scaling value is inferred from the PIL Image object using `pil_scale_value`.

`model_engine.py` can also be run as a standalone script to check its outputs
against the test images.

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
    created_at TEXT NOT NULL,
    user_feedback_correct INTEGER,
    user_label TEXT,
    feedback_submitted_at TEXT
);
```

Each successful prediction saves:

- original image bytes
- uploaded filename
- uploaded content type
- cat probability
- prediction message
- creation timestamp

Feedback fields are nullable because a prediction can be saved before the user
answers the feedback prompt:

- `user_feedback_correct`: `1` if the user said the prediction was correct, `0`
  if the user said it was incorrect, and `NULL` if no feedback has been submitted
- `user_label`: one of `cat`, `dog`, or `neither` when the prediction was marked
  incorrect; otherwise `NULL`
- `feedback_submitted_at`: timestamp for the latest feedback submission, or
  `NULL` if no feedback has been submitted

Useful verification query:

```sql
SELECT
    id,
    filename,
    content_type,
    length(image),
    cat_probability,
    prediction,
    created_at,
    user_feedback_correct,
    user_label,
    feedback_submitted_at
FROM webapp_response;
```

`length(image)` is a quick way to confirm that image bytes were actually saved.
A tool like DBeaver is convenient for viewing the saved rows and image BLOBs.
Images are saved to the table when a prediction is submitted.

## Browser Flow

The frontend flow is implemented in `static/app.js`:

1. `navigator.mediaDevices.getUserMedia()` starts the camera.
2. The camera frame is drawn into a canvas.
3. The canvas is converted to a JPEG blob.
4. The blob is sent to `/predict` as `FormData` with field name `image`.
5. The JSON response updates the prediction display and stores the returned
   prediction id in browser state.
6. The page asks the user whether the prediction was correct.
7. If the prediction was incorrect, the page asks whether the true label was
   `cat`, `dog`, or `neither`.
8. The feedback is sent to `/feedback` as JSON and updates the same database
   row created by `/predict`.

## Local Smoke Checks

Check the health endpoint:

```sh
curl http://127.0.0.1:5000/health
```

Check prediction without the browser:

```sh
curl -X POST -F "image=@test_images/cat.jpg" http://127.0.0.1:5000/predict
```

Check feedback without the browser, replacing `1` with an id returned from
`/predict`:

```sh
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "correct": false, "user_label": "dog"}' \
  http://127.0.0.1:5000/feedback
```

Check sample model outputs:

```sh
curl http://127.0.0.1:5000/test_model_engine
```

Run the standalone model check:

```sh
UV_CACHE_DIR=.uv-cache uv run python model_engine.py
```

## Troubleshooting

### `uv` cache is not writable

The helper scripts should create the uv cache directory. They set
`UV_CACHE_DIR` to a project-local cache by default:

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
