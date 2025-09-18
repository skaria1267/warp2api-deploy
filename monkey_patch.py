#!/usr/bin/env python3
"""
全局HTTP代理补丁 - 强制所有请求通过代理池
"""

import os
import sys

def patch_all_requests():
    """拦截所有HTTP库"""
    proxy_url = os.getenv("PROXY_POOL_URL", "")
    force_proxy = os.getenv("FORCE_PROXY", "false").lower() == "true"
    
    if not (proxy_url and force_proxy):
        print("代理未启用")
        return
    
    print(f"启用全局代理: {proxy_url}")
    
    # 设置环境变量（影响某些库）
    proxy_with_protocol = f"{proxy_url}/proxy?url="
    os.environ['HTTP_PROXY'] = proxy_with_protocol
    os.environ['HTTPS_PROXY'] = proxy_with_protocol
    os.environ['http_proxy'] = proxy_with_protocol
    os.environ['https_proxy'] = proxy_with_protocol
    
    # 排除本地地址
    os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0'
    os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0'

# 在导入其他模块前执行
patch_all_requests()
