import json

import torch, base64
from PIL import Image, ImageOps
from io import BytesIO


class Crack:
    def __init__(self):
        self.model = torch.hub.load('./yolov5', 'custom', path='best.onnx', force_reload=True, skip_validation=True,
                                    trust_repo=True, source='local')

    def inference(self, base64_data):
        im = Image.open(BytesIO(base64.b64decode(base64_data)))
        im = ImageOps.expand(im, (0, 2, 12, 0))
        results = self.model(im, size=512)
        res = results.pandas().xyxy[0].to_json()
        return json.loads(res)["xmin"]["0"]
