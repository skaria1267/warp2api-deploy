#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP请求代理包装器 - 拦截所有HTTP请求
"""

import httpx
import requests
import urllib3
import asyncio
from typing import Optional, Dict, Any
import logging
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from common.proxy_manager import proxy_manager

logger = logging.getLogger(__name__)

# ========== HTTPX 异步客户端代理 ==========
_original_async_client = httpx.AsyncClient

class ProxyAsyncClient:
    """代理版 AsyncClient"""
    
    def __init__(self, *args, **kwargs):
        # 如果启用代理，添加代理配置
        if proxy_manager.force_proxy and proxy_manager.proxy_pool_url:
            kwargs['proxies'] = {
                'http://': f'{proxy_manager.proxy_pool_url}/proxy?url=',
                'https://': f'{proxy_manager.proxy_pool_url}/proxy?url='
            }
        self.client = _original_async_client(*args, **kwargs)
    
    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        # 本地请求直接发送
        if any(x in url for x in ["localhost", "127.0.0.1", "0.0.0.0"]):
            return await self.client.request(method, url, **kwargs)
        
        # 使用代理
        if proxy_manager.force_proxy and proxy_manager.proxy_pool_url:
            logger.debug(f"[HTTPX] 代理: {method} {url}")
            return await proxy_manager.make_request(
                method=method,
                url=url,
                headers=kwargs.get("headers"),
                json_data=kwargs.get("json"),
                data=kwargs.get("content") or kwargs.get("data"),
                timeout=kwargs.get("timeout", 60)
            )
        else:
            return await self.client.request(method, url, **kwargs)
    
    async def get(self, url: str, **kwargs):
        return await self.request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs):
        return await self.request("POST", url, **kwargs)
    
    async def put(self, url: str, **kwargs):
        return await self.request("PUT", url, **kwargs)
    
    async def delete(self, url: str, **kwargs):
        return await self.request("DELETE", url, **kwargs)
    
    async def __aenter__(self):
        await self.client.__aenter__()
        return self
    
    async def __aexit__(self, *args):
        return await self.client.__aexit__(*args)
    
    def __getattr__(self, name):
        return getattr(self.client, name)

# ========== Requests 库代理 ==========
try:
    _original_request = requests.request
    _original_get = requests.get
    _original_post = requests.post
    
    def proxy_request(method, url, **kwargs):
        """同步请求的代理包装"""
        if any(x in url for x in ["localhost", "127.0.0.1", "0.0.0.0"]):
            return _original_request(method, url, **kwargs)
        
        if proxy_manager.force_proxy and proxy_manager.proxy_pool_url:
            logger.debug(f"[Requests] 代理: {method} {url}")
            # 使用代理池
            proxy_url = f'{proxy_manager.proxy_pool_url}/proxy?url={url}'
            return _original_request(method, proxy_url, **kwargs)
        
        return _original_request(method, url, **kwargs)
    
    def proxy_get(url, **kwargs):
        return proxy_request("GET", url, **kwargs)
    
    def proxy_post(url, **kwargs):
        return proxy_request("POST", url, **kwargs)
    
    # 替换 requests 函数
    if proxy_manager.force_proxy and proxy_manager.proxy_pool_url:
        requests.request = proxy_request
        requests.get = proxy_get
        requests.post = proxy_post
        logger.info("✅ Requests库代理已激活")
        
except ImportError:
    pass

# ========== 替换 HTTPX ==========
if proxy_manager.force_proxy and proxy_manager.proxy_pool_url:
    httpx.AsyncClient = ProxyAsyncClient
    logger.info("✅ HTTPX代理已激活")
else:
    logger.info("ℹ️ 直连模式")

# ========== 猴子补丁：拦截 warp2protobuf 的请求 ==========
def patch_warp_requests():
    """修补 warp2protobuf 模块的HTTP请求"""
    try:
        # 尝试修补 auth 模块
        from warp2protobuf.core import auth
        
        # 保存原始函数
        if hasattr(auth, 'acquire_anonymous_access_token'):
            _original_acquire = auth.acquire_anonymous_access_token
            
            async def proxy_acquire_anonymous():
                """通过代理申请匿名token"""
                if proxy_manager.force_proxy and proxy_manager.proxy_pool_url:
                    logger.info("🔄 通过代理申请匿名token...")
                    # 切换节点后再申请
                    await proxy_manager.switch_proxy_node()
                return await _original_acquire()
            
            auth.acquire_anonymous_access_token = proxy_acquire_anonymous
            logger.info("✅ 已修补匿名token申请函数")
    except Exception as e:
        logger.warning(f"修补auth模块失败: {e}")

# 执行修补
if proxy_manager.force_proxy and proxy_manager.proxy_pool_url:
    patch_warp_requests()

logger.info(f"🔧 代理包装器已加载 - 模式: {'代理' if proxy_manager.force_proxy else '直连'}")
