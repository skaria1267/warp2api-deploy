#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP请求代理包装器
"""

import httpx
import asyncio
from typing import Optional, Dict, Any
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from common.proxy_manager import proxy_manager

logger = logging.getLogger(__name__)

# 保存原始的 httpx.AsyncClient
_original_async_client = httpx.AsyncClient

class ProxyAsyncClient:
    """代理版 AsyncClient"""
    
    def __init__(self, *args, **kwargs):
        self.client = _original_async_client(*args, **kwargs)
    
    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """拦截请求，根据配置决定是否使用代理"""
        # 本地请求直接发送
        if "localhost" in url or "127.0.0.1" in url:
            return await self.client.request(method, url, **kwargs)
        
        # 根据配置决定是否使用代理
        if proxy_manager.force_proxy and proxy_manager.proxy_pool_url:
            logger.debug(f"通过代理池: {method} {url}")
            return await proxy_manager.make_request(
                method=method,
                url=url,
                headers=kwargs.get("headers"),
                json_data=kwargs.get("json"),
                data=kwargs.get("content") or kwargs.get("data"),
                timeout=kwargs.get("timeout", 60)
            )
        else:
            logger.debug(f"直连请求: {method} {url}")
            return await self.client.request(method, url, **kwargs)
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("POST", url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("PUT", url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("DELETE", url, **kwargs)
    
    async def __aenter__(self):
        await self.client.__aenter__()
        return self
    
    async def __aexit__(self, *args):
        return await self.client.__aexit__(*args)
    
    def __getattr__(self, name):
        return getattr(self.client, name)

# 只在强制代理模式下替换
if proxy_manager.force_proxy and proxy_manager.proxy_pool_url:
    httpx.AsyncClient = ProxyAsyncClient
    logger.info("✅ HTTP代理已激活")
else:
    logger.info("ℹ️ 直连模式")
