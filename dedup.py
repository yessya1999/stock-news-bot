"""新闻去重模块 - 基于 JSON 文件存储"""
import hashlib
import json
import os
import time
from config import DEDUP_DB_PATH

# 去重记录保留时间（秒）：48小时
RETENTION_SECONDS = 48 * 3600


def _news_hash(news: dict) -> str:
    """生成新闻唯一标识"""
    text = f"{news.get('source', '')}:{news.get('title', '')}:{news.get('content', '')[:100]}"
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _load_db() -> dict:
    """加载去重数据库"""
    if not os.path.exists(DEDUP_DB_PATH):
        return {}
    try:
        with open(DEDUP_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_db(db: dict):
    """保存去重数据库"""
    with open(DEDUP_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False)


def _cleanup(db: dict) -> dict:
    """清理过期记录"""
    now = time.time()
    return {k: v for k, v in db.items() if now - v < RETENTION_SECONDS}


def deduplicate(news_list: list[dict]) -> list[dict]:
    """对新闻列表去重，返回未见过的新闻"""
    db = _load_db()
    db = _cleanup(db)

    unique = []
    now = time.time()

    for news in news_list:
        h = _news_hash(news)
        if h not in db:
            db[h] = now
            unique.append(news)

    _save_db(db)
    print(f"[去重] 输入 {len(news_list)} 条，去重后 {len(unique)} 条新闻")
    return unique
