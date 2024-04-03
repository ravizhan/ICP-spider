import base64
import onnxruntime
import cv2
import numpy as np


class Crack:
    def __init__(self):
        pass

    def read_base64_image(self, base64_string):
        # 解码Base64字符串为字节串
        img_data = base64.b64decode(base64_string)

        # 将解码后的字节串转换为numpy数组（OpenCV使用numpy作为其基础）
        np_array = np.frombuffer(img_data, np.uint8)

        # 使用OpenCV的imdecode函数将字节数据解析为cv::Mat对象
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        return img

    def detect(self, big_img):
        confidence_thres = 0.7
        iou_thres = 0.7
        session = onnxruntime.InferenceSession("yolov8.onnx")
        model_inputs = session.get_inputs()

        self.big_img = self.read_base64_image(big_img)
        img_height, img_width = self.big_img.shape[:2]
        img = cv2.cvtColor(self.big_img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (512, 192))
        image_data = np.array(img) / 255.0
        image_data = np.transpose(image_data, (2, 0, 1))
        image_data = np.expand_dims(image_data, axis=0).astype(np.float32)
        input = {model_inputs[0].name: image_data}
        output = session.run(None, input)
        outputs = np.transpose(np.squeeze(output[0]))
        rows = outputs.shape[0]
        boxes, scores = [], []
        x_factor = img_width / 512
        y_factor = img_height / 192
        for i in range(rows):
            classes_scores = outputs[i][4:]
            max_score = np.amax(classes_scores)
            if max_score >= confidence_thres:
                x, y, w, h = outputs[i][0], outputs[i][1], outputs[i][2], outputs[i][3]
                left = int((x - w / 2) * x_factor)
                top = int((y - h / 2) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                boxes.append([left, top, width, height])
                scores.append(max_score)
        indices = cv2.dnn.NMSBoxes(boxes, scores, confidence_thres, iou_thres)
        new_boxes = [boxes[i] for i in indices]
        # print(new_boxes)
        if len(new_boxes) != 5:
            return False
        return new_boxes

    def siamese(self, small_img, boxes):
        session = onnxruntime.InferenceSession("siamese.onnx")
        positions = [165, 200, 231, 265]
        result_list = []
        for x in positions:
            if len(result_list) == 4:
                break
            raw_image2 = self.read_base64_image(small_img)
            raw_image2 = raw_image2[11:11 + 28, x:x + 26]
            img2 = cv2.cvtColor(raw_image2, cv2.COLOR_BGR2RGB)
            img2 = cv2.resize(img2, (105, 105))
            image_data_2 = np.array(img2) / 255.0
            image_data_2 = np.transpose(image_data_2, (2, 0, 1))
            image_data_2 = np.expand_dims(image_data_2, axis=0).astype(np.float32)
            for box in boxes:
                raw_image1 = self.big_img[box[1]:box[1] + box[3] + 2, box[0]:box[0] + box[2] + 2]
                img1 = cv2.cvtColor(raw_image1, cv2.COLOR_BGR2RGB)
                img1 = cv2.resize(img1, (105, 105))

                image_data_1 = np.array(img1) / 255.0
                image_data_1 = np.transpose(image_data_1, (2, 0, 1))
                image_data_1 = np.expand_dims(image_data_1, axis=0).astype(np.float32)

                inputs = {'input': image_data_1, "input.53": image_data_2}
                output = session.run(None, inputs)
                output_sigmoid = 1 / (1 + np.exp(-output[0]))
                res = output_sigmoid[0][0]
                # print(res)
                if res >= 0.7:
                    # print("\n")
                    # print(res)
                    # print(box)
                    result_list.append([box[0], box[1]])
                    break
        return result_list


if __name__ == '__main__':
    crack = Crack()
    boxes = crack.detect("./1.png")
    print(crack.siamese("./2.png", boxes))
