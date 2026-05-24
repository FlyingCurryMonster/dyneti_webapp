import numpy as np
from tflite_runtime.interpreter import Interpreter
from PIL import Image

class ModelEngine:
    def __init__(self, model_path):
        self.model_path = model_path
        self.interpreter = self.load_model()

        if len(self.interpreter.get_input_details()[0]['shape']) == 4:
            height, width = self.interpreter.get_input_details()[0]['shape'][1:3]
            self.input_img_shape = (height, width)
        else:
            raise ValueError("Can only hanlde models with input shapes of len 4 (batch_size, height, width, channels)") 

        self.input_dtype = self.interpreter.get_input_details()[0]['dtype']
   

    def predict(self, input: np.ndarray):
        '''
        Outputs probability of cat
        '''
        # assert that the input matches what the interpreter expects
        assert input.shape == tuple(self.interpreter.get_input_details()[0]['shape']), "Input shape does not match model input specification"
        
        self.interpreter.set_tensor(self.interpreter.get_input_details()[0]['index'], input)
        self.interpreter.invoke()
        
        return self.interpreter.get_tensor(self.interpreter.get_output_details()[0]['index'])

    def load_model(self):
        # Load TFLite model and allocate tensors.
        interpreter = Interpreter(model_path=self.model_path)
        interpreter.allocate_tensors()
        return interpreter
    
    def preprocess_input(
        self,
        img_path: str,
        rescale: bool = True
        ):
        def pil_scale_value(img):
            if img.mode in ("RGB", "RGBA", "L", "P"):
                return 255.0
            if img.mode in ("I;16", "I;16L", "I;16B"):
                return 65535.0
            if img.mode == "1":
                return 1.0
            if img.mode == "F":
                raise ValueError("Image mode 'F' is already float; cannot determine intended scale for rescaling")
            raise ValueError(f"Unsupported image mode: {img.mode}")

        img = Image.open(img_path).resize(self.input_img_shape)
        img_resize = img.resize(self.input_img_shape)
        img_array = np.array(img_resize, dtype=self.input_dtype) # get rid of dtype hardcode
        img_array = np.expand_dims(img_array, axis=0) # add batch dimension
        if rescale:   
            scale_val = pil_scale_value(img) if pil_scale_value(img) is not None else max(img_array.max(), 1.0) # avoid divide by zero
            img_array /= scale_val # scale to [0, 1]

        return img_array
    
if __name__ == "__main__":
    from pathlib import Path
    import tomllib

    project_root = Path(__file__).resolve().parent
    with (project_root / "config.toml").open("rb") as config_file:
        config = tomllib.load(config_file)

    model_path = (project_root / config["paths"]["model"]).resolve()
    test_images_path = (project_root / config["paths"]["test_images"]).resolve()
    model_engine = ModelEngine(str(model_path))
    # test cat image output
    
    input = model_engine.preprocess_input(test_images_path / "cat.jpg")
    output = model_engine.predict(input)
    print(f"Cat probability: {output[0][0]:.4f}")

    # test dog image output
    input = model_engine.preprocess_input(test_images_path / "dog2.webp")
    output = model_engine.predict(input)
    print(f"Cat probability: {output[0][0]:.4f}")
