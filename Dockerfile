FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -e .

RUN python precompile_protos.py || echo "Protobuf precompilation skipped"

EXPOSE 28888 28889

RUN echo '#!/bin/bash\n\
echo "🚀 Starting Warp Bridge Server..."\n\
python server.py --port 28888 &\n\
WARP_PID=$!\n\
echo "✅ Warp server started with PID: $WARP_PID"\n\
\n\
sleep 5\n\
\n\
echo "🚀 Starting OpenAI Compatible Server..."\n\
python openai_compat.py --port 28889 &\n\
OPENAI_PID=$!\n\
echo "✅ OpenAI server started with PID: $OPENAI_PID"\n\
\n\
echo "🎉 Both servers are running!"\n\
echo "📍 OpenAI API: http://localhost:28889/v1"\n\
echo "🔑 API Key: sk-text"\n\
echo "📊 Health Check: http://localhost:28889/health"\n\
\n\
wait $WARP_PID $OPENAI_PID\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
