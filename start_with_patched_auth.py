#!/usr/bin/env python3
"""
启动脚本 - 使用修补后的auth模块
"""

import os
import sys
import subprocess
import time

# 设置代理环境变量
proxy_url = os.getenv("PROXY_POOL_URL", "")
force_proxy = os.getenv("FORCE_PROXY", "false").lower() == "true"

print("="*60)
print("🚀 Warp2API with Proxy Pool Support")
print("="*60)

if proxy_url and force_proxy:
    print(f"🔄 代理模式已启用")
    print(f"🌐 代理池: {proxy_url}")
    print(f"📊 切换间隔: 每{os.getenv('SWITCH_INTERVAL', '3')}个请求")
    
    # 猴子补丁 - 替换auth模块
    print("🔧 应用auth代理补丁...")
    import importlib.util
    
    # 加载补丁模块
    spec = importlib.util.spec_from_file_location(
        "warp2protobuf.core.auth",
        "warp2protobuf/core/auth_patched.py"
    )
    patched_auth = importlib.util.module_from_spec(spec)
    sys.modules['warp2protobuf.core.auth'] = patched_auth
    spec.loader.exec_module(patched_auth)
else:
    print("⚡ 直连模式")

print("="*60)

# 启动服务
env = os.environ.copy()

warp_process = subprocess.Popen(
    ["python", "server.py", "--port", "28888"],
    env=env
)
print(f"✅ Warp server started (PID: {warp_process.pid})")

time.sleep(5)

openai_process = subprocess.Popen(
    ["python", "openai_compat_enhanced.py", "--port", "28889"],
    env=env
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
