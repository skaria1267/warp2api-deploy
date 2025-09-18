#!/usr/bin/env python3
"""
获取JWT token - 支持代理
"""

import os
import sys
import asyncio
import json

sys.path.insert(0, '/app')

async def main():
    proxy_url = os.getenv("PROXY_POOL_URL", "")
    
    if proxy_url:
        print(f"使用代理: {proxy_url}")
        from common.proxy_manager import proxy_manager
        
        # 尝试多个节点
        for i in range(5):
            print(f"\n尝试 {i+1}/5...")
            await proxy_manager.switch_proxy_node()
            
            try:
                # 尝试获取匿名token
                response = await proxy_manager.make_request(
                    method="POST",
                    url="https://app.warp.dev/auth/api/anonymous",
                    headers={"Content-Type": "application/json"},
                    json_data={},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("access_token")
                    if token:
                        print(f"✅ 成功获取token!")
                        print(f"Token: {token[:50]}...")
                        print(f"\n设置环境变量:")
                        print(f"WARP_JWT={token}")
                        return token
                else:
                    print(f"❌ 状态码: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 错误: {e}")
    else:
        print("未配置代理，使用直连")
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://app.warp.dev/auth/api/anonymous",
                json={}
            )
            if response.status_code == 200:
                token = response.json().get("access_token")
                print(f"Token: {token}")
                return token
    
    print("获取失败")
    return None

if __name__ == "__main__":
    asyncio.run(main())
