FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0

# 代理池配置 - 默认不启用
ENV PROXY_POOL_URL=""
ENV FORCE_PROXY="false"
ENV SWITCH_INTERVAL="3"
ENV PROXY_MAX_RETRIES="5"
ENV PROXY_RETRY_DELAY="0.5"

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir httpx

RUN python precompile_protos.py || echo "Protobuf precompilation skipped"

EXPOSE 28888 28889

RUN echo '#!/bin/bash\n\
echo "========================================"\n\
echo "🚀 Warp2API Enhanced Edition"\n\
echo "========================================"\n\
\n\
if [ -n "$PROXY_POOL_URL" ] && [ "$FORCE_PROXY" = "true" ]; then\n\
    echo "🔄 模式: 代理模式"\n\
    echo "📊 切换间隔: 每${SWITCH_INTERVAL}个请求"\n\
else\n\
    echo "⚡ 模式: 直连模式"\n\
fi\n\
echo "========================================"\n\
\n\
python server.py --port 28888 &\n\
WARP_PID=$!\n\
echo "✅ Warp server started (PID: $WARP_PID)"\n\
\n\
sleep 5\n\
\n\
python openai_compat_enhanced.py --port 28889 &\n\
OPENAI_PID=$!\n\
echo "✅ OpenAI server started (PID: $OPENAI_PID)"\n\
\n\
echo ""\n\
echo "📍 API: http://localhost:28889/v1"\n\
echo "🔑 Key: sk-text"\n\
echo ""\n\
\n\
wait $WARP_PID $OPENAI_PID\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
