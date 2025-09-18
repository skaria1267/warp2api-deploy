#!/usr/bin/env python3
"""
最终启动脚本 - 先应用monkey patch
"""

import os
import sys

# 第一步：应用monkey patch
proxy_url = os.getenv("PROXY_POOL_URL", "")
force_proxy = os.getenv("FORCE_PROXY", "false").lower() == "true"

print("="*60)
print("🚀 Warp2API Final Version")
print("="*60)

if proxy_url and force_proxy:
    print(f"🔄 代理模式")
    print(f"🌐 代理池: {proxy_url}")
    
    # 应用monkey patch
    import monkey_patch_auth
else:
    print("⚡ 直连模式")

print("="*60)

# 第二步：启动服务器
import subprocess
import time

# 启动Warp服务器
warp_process = subprocess.Popen(
    ["python", "server.py", "--port", "28888"]
)
print(f"✅ Warp server started (PID: {warp_process.pid})")

time.sleep(5)

# 启动OpenAI服务器
openai_process = subprocess.Popen(
    ["python", "openai_compat.py", "--port", "28889"]
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
