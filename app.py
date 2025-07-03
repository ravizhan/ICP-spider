from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import base64
import json
import requests
import hashlib
import time
from urllib import parse
from crack import Crack
import uuid
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ICP备案查询API", description="通过域名查询ICP备案信息", version="1.0.0")

# 全局变量
crack = Crack()


def auth():
    """获取认证token"""
    t = str(round(time.time()))
    data = {
        "authKey": hashlib.md5(("testtest" + t).encode()).hexdigest(),
        "timeStamp": t
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://beian.miit.gov.cn/",
        "Content-Type": "application/x-www-form-urlencoded",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Origin": "https://beian.miit.gov.cn"
    }
    
    resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/auth", 
                        headers=headers, data=parse.urlencode(data)).text
    return json.loads(resp)["params"]["bussiness"]


def getImage(token):
    """获取验证码图片"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://beian.miit.gov.cn/",
        "Token": token,
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Origin": "https://beian.miit.gov.cn"
    }
    payload = {
        "clientUid": "point-" + str(uuid.uuid4())
    }
    
    resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/getCheckImagePoint",
                        headers=headers, json=payload).json()
    return resp["params"], payload["clientUid"]


def aes_ecb_encrypt(plaintext: bytes, key: bytes, block_size=16):
    """AES ECB加密"""
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)

    padding_length = block_size - (len(plaintext) % block_size)
    plaintext_padded = plaintext + bytes([padding_length]) * padding_length

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext_padded) + encryptor.finalize()

    return base64.b64encode(ciphertext).decode('utf-8')


def generate_pointjson(big_img, small_img, secretKey):
    """生成点击坐标JSON"""
    boxes = crack.detect(big_img)
    if not boxes:
        raise Exception("文字检测失败")
        
    points = crack.siamese(small_img, boxes)
    new_points = [[p[0] + 20, p[1] + 20] for p in points]
    pointJson = [{"x": p[0], "y": p[1]} for p in new_points]
    enc_pointJson = aes_ecb_encrypt(json.dumps(pointJson).replace(" ", "").encode(), secretKey.encode())
    return enc_pointJson


def checkImage(token, uuid_token, secretKey, clientUid, pointJson):
    """验证图片点击"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://beian.miit.gov.cn/",
        "Token": token,
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Origin": "https://beian.miit.gov.cn"
    }
    data = {
        "token": uuid_token,
        "secretKey": secretKey,
        "clientUid": clientUid,
        "pointJson": pointJson
    }
    resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/checkImage", 
                        headers=headers, json=data).json()
    if resp["code"] == 200:
        return resp["params"]["sign"]
    return False


def query_domain(token, sign, uuid_token, domain):
    """查询域名ICP信息"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://beian.miit.gov.cn/",
        "Token": token,
        "Sign": sign,
        "Uuid": uuid_token,
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Origin": "https://beian.miit.gov.cn",
        "Content-Type": "application/json",
        "Cookie": "__jsluid_s=" + str(uuid.uuid4().hex[:32])
    }
    data = {"pageNum": "", "pageSize": "", "unitName": domain, "serviceType": 1}
    resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/icpAbbreviateInfo/queryByCondition",
                        headers=headers, data=json.dumps(data).replace(" ", "")).text
    return json.loads(resp)


def query_icp_with_retry(domain: str, max_retries: int = 5):
    """带重试机制的ICP查询"""
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试查询域名 {domain}，第 {attempt + 1} 次")
            
            # 获取token
            token = auth()
            time.sleep(0.1)
            
            # 获取验证码
            params, clientUid = getImage(token)
            
            # 生成点击坐标
            pointjson = generate_pointjson(params["bigImage"], params["smallImage"], params["secretKey"])
            time.sleep(0.5)
            
            # 验证图片
            sign = checkImage(token, params["uuid"], params["secretKey"], clientUid, pointjson)
            time.sleep(0.5)
            
            if not sign:
                raise Exception("验证码验证失败")
            
            # 查询域名信息
            result = query_domain(token, sign, params["uuid"], domain)
            logger.info(f"域名 {domain} 查询成功")
            return result
            
        except Exception as e:
            logger.error(f"第 {attempt + 1} 次尝试失败: {str(e)}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail=f"查询失败，已重试{max_retries}次: {str(e)}")
            time.sleep(1)  # 重试前等待1秒


@app.get("/")
async def root():
    """根路径"""
    return {"message": "ICP备案查询API", "version": "1.0.0"}


@app.get("/query")
async def query_icp(domain: str = Query(..., description="要查询的域名", example="scgzyun.com")):
    """
    查询域名的ICP备案信息
    
    - **domain**: 要查询的域名
    """
    try:
        result = query_icp_with_retry(domain)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询域名 {domain} 时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "timestamp": int(time.time())}
