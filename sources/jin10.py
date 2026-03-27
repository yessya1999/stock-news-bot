"""金十数据 - 美联储决议、非农、CPI 等经济数据日历"""
import requests
from config import REQUEST_TIMEOUT, MAX_NEWS_PER_SOURCE


def fetch_jin10() -> list[dict]:
    """抓取金十数据快讯"""
    news_list = []
    try:
        url = "https://flash-api.jin10.com/get_flash_list"
        params = {
            "channel": "-8200",
            "max_time": "",
            "vip": "1",
        }
        headers = {
            "x-app-id": "bVBF4FyRTn5NJF5n",
            "x-version": "1.0.0",
            "Referer": "https://www.jin10.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
        }
        resp = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("data", []) or []
        for item in items[:MAX_NEWS_PER_SOURCE]:
            # 金十数据的内容在 data 字段中
            content_data = item.get("data", {})
            content = content_data.get("content", "").strip() if isinstance(content_data, dict) else ""
            if not content:
                # 尝试 vip_title 或 pic 字段
                content = content_data.get("vip_title", "").strip() if isinstance(content_data, dict) else ""
            if not content:
                continue

            pub_time = item.get("time", "")
            news_list.append({
                "title": content[:60],
                "content": content,
                "source": "金十数据",
                "url": "https://www.jin10.com/",
                "pub_time": pub_time,
            })
    except Exception as e:
        print(f"[金十数据] 抓取失败: {e}")
    return news_list
