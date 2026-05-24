# End User Guide

This web app allows you to take a photo of your pet with your webcam and ask
an ML model if it's a cat or dog.
If the model does not have enough confidence, it will say it is unsure.

## Installation instructions

To install the webapp run:

```sh
./install.sh
```

To run the webapp, run:

```sh
./start_app.sh
```

For more details please refer to the setup section in the developer guide.

## Webapp Usage Instructions

1. After the web app is running, open `http://127.0.0.1:5000` in your browser.
2. Select **Start camera**.
3. Allow camera access if the browser asks for permission.
4. Wait until the camera preview appears.
5. Select **Capture photo**.
6. Review the captured photo preview.
7. Select **Submit prediction**.
8. After the result appears, answer whether the prediction was correct.

The possible outputs are:

- `This is an image of a cat`
- `This is an image of a dog`
- `I can't tell if this image is a cat or a dog with high confidence`

## Providing Feedback

After the prediction appears, the app asks whether the result was correct.

If the prediction is correct, select **Yes**.

If the prediction is not correct, select **No**, then choose the correct image
category:

- **Cat**
- **Dog**
- **Neither**

The feedback is saved to the same database row as the original prediction. If
you change your mind and select another feedback option, the app modifies the
same row in place rather than creating a duplicate prediction.

## Data And Privacy

This app saves each submitted image and prediction result in a local SQLite
database on the machine running the app.

Saved data includes the image, filename, content type, cat probability,
prediction message, prediction timestamp, user feedback, user-provided label
if the prediction was incorrect, and feedback timestamp.

## Troubleshooting

If the camera does not start, check that the browser has permission to use the
camera.

If the page shows `Camera blocked`, use the browser's site settings to allow
camera access, then reload the page.

If prediction fails, make sure the web app is still running in the terminal.

If the browser cannot open the page, ask the person running the app to confirm
the address. With the current default settings, the address is:

```text
http://127.0.0.1:5000
```
