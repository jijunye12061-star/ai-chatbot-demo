import os

# LLM 配置
API_KEY = "VOplCUjdbDBjO1Zf4f2eE5CcBd244835Ad31D5F6Ab7699F9"
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
