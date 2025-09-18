#!/usr/bin/env python3
"""
简单启动脚本 - 直接修补httpx来使用代理
"""

import os
import sys
import subprocess
import time

# 设置代理环境变量
proxy_url = os.getenv("PROXY_POOL_URL", "")
force_proxy = os.getenv("FORCE_PROXY", "false").lower() == "true"

print("="*60)
print("🚀 Warp2API with Proxy Support")
print("="*60)

if proxy_url and force_proxy:
    print(f"🔄 代理模式已启用")
    print(f"🌐 代理池: {proxy_url}")
    print(f"📊 切换间隔: 每{os.getenv('SWITCH_INTERVAL', '3')}个请求")
    
    # 设置系统代理
    os.environ['HTTP_PROXY'] = f"{proxy_url}/proxy?url="
    os.environ['HTTPS_PROXY'] = f"{proxy_url}/proxy?url="
    os.environ['http_proxy'] = f"{proxy_url}/proxy?url="
    os.environ['https_proxy'] = f"{proxy_url}/proxy?url="
    os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0'
else:
    print("⚡ 直连模式")

print("="*60)

# 启动服务
env = os.environ.copy()

# 启动Warp服务器
warp_cmd = ["python", "server.py", "--port", "28888"]
warp_process = subprocess.Popen(warp_cmd, env=env)
print(f"✅ Warp server started (PID: {warp_process.pid})")

time.sleep(5)

# 启动OpenAI服务器
openai_cmd = ["python", "openai_compat_enhanced.py", "--port", "28889"]
openai_process = subprocess.Popen(openai_cmd, env=env)
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
