# End User Guide

This web app allows you to take a photo of your pet with your webcam and ask
an ML model if it's a cat or dog.
If the model does not have enough confidence, it will say it is unsure.


## Instructions

1. After the web app is running, open `http://127.0.0.1:5000` in your browser.
2. Select **Start camera**.
3. Allow camera access if the browser asks for permission.
4. Wait until the camera preview appears.
5. Select **Capture photo**.
6. Review the captured photo preview.
7. Select **Submit prediction**.

The possible outputs are:

- `This is an image of a cat`
- `This is an image of a dog`
- `I can't tell if this image is a cat or a dog with high confidence`


## Data And Privacy

This app saves each submitted image and prediction result in a local SQLite
database on the machine running the app.

Saved data includes the image, filename, content type, cat probability,
prediction message, and timestamp.

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
