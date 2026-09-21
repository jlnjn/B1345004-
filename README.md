# AI Investor Risk Assessment — Version 3

此版本依 Blueprint 擴充為四大區塊：

1. Financial Capacity：收入、現金流、總資產、金融資產、可投資資產、流動性、負債、未來資金需求、Loss Capacity
2. Goal & Time Horizon：投資目標、投資期限、提領需求
3. Behavioral & Emotional Assessment：Loss Aversion、Anxiety、Herding、Confidence、Overconfidence
4. Knowledge & Experience：投資知識與過去經驗

結果頁包含：
- Baseline Risk Score
- Low / Medium / High 基礎分類
- 四大構面分數
- Behavioral Signals
- Financial Capacity vs. Risk Attitude 一致性檢核
- AI Dynamic Risk Profile 預留區

## 安裝

```bash
pip install streamlit pandas openai
```

## 執行

```bash
streamlit run app.py
```

`responses.json` 不需手動建立；第一位使用者完成問卷後會自動產生。

## 檔案

- `app.py`：Streamlit UI 與結果頁
- `questions.json`：題庫、選項、分數與分析因子
- `scoring.py`：評分、Behavioral Signals、一致性檢核
- `README.md`：操作說明

## 注意

目前的分數與 35% / 25% / 30% / 10% 權重是課程原型設計，不應視為經驗驗證或法規認可的正式適合度模型。正式金融用途前需要另外做模型驗證、治理及適用法規檢核。


## V3 資產架構

Financial Capacity 中的資產拆成三層：

- Total Assets：包含房地產、現金存款、投資及其他主要資產。
- Financial Assets：排除自住房地產，聚焦現金、存款、股票、ETF、基金、債券等金融資產。
- Investable Assets：真正可投入投資，而且短期內不需要動用的資金。

這樣可避免「總資產高」被直接解讀為「可承受高投資風險」。
