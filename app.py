import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

from scoring import calculate_profile, SECTION_NAMES, BEHAVIOR_NAMES

BASE_DIR = Path(__file__).parent
QUESTION_FILE = BASE_DIR / "questions.json"
RESPONSE_FILE = BASE_DIR / "responses.json"

st.set_page_config(
    page_title="AI 投資人風險評估",
    page_icon="📊",
    layout="wide",
)

@st.cache_data
def load_questions():
    with open(QUESTION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_response(record):
    records = []
    if RESPONSE_FILE.exists():
        try:
            with open(RESPONSE_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
        except (json.JSONDecodeError, OSError):
            records = []

    records.append(record)
    with open(RESPONSE_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def total_questions(questionnaire):
    return sum(len(s["questions"]) for s in questionnaire["sections"])

questionnaire = load_questions()

st.title("AI 投資人風險評估")
st.caption("Investor Risk Assessment")
st.write(
    "透過財務條件、投資目標、行為／情緒與投資經驗，建立基礎風險輪廓。"
)
st.info("課程示範用途：目前只進行風險評估與分析，不提供投資商品推薦。")

with st.form("risk_form"):
    st.subheader("基本資料")
    c1, c2 = st.columns(2)
    with c1:
        customer_name = st.text_input("姓名或暱稱", placeholder="例如：王小明")
    with c2:
        customer_id = st.text_input("客戶編號", placeholder="例如：C001")

    answers = {}

    for section in questionnaire["sections"]:
        st.divider()
        st.header(f'{section["id"]}. {section["title"]}')
        st.caption(section["subtitle"])

        for q in section["questions"]:
            labels = [x["label"] for x in q["options"]]
            option_map = {x["label"]: x for x in q["options"]}

            selected = st.radio(
                q["text"],
                labels,
                index=None,
                key=q["id"],
            )

            if selected is not None:
                answers[q["id"]] = {
                    "answer": selected,
                    "score": option_map[selected]["score"],
                    "factor": q.get("factor"),
                }

    submitted = st.form_submit_button(
        "完成風險評估",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if len(answers) != total_questions(questionnaire):
        st.error("還有題目尚未完成，請回答所有題目後再送出。")
        st.stop()

    profile = calculate_profile(questionnaire, answers)

    record = {
        "customer_id": customer_id.strip() or f"C-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "name": customer_name.strip() or "未填寫",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "questionnaire_version": questionnaire.get("version", "2.0"),
        "answers": answers,
        **profile,
    }
    save_response(record)

    st.success("評估完成")

    st.header("Baseline Risk Profile｜基礎風險輪廓")
    m1, m2, m3 = st.columns(3)
    m1.metric("Overall Risk Score", f'{profile["overall_score"]:.1f} / 100')
    m2.metric("Risk Profile", profile["risk_level"])
    m3.metric(
        "Capacity vs. Attitude",
        f'{profile["capacity_attitude_gap"]:+.1f}',
        help="正數代表財務承受能力高於行為風險偏好；負數則相反。",
    )

    section_df = pd.DataFrame([
        {"構面": SECTION_NAMES[k], "分數": profile["section_scores"][k]}
        for k in ["A", "B", "C", "D"]
    ])

    left, right = st.columns([1.15, 1])

    with left:
        st.subheader("四大構面")
        fig_section = px.line_polar(
            section_df, 
            r='分數', 
            theta='構面', 
            line_close=True,
            range_r=[0, 100] 
        )
        fig_section.update_traces(fill='toself') 
        st.plotly_chart(fig_section, use_container_width=True)
       
        
        st.dataframe(section_df, use_container_width=True, hide_index=True)

    with right:
        st.subheader("Behavioral Signals｜行為／情緒指標")
        behavior_rows = []
        for key, value in profile["behavioral_signals"].items():
            behavior_rows.append({
                "指標": BEHAVIOR_NAMES.get(key, key),
                "分數": value,
            })

        behavior_df = pd.DataFrame(behavior_rows)
        if not behavior_df.empty:
            fig_behavior = px.line_polar(
                behavior_df, 
                r='分數', 
                theta='指標', 
                line_close=True,
                range_r=[0, 100] 
                )
            fig_behavior.update_traces(fill='toself')
            st.plotly_chart(fig_behavior, use_container_width=True)
            
            
            st.dataframe(behavior_df, use_container_width=True, hide_index=True)
            st.subheader("Consistency Check｜一致性檢核")
    if profile["flags"]:
        for flag in profile["flags"]:
            st.warning(flag)
    else:
        st.info("目前沒有發現需要特別標記的重大不一致。")

    st.subheader("Dynamic Risk Profile｜下一階段 AI")
    st.write(
        "目前版本已建立 Baseline Risk Score、Financial Capacity、"
        "Behavioral Signals 與一致性檢核。下一階段可由 AI 根據矛盾點"
        "產生動態追問，並以自然語言解釋風險輪廓。"
    )

    with st.expander("查看本次填答紀錄"):
        display_rows = []
        for section in questionnaire["sections"]:
            for q in section["questions"]:
                a = answers[q["id"]]
                display_rows.append({
                    "題號": q["id"],
                    "題目": q["text"],
                    "回答": a["answer"],
                    "分數": a["score"],
                    "分析因子": a["factor"],
                })
        st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)
