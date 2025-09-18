FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0

# 代理配置
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
RUN pip install --no-cache-dir httpx requests

RUN python precompile_protos.py || echo "Protobuf precompilation skipped"

EXPOSE 28888 28889

CMD ["/app/start_with_proxy.sh"]
