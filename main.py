"""主入口 - 定时摘要和突发监控"""
import sys
import time

from sources import ALL_SOURCES, BREAKING_SOURCES
from ai_analyzer import analyze_batch, filter_breaking
from dedup import deduplicate
from wecom import send_daily_digest, send_breaking_news


def collect_news(source_list: list) -> list[dict]:
    """从指定源列表采集新闻"""
    all_news = []
    for name, fetcher in source_list:
        print(f"[采集] 正在抓取: {name}")
        try:
            news = fetcher()
            print(f"[采集] {name} 获取 {len(news)} 条")
            all_news.extend(news)
        except Exception as e:
            print(f"[采集] {name} 失败: {e}")
        time.sleep(1)  # 礼貌间隔
    return all_news


def run_daily_digest(period: str = "早报"):
    """执行定时摘要任务"""
    print(f"\n{'='*50}")
    print(f"开始执行定时摘要任务 - {period}")
    print(f"{'='*50}\n")

    # 1. 采集所有源
    raw_news = collect_news(ALL_SOURCES)
    print(f"\n[汇总] 共采集 {len(raw_news)} 条原始新闻")

    if not raw_news:
        print("[汇总] 无新闻，跳过")
        return

    # 2. 去重
    unique_news = deduplicate(raw_news)
    if not unique_news:
        print("[汇总] 去重后无新内容，跳过")
        return

    # 3. AI 分析
    print(f"\n[AI] 开始分析 {len(unique_news)} 条新闻...")
    analyzed = analyze_batch(unique_news)
    print(f"[AI] 分析完成，{len(analyzed)} 条结果")

    # 4. 按评分排序，取 Top N
    analyzed.sort(key=lambda x: x.get("score", 0), reverse=True)
    top_news = analyzed[:15]

    # 5. 推送
    send_daily_digest(top_news, period)


def run_breaking_monitor():
    """执行突发监控任务"""
    print(f"\n{'='*50}")
    print("开始执行突发监控任务")
    print(f"{'='*50}\n")

    # 1. 仅抓取高频源
    raw_news = collect_news(BREAKING_SOURCES)
    print(f"\n[汇总] 共采集 {len(raw_news)} 条快讯")

    if not raw_news:
        print("[汇总] 无快讯，跳过")
        return

    # 2. 去重
    unique_news = deduplicate(raw_news)
    if not unique_news:
        print("[汇总] 无新内容，跳过")
        return

    # 3. AI 分析
    print(f"\n[AI] 开始分析 {len(unique_news)} 条快讯...")
    analyzed = analyze_batch(unique_news)

    # 4. 筛选重大事件
    breaking = filter_breaking(analyzed)
    print(f"[突发] 发现 {len(breaking)} 条重大事件")

    # 5. 逐条推送突发
    for news in breaking:
        send_breaking_news(news)
        time.sleep(2)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "digest"

    if mode == "digest":
        # 根据时间判断早/午/晚报
        hour = time.localtime().tm_hour
        if hour < 10:
            period = "早报"
        elif hour < 14:
            period = "午报"
        else:
            period = "晚报"
        run_daily_digest(period)
    elif mode == "breaking":
        run_breaking_monitor()
    elif mode == "test":
        # 测试模式：只采集不推送
        print("[测试] 采集所有源...")
        raw = collect_news(ALL_SOURCES)
        print(f"[测试] 共获取 {len(raw)} 条新闻")
        for n in raw[:5]:
            print(f"  - [{n['source']}] {n['title'][:50]}")
    else:
        print(f"用法: python main.py [digest|breaking|test]")
        sys.exit(1)


if __name__ == "__main__":
    main()
