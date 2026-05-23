# End User Guide

This web app allows you to take a photo of your pet with your webcam and ask
an ML model if it's a cat or dog.
If the model does not have enough confidence, it will say its unsure.


# Instructions

1. After the webapp is running (see developer-guide) go to http://127.0.0.1:5000 in your browser.
2. Select **Start camera**.
3. Allow camera access if the browser asks for permission.
4. Select **Capture photo**.
5. Review the captured photo preview.
6. Select **Submit prediction**.

The possible outputs are 
- `This is an image of a cat`
- `This is an image of a dog`
- `I can't tell if this image is a cat or a dog with high confidence`


# Data And Privacy

This app saves each submitted image and prediction result in a local SQLite
database on the machine running the app.