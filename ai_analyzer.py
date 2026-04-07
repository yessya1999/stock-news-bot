"""AI 分析模块 - 使用硅基流动 SiliconFlow 进行新闻摘要和影响评分"""
import json
import config

# 使用 openai SDK 兼容硅基流动 API
from openai import OpenAI


SYSTEM_PROMPT = """你是一个专业的股市财经分析师。对于给定的新闻，请严格按 JSON 格式返回分析结果。

要求：
1. summary: 新闻摘要（30-80字，概括核心事件）
2. analysis: 股市影响分析（50-150字，说明为什么影响股市、影响逻辑、哪些个股或ETF值得关注）
3. score: 股市影响评分（1-10，10=极高影响）
4. direction: 影响方向（利好/利空/中性）
5. sectors: 影响板块（如"银行、地产"，列出2-5个）
6. market: 影响市场（A股/美股/两者）

只返回 JSON，不要其他文字。示例：
{"summary":"央行宣布降准0.5个百分点，预计释放长期资金约1.2万亿元","analysis":"降准直接增加银行可贷资金，降低资金成本，利好信贷扩张。房地产行业有望获得更多融资支持，基建投资也将受益于宽松流动性。关注招商银行、万科A、中国建筑等标的。","score":9,"direction":"利好","sectors":"银行、地产、基建","market":"A股"}"""

BATCH_PROMPT = """你是一个专业的股市财经分析师。对以下多条新闻逐条分析，返回一个 JSON 数组。

每条新闻的分析格式：
{"index": 序号, "summary": "新闻摘要(30-80字)", "analysis": "股市影响分析(50-150字，说明影响逻辑和值得关注的标的)", "score": 评分1-10, "direction": "利好/利空/中性", "sectors": "影响板块(2-5个)", "market": "A股/美股/两者"}

只返回 JSON 数组，不要其他文字。"""


def _get_client() -> OpenAI:
    """获取硅基流动 AI 客户端"""
    return OpenAI(
        api_key=config.SILICONFLOW_API_KEY,
        base_url=config.SILICONFLOW_BASE_URL,
    )


def _get_model() -> str:
    return config.SILICONFLOW_MODEL


def analyze_single(news: dict) -> dict:
    """分析单条新闻"""
    client = _get_client()
    text = f"标题：{news['title']}\n内容：{news['content']}\n来源：{news['source']}"

    try:
        resp = client.chat.completions.create(
            model=_get_model(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        result_text = resp.choices[0].message.content.strip()
        # 清理 markdown 代码块标记
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        result = json.loads(result_text)
        return {**news, **result}
    except Exception as e:
        print(f"[AI分析] 单条分析失败: {e}")
        return {
            **news,
            "summary": news["title"][:50],
            "score": 5,
            "direction": "中性",
            "sectors": "未知",
            "market": "A股",
        }


def analyze_batch(news_list: list[dict]) -> list[dict]:
    """批量分析新闻（节省 API 调用）"""
    if not news_list:
        return []

    # 每批最多处理 10 条，避免 token 过长
    batch_size = 10
    all_results = []

    for i in range(0, len(news_list), batch_size):
        batch = news_list[i:i + batch_size]
        numbered = "\n".join(
            f"[{j+1}] 标题：{n['title']} | 内容：{n['content'][:100]} | 来源：{n['source']}"
            for j, n in enumerate(batch)
        )

        client = _get_client()
        try:
            resp = client.chat.completions.create(
                model=_get_model(),
                messages=[
                    {"role": "system", "content": BATCH_PROMPT},
                    {"role": "user", "content": numbered},
                ],
                temperature=0.3,
                max_tokens=4000,
            )
            result_text = resp.choices[0].message.content.strip()
            if result_text.startswith("```"):
                result_text = result_text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            analyses = json.loads(result_text)

            for analysis in analyses:
                idx = analysis.get("index", 0) - 1
                if 0 <= idx < len(batch):
                    all_results.append({**batch[idx], **analysis})
                    del all_results[-1]["index"]
        except Exception as e:
            print(f"[AI分析] 批量分析失败，回退单条模式: {e}")
            for n in batch:
                all_results.append(analyze_single(n))

    return all_results


def filter_breaking(analyzed_news: list[dict]) -> list[dict]:
    """筛选突发重大事件（评分 >= 阈值）"""
    return [
        n for n in analyzed_news
        if n.get("score", 0) >= config.BREAKING_SCORE_THRESHOLD
    ]
