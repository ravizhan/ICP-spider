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


def auth():
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
    try:
        resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/auth", headers=headers,
                             data=parse.urlencode(data)).text
        return json.loads(resp)["params"]["bussiness"]
    except Exception:
        time.sleep(5)
        resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/auth", headers=headers,
                             data=parse.urlencode(data)).text
        return json.loads(resp)["params"]["bussiness"]


def getImage():
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
    try:
        resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/getCheckImagePoint",
                             headers=headers, json=payload).json()
        return resp["params"], payload["clientUid"]
    except Exception:
        time.sleep(5)
        resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/getCheckImagePoint",
                             headers=headers, json=payload).json()
        return resp["params"], payload["clientUid"]


def aes_ecb_encrypt(plaintext: bytes, key: bytes, block_size=16):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)

    padding_length = block_size - (len(plaintext) % block_size)
    plaintext_padded = plaintext + bytes([padding_length]) * padding_length

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext_padded) + encryptor.finalize()

    return base64.b64encode(ciphertext).decode('utf-8')


def generate_pointjson(big_img, small_img, secretKey):
    boxes = crack.detect(big_img)
    if boxes:
        print("文字检测成功")
    else:
        print("文字检测失败,请重试")
        raise Exception("文字检测失败,请重试")
    points = crack.siamese(small_img, boxes)
    print("文字匹配成功")
    new_points = [[p[0] + 20, p[1] + 20] for p in points]
    pointJson = [{"x": p[0], "y": p[1]} for p in new_points]
    # print(json.dumps(pointJson))
    enc_pointJson = aes_ecb_encrypt(json.dumps(pointJson).replace(" ", "").encode(), secretKey.encode())
    return enc_pointJson


def checkImage(uuid_token, secretKey, clientUid, pointJson):
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
    resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/checkImage", headers=headers,
                         json=data).json()
    if resp["code"] == 200:
        # print(resp["params"])
        return resp["params"]["sign"]
    return False


def query(sign, uuid_token, domain):
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
        "Cookie": "__jsluid_s="+str(uuid.uuid4().hex[:32])
    }
    data = {"pageNum": "", "pageSize": "", "unitName": domain, "serviceType": 1}
    resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/icpAbbreviateInfo/queryByCondition",
                         headers=headers, data=json.dumps(data).replace(" ","")).text
    return resp


crack = Crack()
token = auth()
time.sleep(0.1)
print("正在获取验证码")
params, clientUid = getImage()
pointjson = generate_pointjson(params["bigImage"], params["smallImage"], params["secretKey"])
time.sleep(0.5)
sign = checkImage(params["uuid"], params["secretKey"], clientUid, pointjson)
time.sleep(0.5)
if sign:
    print(query(sign, params["uuid"],"baidu.com"))
else:
    print("failed")
