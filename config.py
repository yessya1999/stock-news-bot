"""项目配置"""
import os

# 企业微信应用推送配置
WECOM_CORP_ID = os.environ.get("WECOM_CORP_ID", "")
WECOM_CORP_SECRET = os.environ.get("WECOM_CORP_SECRET", "")
WECOM_AGENT_ID = os.environ.get("WECOM_AGENT_ID", "")
WECOM_TO_USER = os.environ.get("WECOM_TO_USER", "@all")  # @all 表示全员

# AI API 配置 (硅基流动 SiliconFlow，兼容 OpenAI SDK)
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
SILICONFLOW_MODEL = os.environ.get("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct")  # 免费模型

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
