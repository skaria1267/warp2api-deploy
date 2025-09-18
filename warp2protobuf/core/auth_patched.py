#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patched JWT Authentication - 使用代理池
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 导入原始auth模块的所有内容
from warp2protobuf.core.auth import *
import warp2protobuf.core.auth as original_auth

# 导入代理管理器
try:
    from common.proxy_manager import proxy_manager
    USE_PROXY = proxy_manager.force_proxy and proxy_manager.proxy_pool_url
except:
    USE_PROXY = False

# 重写acquire_anonymous_access_token函数
async def acquire_anonymous_access_token_with_proxy() -> str:
    """通过代理获取匿名token"""
    logger.info("🔑 申请匿名访问令牌（代理模式）...")
    
    if USE_PROXY:
        # 使用正确的GraphQL URL
        url = "https://app.warp.dev/graphql/v2?op=CreateAnonymousUser"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "operationName": "CreateAnonymousUser",
            "variables": {},
            "query": "mutation CreateAnonymousUser { createAnonymousUser { user { id email } token { accessToken refreshToken } } }"
        }
        
        try:
            # 先切换节点
            await proxy_manager.switch_proxy_node()
            
            # 通过代理发送请求
            response = await proxy_manager.make_request(
                method="POST",
                url=url,
                headers=headers,
                json_data=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                token_data = data.get("data", {}).get("createAnonymousUser", {}).get("token", {})
                access_token = token_data.get("accessToken")
                if access_token:
                    logger.info("✅ 成功获取匿名token（通过代理）")
                    # 保存到环境变量
                    os.environ['WARP_JWT'] = access_token
                    return access_token
            else:
                logger.error(f"获取失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"代理请求失败: {e}")
    
    # 如果代理失败或未启用，使用原始方法
    return await original_auth.acquire_anonymous_access_token()

# 替换原函数
original_auth.acquire_anonymous_access_token = acquire_anonymous_access_token_with_proxy

# 重写refresh_jwt_token函数
original_refresh = original_auth.refresh_jwt_token

async def refresh_jwt_token_with_proxy() -> dict:
    """通过代理刷新JWT token"""
    if USE_PROXY:
        logger.info("🔄 刷新JWT令牌（代理模式）...")
        try:
            # 尝试通过代理刷新
            import base64
            from ..config.settings import REFRESH_TOKEN_B64, REFRESH_URL, CLIENT_VERSION, OS_CATEGORY, OS_NAME, OS_VERSION
            
            env_refresh = os.getenv("WARP_REFRESH_TOKEN")
            if env_refresh:
                payload = f"grant_type=refresh_token&refresh_token={env_refresh}"
            else:
                payload = base64.b64decode(REFRESH_TOKEN_B64).decode('utf-8')
            
            headers = {
                "x-warp-client-version": CLIENT_VERSION,
                "x-warp-os-category": OS_CATEGORY,
                "x-warp-os-name": OS_NAME,
                "x-warp-os-version": OS_VERSION,
                "content-type": "application/x-www-form-urlencoded",
                "accept": "*/*"
            }
            
            # 切换节点
            await proxy_manager.switch_proxy_node()
            
            response = await proxy_manager.make_request(
                method="POST",
                url=REFRESH_URL,
                headers=headers,
                data=payload.encode('utf-8'),
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ JWT刷新成功（通过代理）")
                return response.json()
        except Exception as e:
            logger.error(f"代理刷新失败: {e}")
    
    # 回退到原始方法
    return await original_refresh()

original_auth.refresh_jwt_token = refresh_jwt_token_with_proxy
