#!/usr/bin/env python3
"""
测试ICP备案查询API
"""
import requests
import json

def test_api():
    """测试API接口"""
    base_url = "http://localhost:8000"
    
    # 测试健康检查
    print("测试健康检查接口...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"健康检查: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"健康检查失败: {e}")
        return
    
    # 测试域名查询
    test_domain = "scgzyun.com"
    print(f"\n测试域名查询: {test_domain}")
    try:
        response = requests.get(f"{base_url}/query?domain={test_domain}")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("查询结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"查询失败: {response.text}")
    except Exception as e:
        print(f"查询请求失败: {e}")

if __name__ == "__main__":
    test_api()
