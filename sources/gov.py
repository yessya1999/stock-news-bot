"""政府/监管源 - 中国政府网、央行"""
import requests
from bs4 import BeautifulSoup
from config import REQUEST_HEADERS, REQUEST_TIMEOUT, MAX_NEWS_PER_SOURCE


def _fetch_gov() -> list[dict]:
    """中国政府网 - 部门联播（可静态抓取）"""
    news_list = []
    try:
        url = "https://www.gov.cn/lianbo/bumen/"
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        for a_tag in soup.select("a"):
            title = a_tag.get_text(strip=True)
            if not title or len(title) < 10:
                continue
            href = a_tag.get("href", "")
            # 过滤非新闻链接
            if not href or "gov.cn" not in href and not href.startswith("/"):
                continue
            if href.startswith("/"):
                href = "https://www.gov.cn" + href
            news_list.append({
                "title": title,
                "content": title,
                "source": "中国政府网",
                "url": href,
                "pub_time": "",
            })
            if len(news_list) >= MAX_NEWS_PER_SOURCE:
                break
    except Exception as e:
        print(f"[中国政府网] 抓取失败: {e}")
    return news_list


def _fetch_pbc() -> list[dict]:
    """央行新闻发布"""
    news_list = []
    try:
        # 央行新闻发布页
        url = "http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html"
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        for a_tag in soup.select("td a, .portlet_list a"):
            title = a_tag.get_text(strip=True)
            if not title or len(title) < 8:
                continue
            href = a_tag.get("href", "")
            if not href or href == "#":
                continue
            if href.startswith("/"):
                href = "http://www.pbc.gov.cn" + href
            news_list.append({
                "title": title,
                "content": title,
                "source": "央行",
                "url": href,
                "pub_time": "",
            })
            if len(news_list) >= 10:
                break
    except Exception as e:
        print(f"[央行] 抓取失败: {e}")
    return news_list


def fetch_gov() -> list[dict]:
    """汇总所有政府/监管源"""
    results = []
    results.extend(_fetch_gov())
    results.extend(_fetch_pbc())
    return results
