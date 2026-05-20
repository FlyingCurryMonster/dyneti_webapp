MODEL_PATH = './model.tflite'

from email.mime import image

import numpy as np
from tensorflow import lite as tf_lite
from PIL import Image

def load_model():
    # Load TFLite model and allocate tensors.
    interpreter = tf_lite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    return interpreter


def preprocess_input(
        # image: Image,
        img_path: str,
        shape: tuple,
        rescale: bool = True        
        ):
    img = Image.open(img_path).resize(shape)
    img_resize = img.resize(shape)
    img_array = np.array(img_resize, dtype=np.float32) # get rid of dtype hardcode
    img_array = np.expand_dims(img_array, axis=0) # add batch dimension
    if rescale:
        img_array /= 255.0 # scale to [0, 1], check if PIL can figure out what the scale of the image is
    return img_array
    

def predict(input:np.ndarray, interpreter: tf_lite.Interpreter):
    '''
    Outputs probability of cat
    '''
    # assert that the input matches what the interpreter expects
    assert input.shape == interpreter.get_input_details()[0]['shape'], "Input shape does not match model input specification"
    
    interpreter.set_tensor(interpreter.get_input_details()[0]['index'], input)
    interpreter.invoke()
    
    return interpreter.get_tensor(interpreter.get_output_details()[0]['index'])

interpreter = load_model()
model_img_shape = interpreter.get_input_details()[0]['shape'][1:3] # get the expected input shape (height, width)
input = preprocess_input(img_path='cat.jpg', shape=model_img_shape)

model_out = predict(input, interpreter)
print(model_out)

# cat_img = Image.open('cat.jpg')
# cat_img_resize = cat_img.resize((224, 224))
# cat_input = np.array(cat_img_resize, dtype=np.float32) / 255
# cat_input = np.expand_dims(cat_input, axis=0)
# # Load TFLite model and allocate tensors.

# # Get input and output tensors.
# input_details = interpreter.get_input_details()
# output_details = interpreter.get_output_details()

# # Test model on random input data.
# input_shape = input_details[0]['shape']
# input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)
# interpreter.set_tensor(input_details[0]['index'], input_data)

# interpreter.invoke()

# # The function `get_tensor()` returns a copy of the tensor data.
# # Use `tensor()` in order to get a pointer to the tensor.
# output_data = interpreter.get_tensor(output_details[0]['index'])
