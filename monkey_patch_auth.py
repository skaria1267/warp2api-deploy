#!/usr/bin/env python3
"""
Monkey patch auth模块使其通过代理
"""

import os
import httpx

# 获取代理配置
proxy_url = os.getenv("PROXY_POOL_URL", "")
force_proxy = os.getenv("FORCE_PROXY", "false").lower() == "true"

if proxy_url and force_proxy:
    print(f"[Monkey Patch] 激活auth代理: {proxy_url}")
    
    # 保存原始的httpx.AsyncClient
    _original_async_client = httpx.AsyncClient
    
    # 创建代理版本
    class ProxyAsyncClient(_original_async_client):
        def __init__(self, *args, **kwargs):
            # 强制添加代理
            kwargs['proxies'] = {
                'http://': proxy_url,
                'https://': proxy_url
            }
            kwargs['verify'] = False  # 禁用SSL验证
            super().__init__(*args, **kwargs)
    
    # 替换httpx.AsyncClient
    httpx.AsyncClient = ProxyAsyncClient
    print("[Monkey Patch] httpx.AsyncClient已被代理版本替换")
