# ICP备案查询工具

## 警告

本项目仅限用于学习研究

禁止售卖本项目，禁止用于违法目的

任何后果与本人无关

## 特点

- 使用yolov8+孪生网络解决点选验证码

- 准确率高，只要不是这种阴间图片，基本没问题

  ![image-20240403142830308](https://s21.ax1x.com/2024/04/03/pFH4pKU.png)

- 识别一次用时2~3秒

- 使用ONNX模型

## 使用方法

安装依赖

```shell
pip install -r requirements.txt
```

修改`main.py`中要查询的域名

运行 `main.py` 即可

## 备注

- 官网反爬策略较为玄学，请勿疯狂请求
- 运行结果为原始响应，如有需要请自行解析

## 鸣谢

[Siamese-pytorch](https://github.com/bubbliiiing/Siamese-pytorch) 孪生神经网络

[ultralytics](https://github.com/ultralytics/ultralytics) YOLOv8

没有他们的付出就没有本项目的诞生

## 开源协议

依据上游项目 [ultralytics](https://github.com/ultralytics/ultralytics) 所使用的AGPLv3协议，现以相同协议开源本项目，请自觉遵守。
