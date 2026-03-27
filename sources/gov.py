"""政府/监管源 - 新华社、中国政府网、证监会、央行"""
import feedparser
import requests
from bs4 import BeautifulSoup
from config import REQUEST_HEADERS, REQUEST_TIMEOUT, MAX_NEWS_PER_SOURCE


def _fetch_gov_rss() -> list[dict]:
    """中国政府网 RSS"""
    news_list = []
    try:
        feed = feedparser.parse("http://www.gov.cn/rss/govall.xml")
        for entry in feed.entries[:MAX_NEWS_PER_SOURCE]:
            title = entry.get("title", "").strip()
            if not title:
                continue
            news_list.append({
                "title": title,
                "content": entry.get("summary", title),
                "source": "中国政府网",
                "url": entry.get("link", ""),
                "pub_time": entry.get("published", ""),
            })
    except Exception as e:
        print(f"[中国政府网RSS] 抓取失败: {e}")
    return news_list


def _fetch_xinhua() -> list[dict]:
    """新华社财经频道"""
    news_list = []
    try:
        url = "http://qc.wa.news.cn/nodeart/list?nid=11147664&pgnum=1&cnt=20&tp=1&orderby=1"
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("data", {}).get("list", []) or []
        for item in items[:MAX_NEWS_PER_SOURCE]:
            title = item.get("Title", "").strip()
            if not title:
                continue
            news_list.append({
                "title": title,
                "content": item.get("Abstract", title),
                "source": "新华社",
                "url": item.get("LinkUrl", ""),
                "pub_time": item.get("PubTime", ""),
            })
    except Exception as e:
        print(f"[新华社] 抓取失败: {e}")
    return news_list


def _fetch_pbc() -> list[dict]:
    """央行公告"""
    news_list = []
    try:
        url = "http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html"
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        for item in soup.select(".newslist_style li")[:10]:
            a_tag = item.select_one("a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            if href and not href.startswith("http"):
                href = "http://www.pbc.gov.cn" + href
            news_list.append({
                "title": title,
                "content": title,
                "source": "央行",
                "url": href,
                "pub_time": "",
            })
    except Exception as e:
        print(f"[央行] 抓取失败: {e}")
    return news_list


def fetch_gov() -> list[dict]:
    """汇总所有政府/监管源"""
    results = []
    results.extend(_fetch_gov_rss())
    results.extend(_fetch_xinhua())
    results.extend(_fetch_pbc())
    return results
