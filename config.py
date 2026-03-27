"""项目配置"""
import os

# PushPlus 推送配置
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")
PUSHPLUS_URL = "https://www.pushplus.plus/send"

# AI API 配置 (支持 DeepSeek / Gemini)
AI_PROVIDER = os.environ.get("AI_PROVIDER", "deepseek")  # deepseek 或 gemini
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# 去重数据库路径
DEDUP_DB_PATH = os.environ.get("DEDUP_DB_PATH", "news_dedup.json")

# 突发快讯阈值（评分 >= 此值才推送）
BREAKING_SCORE_THRESHOLD = 8

# 请求配置
REQUEST_TIMEOUT = 15
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 每个源最多抓取的新闻条数
MAX_NEWS_PER_SOURCE = 20
