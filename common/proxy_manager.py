#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理池管理器 - 可配置的代理策略
"""

import os
import time
import asyncio
import logging
from typing import Optional, Dict, Any
import httpx
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class ProxyManager:
    """代理池管理器"""
    
    def __init__(self):
        # 配置项 - 从环境变量读取
        self.proxy_pool_url = os.getenv("PROXY_POOL_URL", "")
        self.force_proxy = os.getenv("FORCE_PROXY", "false").lower() == "true"
        self.switch_interval = int(os.getenv("SWITCH_INTERVAL", "3"))
        self.max_retries = int(os.getenv("PROXY_MAX_RETRIES", "5"))
        self.retry_delay = float(os.getenv("PROXY_RETRY_DELAY", "0.5"))
        
        self.request_count = 0
        self.last_switch = 0
        
        if self.proxy_pool_url:
            logger.info("="*50)
            logger.info("代理池配置:")
            logger.info(f"  代理池: 已配置")
            logger.info(f"  强制代理: {self.force_proxy}")
            logger.info(f"  切换间隔: 每{self.switch_interval}个请求")
            logger.info(f"  最大重试: {self.max_retries}次")
            logger.info("="*50)
        else:
            logger.info("未配置代理池，使用直连模式")
    
    async def switch_proxy_node(self):
        """切换代理节点"""
        if not self.proxy_pool_url:
            return False
            
        try:
            switch_url = f"{self.proxy_pool_url}/switch"
            async with httpx.AsyncClient() as client:
                response = await client.get(switch_url, timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ 切换到节点: {result.get('switched_to', 'unknown')}")
                    self.last_switch = self.request_count
                    return True
        except Exception as e:
            logger.warning(f"切换节点失败: {e}")
        return False
    
    async def make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        data: Optional[Any] = None,
        timeout: float = 60
    ) -> httpx.Response:
        """
        发送请求 - 根据配置决定是否使用代理
        """
        self.request_count += 1
        
        # 判断是否需要切换节点
        if self.force_proxy and self.proxy_pool_url and self.switch_interval > 0:
            if self.request_count % self.switch_interval == 0:
                await self.switch_proxy_node()
        
        # 如果不强制使用代理或未配置代理池，直接发送请求
        if not self.force_proxy or not self.proxy_pool_url:
            logger.debug(f"直连模式: {method} {url}")
            async with httpx.AsyncClient() as client:
                return await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data if json_data else None,
                    content=data if data else None,
                    timeout=timeout
                )
        
        # 使用代理池发送请求
        logger.debug(f"代理模式: {method} {url}")
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                proxy_url = f"{self.proxy_pool_url}/proxy"
                
                async with httpx.AsyncClient() as client:
                    if method.upper() in ['GET', 'DELETE']:
                        response = await client.request(
                            method=method,
                            url=proxy_url,
                            params={"url": url},
                            headers=headers,
                            timeout=timeout
                        )
                    else:
                        response = await client.request(
                            method="POST",
                            url=proxy_url,
                            params={"url": url},
                            headers=headers,
                            json=json_data if json_data else None,
                            content=data if data else None,
                            timeout=timeout
                        )
                    
                    # 处理错误
                    if response.status_code >= 500 or response.status_code == 429:
                        logger.warning(f"请求失败 ({response.status_code})，切换节点重试")
                        await self.switch_proxy_node()
                        await asyncio.sleep(self.retry_delay)
                        retries += 1
                        continue
                    
                    return response
                    
            except Exception as e:
                last_error = e
                logger.error(f"请求错误: {e}")
                
                if retries < self.max_retries - 1:
                    await self.switch_proxy_node()
                    await asyncio.sleep(self.retry_delay)
                    retries += 1
                else:
                    break
        
        raise Exception(f"请求失败（重试{retries}次）: {last_error}")

# 全局代理管理器
proxy_manager = ProxyManager()
