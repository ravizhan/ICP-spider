import base64
import numpy as np
import cv2
from fastdeploy.vision.detection import YOLOv8


class Crack:
    def __init__(self):
        self.model = YOLOv8("./best.onnx")

    def inference(self, base64_data):
        img_data = base64.b64decode(base64_data)
        img_array = np.fromstring(img_data, np.uint8)
        img = cv2.imdecode(img_array, 1)
        img = np.array(img).astype("float32")
        result = self.model.predict(img)
        # im = fastdeploy.vision.vis_detection(img, result)
        # cv2.imwrite("result.jpg", im)
        if len(result.scores) == 1:
            return result.boxes[0][0]
        for res in range(len(result.scores)):
            if result.scores[res] >= 0.9:
                return result.boxes[res][0]
