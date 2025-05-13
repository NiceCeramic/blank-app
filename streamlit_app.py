import streamlit as st
import pandas as pd
import datetime
import altair as alt

st.title("🎯 레이저사격 점수 기록 시스템")

# 세션 상태 초기화
if 'score_data' not in st.session_state:
    st.session_state.score_data = pd.DataFrame(columns=["날짜", "학년", "반", "번호", "이름", "점수"])

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
            new_row = pd.DataFrame([[date, grade, class_name, number, name, score]],
                                   columns=["날짜", "학년", "반", "번호", "이름", "점수"])
            st.session_state.score_data = pd.concat([st.session_state.score_data, new_row], ignore_index=True)
            st.success(f"{grade} {class_name} {number}번 {name} 학생의 점수가 저장되었습니다!")

# --- 데이터 시각화 ---
if not st.session_state.score_data.empty:
    df = st.session_state.score_data.copy()
    df['날짜'] = pd.to_datetime(df['날짜'])

    st.header("📈 학생별 점수 변화 추이")
    selected_names = st.multiselect("학생 선택", df["이름"].unique(), default=list(df["이름"].unique()))

    if selected_names:
        filtered = df[df["이름"].isin(selected_names)]
        chart = alt.Chart(filtered).mark_line(point=True).encode(
            x="날짜:T",
            y="점수:Q",
            color="이름:N"
        ).properties(width=700, height=400)
        st.altair_chart(chart)

    st.header("🏆 반별 순위 (최신 날짜 기준)")
    latest_date = df["날짜"].max()
    latest_scores = df[df["날짜"] == latest_date]
    ranked = latest_scores.sort_values(by=["학년", "반", "점수"], ascending=[True, True, False])
    ranked['순위'] = ranked.groupby(["학년", "반"])['점수'].rank(ascending=False, method='min')
    st.subheader(f"📅 {latest_date.strftime('%Y-%m-%d')} 기준")
    st.dataframe(ranked[["학년", "반", "번호", "이름", "점수", "순위"]].sort_values(by=["학년", "반", "순위"]))

# --- 저장 기능 ---
st.markdown("---")
if st.button("💾 전체 데이터 다운로드"):
    st.download_button(
        label="CSV 파일로 저장",
        data=st.session_state.score_data.to_csv(index=False).encode('utf-8-sig'),
        file_name='laser_scores.csv',
        mime='text/csv'
    )

