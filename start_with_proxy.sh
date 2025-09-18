#!/bin/bash
echo "========================================"
echo "🚀 Warp2API with Proxy Pool"
echo "========================================"

if [ -n "$PROXY_POOL_URL" ] && [ "$FORCE_PROXY" = "true" ]; then
    echo "🔄 代理模式已启用"
    echo "🌐 代理池: $PROXY_POOL_URL"
    echo "📊 切换间隔: 每${SWITCH_INTERVAL}个请求"
    
    # 导出代理环境变量
    export HTTP_PROXY="${PROXY_POOL_URL}/proxy?url="
    export HTTPS_PROXY="${PROXY_POOL_URL}/proxy?url="
    export NO_PROXY="localhost,127.0.0.1,0.0.0.0"
else
    echo "⚡ 直连模式"
fi

echo "========================================"

# 启动服务
python -c "import monkey_patch" 2>/dev/null || true
python server.py --port 28888 &
WARP_PID=$!
echo "✅ Warp server started (PID: $WARP_PID)"

sleep 5

python openai_compat_enhanced.py --port 28889 &
OPENAI_PID=$!
echo "✅ OpenAI server started (PID: $OPENAI_PID)"

echo ""
echo "📍 API: http://localhost:28889/v1"
echo "🔑 Key: sk-text"
echo ""

wait $WARP_PID $OPENAI_PID
