import os

# LLM 配置
API_KEY = os.getenv("LLM_API_KEY", "")
if not API_KEY:
    raise ValueError("环境变量 LLM_API_KEY 未设置，请在 .env 文件或启动命令中配置")
BASE_URL = "https://dd-ai-api.eastmoney.com/v1"
MODEL = "DeepSeek-V3"
MAX_TOKENS = 2000
SYSTEM_PROMPT = "You are a helpful assistant."

# 环境
ENV = os.getenv("APP_ENV", "dev")

# 数据库配置
DB_CONFIG = {
    "dev": {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "dev",
        "database": "fund_platform",
    },
    "prod": {
        "host": os.getenv("DORIS_HOST", ""),
        "port": 9030,
        "user": os.getenv("DORIS_USER", ""),
        "password": os.getenv("DORIS_PASSWORD", ""),
        "database": "tytdata",
    },
}[ENV]
