import streamlit as st
import pandas as pd
import datetime
import altair as alt

st.set_page_config(page_title="레이저 사격 기록", layout="wide")

st.title("🎯 레이저사격 점수 기록 시스템")

# 세션 상태 초기화
if 'score_data' not in st.session_state:
    st.session_state.score_data = pd.DataFrame(columns=[
        "날짜", "학년", "반", "번호", "이름", "점수", "입력시간"
    ])

# --- 점수 입력 폼 ---
st.header("📌 점수 입력")

with st.form("score_form"):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("이름")
        grade = st.selectbox("학년", ["1학년", "2학년", "3학년", "4학년", "5학년", "6학년"])
        class_name = st.selectbox("반", ["1반", "2반", "3반"])
    
    with col2:
        number = st.text_input("번호")
        date = st.date_input("날짜", datetime.date.today())
        score = st.number_input("점수", min_value=0, max_value=100, step=1)

    submitted = st.form_submit_button("점수 저장")
    if submitted:
        if not name or not number:
            st.warning("이름과 번호는 반드시 입력해주세요.")
        else:
            new_row = pd.DataFrame([[date, grade, class_name, number, name, score, datetime.datetime.now()]],
                                   columns=["날짜", "학년", "반", "번호", "이름", "점수", "입력시간"])
            st.session_state.score_data = pd.concat(
                [st.session_state.score_data, new_row], ignore_index=True)
            st.success(f"{grade} {class_name} {number}번 {name} 학생의 점수가 저장되었습니다!")

# --- 데이터 준비 ---
df = st.session_state.score_data.copy()
df['날짜'] = pd.to_datetime(df['날짜'])
df['입력시간'] = pd.to_datetime(df['입력시간'])

if not df.empty:
    st.header("📈 학생별 점수 변화 추이 (평균 점수 기준)")

    selected_name = st.selectbox("📌 조회할 학생 선택", df["이름"].unique())
    student_df = df[df["이름"] == selected_name]

    if not student_df.empty:
        grouped = student_df.groupby("날짜")["점수"].agg(['mean', 'count']).reset_index()
        grouped.columns = ["날짜", "평균점수", "도전횟수"]

        st.subheader(f"🧍 {selected_name} 학생 점수 추이")
        chart = alt.Chart(grouped).mark_line(point=True).encode(
            x="날짜:T",
            y="평균점수:Q",
            tooltip=["날짜:T", "평균점수:Q", "도전횟수:Q"]
        ).properties(width=700, height=400)

        st.altair_chart(chart)
        st.dataframe(grouped)

    st.header("🏆 반별 순위 (최신 날짜 기준, 최고 점수 기준)")
    latest_date = df["날짜"].max()
    latest_scores = df[df["날짜"] == latest_date]
    best_scores = latest_scores.groupby(["학년", "반", "번호", "이름"])["점수"].max().reset_index()

    best_scores['순위'] = best_scores.groupby(["학년", "반"])['점수']\
        .rank(ascending=False, method='min')
    st.subheader(f"📅 {latest_date.strftime('%Y-%m-%d')} 기준")
    st.dataframe(best_scores.sort_values(by=["학년", "반", "순위"]))

    st.markdown("---")
    st.subheader("📊 전체 기록 확인")
    st.dataframe(df.sort_values(by="입력시간", ascending=False))

    # CSV 저장 기능
    st.download_button(
        label="💾 CSV 파일 다운로드",
        data=df.to_csv(index=False).encode('utf-8-sig'),
        file_name="laser_scores.csv",
        mime='text/csv'
    )
else:
    st.info("아직 저장된 데이터가 없습니다.")
