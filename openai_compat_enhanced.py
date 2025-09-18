#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版 OpenAI 兼容服务器 - 支持代理池
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# 导入代理包装器（会根据配置决定是否激活）
import protobuf2openai.proxy_wrapper

# 现在运行原始的 openai_compat.py
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info("🚀 Warp2API Enhanced Edition")
    logger.info("="*60)
    
    force_proxy = os.getenv("FORCE_PROXY", "false").lower() == "true"
    proxy_pool = os.getenv("PROXY_POOL_URL", "")
    
    if force_proxy and proxy_pool:
        logger.info("🔄 模式: 代理模式")
        logger.info(f"📊 切换间隔: 每{os.getenv('SWITCH_INTERVAL', '3')}个请求")
    else:
        logger.info("⚡ 模式: 直连模式")
    logger.info("="*60)
    
    # 导入并运行原始的 openai_compat
    import argparse
    import uvicorn
    from common.config import config
    from protobuf2openai.app import app
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="OpenAI兼容API服务器")
    parser.add_argument(
        "--port", type=int, default=config.OPENAI_COMPAT_PORT,
        help=f"服务器监听端口 (默认: {config.OPENAI_COMPAT_PORT})"
    )
    args = parser.parse_args()
    
    # 运行服务器
    uvicorn.run(
        app,
        host=config.HOST,
        port=args.port,
        log_level="info",
    )
