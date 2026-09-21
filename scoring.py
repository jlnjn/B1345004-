from collections import defaultdict

SECTION_NAMES = {
    "A": "財務承受能力",
    "B": "投資目標與時間",
    "C": "風險偏好與行為",
    "D": "投資知識與經驗",
}

BEHAVIOR_NAMES = {
    "loss_aversion": "損失規避",
    "anxiety": "焦慮程度",
    "herding": "從眾傾向",
    "confidence": "判斷信心",
    "overconfidence": "過度自信風險",
}

def _to_100(scores):
    if not scores:
        return 0.0
    avg = sum(scores) / len(scores)
    return round((avg - 1) / 4 * 100, 1)

def risk_band(score):
    if score < 40:
        return "低風險傾向"
    if score < 70:
        return "中度風險傾向"
    return "高風險傾向"

def calculate_profile(questionnaire, answers):
    section_scores = {}
    factor_scores = defaultdict(list)
    weights = {}

    for section in questionnaire["sections"]:
        values = []
        weights[section["id"]] = section["weight"]

        for q in section["questions"]:
            item = answers.get(q["id"])
            if item is None:
                continue
            score = item["score"]
            values.append(score)
            factor_scores[q.get("factor", "other")].append(score)

        section_scores[section["id"]] = _to_100(values)

    overall = round(
        sum(section_scores[sid] * weights[sid] for sid in section_scores), 1
    )

    # Behavioral signals are kept separate from the overall number.
    behavioral = {}
    for factor in ["loss_aversion", "anxiety", "herding", "confidence", "overconfidence"]:
        if factor in factor_scores:
            behavioral[factor] = _to_100(factor_scores[factor])

    capacity = section_scores.get("A", 0)
    attitude = section_scores.get("C", 0)
    gap = round(capacity - attitude, 1)

    flags = []
    if abs(gap) >= 30:
        if gap > 0:
            flags.append("財務上能承受的風險明顯高於心理／行為上願意承受的風險。")
        else:
            flags.append("心理／行為上願意承受的風險明顯高於目前財務條件可承受的風險。")

    loss_capacity = _to_100(factor_scores.get("loss_capacity", []))
    if loss_capacity < 40:
        flags.append("20% 投資損失可能對生活或財務計畫造成明顯影響。")

    liquidity = _to_100(factor_scores.get("liquidity", []))
    if liquidity < 40:
        flags.append("目前緊急備用資金／流動性相對有限。")

    total_assets = _to_100(factor_scores.get("total_assets", []))
    financial_assets = _to_100(factor_scores.get("financial_assets", []))
    investable_assets = _to_100(factor_scores.get("investable_assets", []))

    # These flags help AI distinguish asset-rich from genuinely liquid/investable capacity.
    if total_assets >= 60 and investable_assets < 40:
        flags.append("總資產相對較高，但可投資資產相對有限；資產可能較集中於非流動性用途。")
    if financial_assets >= 60 and liquidity < 40:
        flags.append("金融資產不低，但可立即支應生活需求的流動性仍相對有限。")

    return {
        "section_scores": section_scores,
        "overall_score": overall,
        "risk_level": risk_band(overall),
        "behavioral_signals": behavioral,
        "capacity_attitude_gap": gap,
        "flags": flags,
    }
