"""数据源采集器"""
from sources.cls import fetch_cls
from sources.wallstreetcn import fetch_wallstreetcn
from sources.sina_finance import fetch_sina_finance
from sources.eastmoney import fetch_eastmoney
from sources.jin10 import fetch_jin10
from sources.gov import fetch_gov

ALL_SOURCES = [
    ("财联社", fetch_cls),
    ("华尔街见闻", fetch_wallstreetcn),
    ("新浪财经", fetch_sina_finance),
    ("东方财富", fetch_eastmoney),
    ("金十数据", fetch_jin10),
    ("政府/监管", fetch_gov),
]

# 高频监控源（突发快讯用）
BREAKING_SOURCES = [
    ("财联社", fetch_cls),
    ("华尔街见闻", fetch_wallstreetcn),
]
