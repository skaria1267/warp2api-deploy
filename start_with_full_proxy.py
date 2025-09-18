#!/usr/bin/env python3
"""
完全代理启动脚本 - 确保所有请求都通过代理池
"""

import os
import sys
import subprocess
import time
import asyncio

# 设置代理环境变量（影响底层库）
proxy_url = os.getenv("PROXY_POOL_URL", "")
force_proxy = os.getenv("FORCE_PROXY", "false").lower() == "true"

if proxy_url and force_proxy:
    print(f"🔄 设置全局代理: {proxy_url}")
    proxy_endpoint = f"{proxy_url}/proxy?url="
    os.environ['HTTP_PROXY'] = proxy_endpoint
    os.environ['HTTPS_PROXY'] = proxy_endpoint
    os.environ['http_proxy'] = proxy_endpoint
    os.environ['https_proxy'] = proxy_endpoint
    os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0'
    os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0'

# 猴子补丁 - 在导入任何模块前执行
import urllib.request
import urllib3
import ssl

# 禁用SSL验证警告
urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

# 现在才导入项目模块
sys.path.insert(0, '/app')

async def get_anonymous_token_with_proxy():
    """通过代理获取匿名token"""
    print("🔑 尝试通过代理获取匿名token...")
    
    if not proxy_url or not force_proxy:
        print("未启用代理，跳过")
        return
    
    try:
        from common.proxy_manager import proxy_manager
        import httpx
        
        # 先切换节点
        await proxy_manager.switch_proxy_node()
        
        # 尝试获取匿名token
        anonymous_url = "https://app.warp.dev/auth/api/anonymous"
        response = await proxy_manager.make_request(
            method="POST",
            url=anonymous_url,
            headers={"Content-Type": "application/json"},
            json_data={},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                os.environ['WARP_JWT'] = token
                print(f"✅ 成功获取匿名token")
                return token
    except Exception as e:
        print(f"❌ 获取匿名token失败: {e}")
    
    return None

def main():
    print("="*60)
    print("🚀 Warp2API with Full Proxy Support")
    print("="*60)
    
    if proxy_url and force_proxy:
        print(f"🔄 代理模式已启用")
        print(f"🌐 代理池: {proxy_url}")
        print(f"📊 切换间隔: 每{os.getenv('SWITCH_INTERVAL', '3')}个请求")
        
        # 尝试获取匿名token
        asyncio.run(get_anonymous_token_with_proxy())
    else:
        print("⚡ 直连模式")
    
    print("="*60)
    
    # 启动服务
    warp_process = subprocess.Popen(
        ["python", "server.py", "--port", "28888"],
        env=os.environ.copy()
    )
    print(f"✅ Warp server started (PID: {warp_process.pid})")
    
    time.sleep(5)
    
    openai_process = subprocess.Popen(
        ["python", "openai_compat_enhanced.py", "--port", "28889"],
        env=os.environ.copy()
    )
    print(f"✅ OpenAI server started (PID: {openai_process.pid})")
    
    print("")
    print("📍 API: http://localhost:28889/v1")
    print("🔑 Key: sk-text")
    print("")
    
    try:
        warp_process.wait()
        openai_process.wait()
    except KeyboardInterrupt:
        print("\n正在关闭...")
        warp_process.terminate()
        openai_process.terminate()

if __name__ == "__main__":
    main()
