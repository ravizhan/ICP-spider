## 警告

本项目仅限用于学习研究

任何后果与本人无关

## 特点

- 使用yolov5识别滑动验证码，用魔法打败魔法
- 准确率在95%以上，如有需要可自行训练模型
- 直接对接官网，数据权威准确

## 使用方法

下载[yolov5项目](https://github.com/ultralytics/yolov5)

```
git clone https://github.com/ultralytics/yolov5
```

安装依赖

```
pip install -r requirements.txt
```

运行 `main.py` 即可

## 注意事项

- 官网反爬策略较为玄学，请勿疯狂请求

- 项目中有两种格式的模型，CPU推理使用`onnx`更快，GPU推理使用`pt`更快，默认为`onnx`

  位置在`capture.py`

- 本模型使用预训练模型yolov5n进行训练