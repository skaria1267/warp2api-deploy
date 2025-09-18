#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版 OpenAI 兼容服务器 - 支持代理池
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# 导入代理包装器（会根据配置决定是否激活）
import protobuf2openai.proxy_wrapper

# 导入原始应用
from openai_compat import *

if __name__ == "__main__":
    import os
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
    
    main()
