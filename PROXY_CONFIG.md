# Warp2API 代理池配置说明

## 环境变量说明

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| PROXY_POOL_URL | 空 | 代理池服务地址 |
| FORCE_PROXY | false | 是否强制使用代理 |
| SWITCH_INTERVAL | 3 | 每几个请求切换一次IP |
| PROXY_MAX_RETRIES | 5 | 请求失败最大重试次数 |
| PROXY_RETRY_DELAY | 0.5 | 重试延迟（秒） |

## 使用模式

### 1. 直连模式（默认）
- FORCE_PROXY=false 或不设置代理池地址
- 直接请求目标服务器
- 性能最佳

### 2. 代理模式
- FORCE_PROXY=true 且设置 PROXY_POOL_URL
- 所有请求通过代理池
- 按间隔自动切换IP

## 配置示例

需要在 Zeabur 或其他平台设置环境变量启用代理功能。
