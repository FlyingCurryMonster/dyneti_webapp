# Implementation methodology
## File structure
- I chose a modular file structure that separates the Flask backend, HTML/JavaScript frontend, model inference engine, and SQLite database interface.
- I used HTML and JavaScript to build a simple frontend, with a CSS file for a clean layout. I used the browser's built-in webcam API to capture an image and send it to the backend as a multipart form POST request. I used Flask to handle backend routes and JSON responses, and I used the PIL image library to load and preprocess images before sending them to the model.
- For my database, I used SQLite and created a SQLite file in Flask's `instance` directory. Each prediction stores the original uploaded image as a BLOB, the model score, the predicted class label, and optional user feedback fields. I used DBeaver to inspect each submission because it can display saved BLOB images directly in its UI.

## Virtual environment and configs
- To build and manage the virtual environment, I used the `uv` package manager. I wanted the project to have an isolated Python environment so the app could be installed consistently on different machines, and I chose `uv` because it is fast at dependency resolution and environment setup.
- I used the `tflite-runtime` package to avoid downloading the full TensorFlow library. During setup, I found that this runtime requires `numpy<2`, so I added that constraint to `pyproject.toml`.
- I used `config.toml` to configure runtime parameters for the web app, including the model path, database path, server settings, test image directory, and classification threshold. I considered environment variables, but a local config file avoids relying on machine-specific OS environment state.

## Model inference and classification threshold
- Since the given tflite model is expected to be accurate on cat and dog images, I set a probability threshold so ambiguous predictions are reported as uncertain instead of forcing every image into a cat or dog label. With the default threshold, the backend only returns a cat or dog label when the model confidence is at least 0.975 in either direction.
- For image preprocessing, I used the PIL image library to load the image. The TFLite model expects normalized pixel intensities in the range `[0, 1]`, so I infer the rescale value from the PIL image mode instead of hard-coding assumptions for every input. For standard 8-bit modes like `RGB`, `RGBA`, `L`, and `P`, I rescale by `255.0`; for 16-bit integer modes I rescale by `65535.0`; and for unsupported unsupported modes, I raise an error since I don't confidently know what the rescale value should be. I also included shape checking so that inputs must match the model's expected `(batch, height, width, channels)` tensor shape before inference.
- I also included user feedback on whether the prediction was correct so the stored results can support future model evaluation and retraining. The `/predict` response returns the SQLite row id, and the frontend uses that id to submit feedback to `/feedback`. The feedback fields are nullable because a prediction can be saved before the user responds, and the same row is updated later with whether the user said the prediction was correct, the user-provided label when it was incorrect, and the feedback timestamp.

# Future implementation ideas
## Postgres database and deduplication
- In production, I would use a Postgres database instead of SQLite because Postgres handles concurrent writes and is more scalable than SQLite. I would keep one table for user image submission and a separate table for deduplicated, reviewable training examples.
- One edge case is that a user may upload the same image multiple times. Since new images gives us the opportunity to improve the model, the training dataset should not be cluttered with duplicates. For exact duplicates, I would store and compare an image byte hash.
- For production, I would store image files in object based storage.  In postgres I'd keep data that is much more tabular friendly such as metadata, storage paths, hashes, prediction outputs, and feedback labels. That design would scale better than storing every image directly in the relational database.

## Online learning and validation
- Once we have a deduplicated table, we can use it for retraining and evaultaion.  I wouldn't train on data live since we'd need to validate carefully that incorrectly classified images are properly labeld.
- We would need a methodology to ensure users are not giving incorrect feedback. The safest approach would be to manually review a sample of incorrectly classified images and label them before using them for training. We could also prioritize images that were close to the classification threshold or images where the user marked the model as incorrect, because those examples are most informative for improving the classifier.
- We'd also need to evaluate the model on a test set to ensure that our retrained model is actually improving.


## Model hot swapping and production readiness
- We should ideally be able to swap out models while the app is running, and keep track of the model version.
- Each prediction row should include a `model_version` so feedback can be traced back to the exact model that produced the result.
- Before hot swapping a model, I would run smoke checks against known test images. If the new model passes those checks, the app could atomically load the new model version; if it fails, the system should keep serving the previous model.
- For production readiness, I would run the Flask app behind a production WSGI server, add logging and health checks.