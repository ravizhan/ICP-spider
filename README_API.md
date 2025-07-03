# ICP备案查询API

这是一个基于FastAPI的ICP备案信息查询服务，可以通过域名查询相关的ICP备案信息。

## 功能特性

- 🚀 基于FastAPI框架，性能优异
- 🔄 自动重试机制，最多重试5次
- 🛡️ 自动处理验证码识别
- 📋 RESTful API接口
- 📖 自动生成API文档

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务

### 方法1：使用Docker (推荐)

```bash
# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方法2：本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## API接口

### 查询域名ICP备案信息

**GET** `/query?domain={domain}`

#### 参数
- `domain` (必需): 要查询的域名，例如 `scgzyun.com`

#### 示例请求
```bash
curl "http://localhost:8000/query?domain=scgzyun.com"
```

#### 示例响应
```json
{
  "code": 200,
  "msg": "操作成功",
  "params": {
    "endRow": 0,
    "firstPage": 1,
    "hasNextPage": false,
    "hasPreviousPage": false,
    "isFirstPage": true,
    "isLastPage": true,
    "lastPage": 1,
    "list": [
      {
        "contentTypeName": "",
        "domain": "scgzyun.com",
        "domainId": 990004509801,
        "leaderName": "",
        "limitAccess": "否",
        "mainId": 110001964865,
        "mainLicence": "蜀ICP备19011193号",
        "natureName": "企业",
        "serviceId": 990005092743,
        "serviceLicence": "蜀ICP备19011193号-6",
        "unitName": "成都七淘网络科技有限公司",
        "updateRecordTime": "2024-03-01 09:25:43"
      }
    ],
    "navigatePages": 8,
    "navigatepageNums": [1],
    "nextPage": 1,
    "pageNum": 1,
    "pageSize": 10,
    "pages": 1,
    "prePage": 1,
    "size": 1,
    "startRow": 0,
    "total": 1
  },
  "success": true
}
```

### 健康检查

**GET** `/health`

#### 示例请求
```bash
curl "http://localhost:8000/health"
```

#### 示例响应
```json
{
  "status": "healthy",
  "timestamp": 1704362400
}
```

## API文档

启动服务后，可以访问以下地址查看自动生成的API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 错误处理

- 自动重试机制：当查询失败时，会自动重试最多5次
- 详细错误信息：返回具体的错误原因
- HTTP状态码：标准的HTTP状态码响应

## 测试

### 本地测试
```bash
python test_api.py
```

### Docker测试
```bash
# 在容器中运行测试
docker-compose exec icp-spider-api python test_api.py

# 或者直接测试API接口
curl "http://localhost:8000/health"
curl "http://localhost:8000/query?domain=scgzyun.com"
```

## 注意事项

1. 服务依赖于外部的验证码识别模型文件：`yolov8.onnx` 和 `siamese.onnx`
2. 确保这些模型文件在项目根目录中
3. 首次运行可能需要一些时间来加载模型
4. 建议在生产环境中使用更强的错误处理和日志记录

## 项目结构

```
ICP-spider/
├── app.py              # FastAPI应用主文件
├── test_api.py         # 测试脚本
├── main.py             # 原始脚本
├── crack.py            # 验证码识别模块
├── requirements.txt    # 依赖列表
├── Dockerfile          # Docker镜像构建文件
├── docker-compose.yml  # Docker编排文件
├── .dockerignore       # Docker忽略文件
├── yolov8.onnx        # YOLO模型文件
├── siamese.onnx       # Siamese模型文件
└── README_API.md      # 项目说明
```

## Docker部署

### 构建和运行
```bash
# 构建镜像
docker build -t icp-spider-api .

# 运行容器
docker run -d -p 8000:8000 --name icp-spider-api icp-spider-api

# 或使用docker-compose
docker-compose up -d --build
```

### 生产环境部署
```bash
# 使用docker-compose部署
docker-compose -f docker-compose.yml up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```
