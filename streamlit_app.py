import streamlit as st
import pandas as pd
import datetime
import altair as alt

st.set_page_config(page_title="레이저 사격 점수 기록", layout="wide")
st.title("🎯 레이저사격 점수 기록 시스템")

# 초기화
if 'score_data' not in st.session_state:
    st.session_state.score_data = pd.DataFrame(columns=[
        "날짜", "학년", "반", "번호", "이름",
        "1발", "2발", "3발", "4발", "5발", "평균점수", "입력시간"
    ])

# --- 점수 입력 폼 ---
st.header("📌 회기별 5발 점수 입력")

with st.form("session_form"):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("이름")
        grade = st.selectbox("학년", ["1학년", "2학년", "3학년", "4학년", "5학년", "6학년"])
        class_name = st.selectbox("반", ["1반", "2반", "3반"])

    with col2:
        number = st.text_input("번호")
        date = st.date_input("날짜", datetime.date.today())

    st.markdown("**💡 한 회기당 5발을 쏩니다. 소수점 단위로 입력하세요.**")
    shot_cols = st.columns(5)
    shots = []
    for i in range(5):
        with shot_cols[i]:
            shot = st.number_input(f"{i+1}발", min_value=0.0, max_value=10.0, step=0.1, key=f"shot_{i}")
            shots.append(shot)

    submitted = st.form_submit_button("점수 저장")
    if submitted:
        if not name or not number:
            st.warning("이름과 번호는 반드시 입력해주세요.")
        else:
            avg = round(sum(shots) / 5, 2)
            new_row = pd.DataFrame([[date, grade, class_name, number, name,
                                     *shots, avg, datetime.datetime.now()]],
                                   columns=st.session_state.score_data.columns)
            st.session_state.score_data = pd.concat([st.session_state.score_data, new_row], ignore_index=True)
            st.success(f"{grade} {class_name} {number}번 {name} 학생의 점수가 저장되었습니다!")

# --- 기록 확인 및 수정 ---
if not st.session_state.score_data.empty:
    df = st.session_state.score_data.copy()
    df['날짜'] = pd.to_datetime(df['날짜'])
    df['입력시간'] = pd.to_datetime(df['입력시간'])

    st.header("📋 입력 기록 및 수정")

    edit_df = df.sort_values(by="입력시간", ascending=False).reset_index(drop=True)
    edit_index = st.selectbox("✏️ 수정할 기록 선택 (최근 순)", options=edit_df.index,
                              format_func=lambda i: f"{edit_df.loc[i, '이름']} ({edit_df.loc[i, '날짜'].date()})")

    with st.expander("기록 수정"):
        selected = edit_df.loc[edit_index]
        new_shots = []
        st.write(f"이름: {selected['이름']}, 날짜: {selected['날짜'].date()}, 평균점수: {selected['평균점수']}")
        shot_cols = st.columns(5)
        for i in range(5):
            with shot_cols[i]:
                shot_val = st.number_input(f"{i+1}발 (수정)", min_value=0.0, max_value=10.0, step=0.1,
                                           value=selected[f"{i+1}발"], key=f"edit_{i}")
                new_shots.append(shot_val)
        if st.button("✅ 수정 저장"):
            avg = round(sum(new_shots) / 5, 2)
            for i in range(5):
                st.session_state.score_data.loc[
                    (st.session_state.score_data['입력시간'] == selected['입력시간']),
                    f"{i+1}발"
                ] = new_shots[i]
            st.session_state.score_data.loc[
                (st.session_state.score_data['입력시간'] == selected['입력시간']),
                "평균점수"
            ] = avg
            st.success("기록이 성공적으로 수정되었습니다.")

    st.markdown("---")
    st.subheader("📈 학생별 평균 점수 추이")
    selected_name = st.selectbox("학생 선택", df["이름"].unique())
    student_df = df[df["이름"] == selected_name]
    avg_by_day = student_df.groupby("날짜")["평균점수"].mean().reset_index()

    chart = alt.Chart(avg_by_day).mark_line(point=True).encode(
        x="날짜:T", y="평균점수:Q", tooltip=["날짜:T", "평균점수"]
    ).properties(width=700, height=400)

    st.altair_chart(chart)
    st.dataframe(avg_by_day)

    st.header("🏆 반별 순위 (최신 날짜 기준, 평균 최고점)")
    latest = df["날짜"].max()
    latest_scores = df[df["날짜"] == latest]
    best_avg = latest_scores.groupby(["학년", "반", "번호", "이름"])["평균점수"].max().reset_index()
    best_avg["순위"] = best_avg.groupby(["학년", "반"])["평균점수"].rank(ascending=False, method="min")
    st.subheader(f"📅 {latest.strftime('%Y-%m-%d')} 기준")
    st.dataframe(best_avg.sort_values(by=["학년", "반", "순위"]))

    st.download_button(
        label="💾 전체 기록 CSV 다운로드",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="레이저사격_기록.csv",
        mime="text/csv"
    )

else:
    st.info("아직 입력된 점수가 없습니다.")

