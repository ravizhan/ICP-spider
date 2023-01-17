import json
import requests
import hashlib
import time
from urllib import parse
from capture import Crack


def auth():
    t = str(round(time.time()))
    data = {
        "authKey": hashlib.md5(("testtest" + t).encode()).hexdigest(),
        "timeStamp": t
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Referer": "https://beian.miit.gov.cn/",
        "Content-Type": "application/x-www-form-urlencoded",
        "Connection": "keep-alive",
        "Accept": "*/*"
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Referer": "https://beian.miit.gov.cn/",
        "token": token,
        "Connection": "keep-alive",
        "Accept": "*/*"
    }
    try:
        resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/getCheckImage",
                             headers=headers).json()
        return resp["params"]["bigImage"], resp["params"]["uuid"]
    except Exception:
        time.sleep(5)
        resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/getCheckImage",
                             headers=headers).json()
        return resp["params"]["bigImage"], resp["params"]["uuid"]


def checkImage(key, value):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Referer": "https://beian.miit.gov.cn/",
        "token": token,
        "Connection": "keep-alive",
        "Accept": "*/*"
    }
    data = {"key": key, "value": value}
    resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/checkImage", headers=headers,
                         json=data).json()
    if resp["code"] == 200:
        return resp["params"]
    return False


def query(sign, domain):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Referer": "https://beian.miit.gov.cn/",
        "token": token,
        "sign": sign,
        "Connection": "keep-alive",
        "Accept": "*/*"
    }
    data = {"pageNum": "", "pageSize": "", "unitName": domain}
    resp = requests.post("https://hlwicpfwc.miit.gov.cn/icpproject_query/api/icpAbbreviateInfo/queryByCondition",
                         headers=headers, json=data).json()
    return resp


crack = Crack()
token = auth()
time.sleep(0.1)
content, uuid = getImage()
pos = str(round(crack.inference(content)))
res = checkImage(uuid, pos)
if res:
    print(query(res, "baidu.com"))
else:
    print("failed")
