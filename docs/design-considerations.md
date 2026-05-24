# Implementation methodology
## File structure
- I chose my file structure to have modularity, by seperating the flask backend, html/javascript frontend, model inference engine, and SQLite database interface.
- I used HTML and javascript to make a simple frontend with a css file to create a simple and clean layout.  I used the browser's built in webcam API to capture an image, and send it to the backend as a multipart form post request.  I used flask to handle the backend routes and responses, and I used the PIL image library to handle image loading and preprocessing for the model.
- For my database I used SQLite and created a sqlite file in the "instance" directory.  I used dbeaver to inspect each submission, and saved the images in BLOB format.  Dbeaver conveniently renders the BLOB as an image in its UI.

## Virtual environment and configs
- To build and manage the virtual environment I used the `uv` package manager.  I wanted to use a virtual environment so that try my best to ensure the app can run on different machines.  I had heard about `uv` being much faster at resolving package dependency graphs than venv, and wanted to try it out.  
- I used the tflite-runtime package to avoid downloading the full tensorflow library.  `uv` pointed out that tflite-runtime requires `numpy<2`, so I added  that constraint to the `pyproject.toml`.
- I used a `config.toml` as a way to configure runtime parameters of the web app.  I thought about using environment variables for this, but I didn't want to populate the OS namespace, and I didn't want to have to think about potential variable name collisions in the current namespace.

## Model inference and classification threshold
- Since it's given that our model is a "good" model -- it has nearly deterministic accuracy, I set a probability threshold so that ambiguous predictions are reported as uncertain.  I set this default so that the model predicts cat or dog with at least 0.975 uncertainty.
- For image preprocessing, I used the PIL image library to load the image.  The tflite model expects pixel intensities to be bounded between (0, 1).  An edge case I worried about is the correct rescale value to use.  I enforced that only PIL images with a mode atribute of ("RGB", "RGBA", "L", "P", "I;16", "I;16L", 'I;16B', "1", "F") can be uploaded, since I can verify what their maximum pixel intensity is for each mode.  I wasn't sure how to handle "F" mode images, which are already float-ish, so I just return None for the rescale value in that case.  I also included shape checking so that my uploaded image is enforced to be a 3 channel image.
- I also included user feedback on whether the prediction was correct or not, so that it enables model retraining on new data in the future.  Null responses should be handled in the SQLite table.

# Future implementation ideas
## Postgres database and deduplication
- I would use a postgres database instead of SQLite. and use a table that inserts a row for every user image submission, and then have a seperate table that deduplicates the data.  
- An edge case is that the user uploads the same image multiple times.  The utility of storing the data is we can retrain the model, and so we want to ensure we are not cluttering the training data with duplicates.  One methodology for deduplicating is to include a session id for each user, and check for similarity of images within a session.  To assess for similarity we can use PCA to reduce the dimensionality of the images, and then use a distance metric in the reduced space to determine if two images are similar.
- 
## Online learning and validation
- Once we have a deduplicated table, we can use that for online learning.  
- We would need to implement a methodology ensure our users are not giving incorrect feedback.  The brute force way would to be manually check all incorrectly classified images and label them.  We could also just constrain our focus to images that were close to the classification threshold but were missclassifeid.


## Model hot swapping and production readiness
- We should ideally be able to swap out models while the app is running. But being able to hot swap models without restarting the server would be nice to have.

