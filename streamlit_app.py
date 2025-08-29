#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)


#######################
# Load data
df_reshaped = pd.read_csv('aa.csv') ## 분석 데이터 넣기


#######################
# Sidebar
#######################
# Sidebar
with st.sidebar:
    st.title("충남 교육기관 대시보드")
    st.caption("필터를 선택해 보세요")

    # 테마 선택
    theme = st.selectbox(
        "색상 테마 선택",
        options=["blues", "greens", "purples", "reds", "oranges", "viridis", "plasma"],
        index=0,
        help="차트 컬러맵을 고릅니다."
    )

    # 연도 컬럼 있을 때만 노출 (데이터에 연도 없는 경우 자동 숨김)
    year_col = None
    for cand in ["연도", "년도", "year", "YEAR"]:
        if cand in df_reshaped.columns:
            year_col = cand
            break
    if year_col:
        years = sorted(df_reshaped[year_col].dropna().unique().tolist())
        sel_year = st.selectbox("연도 선택", options=years, index=len(years)-1)
    else:
        sel_year = None

    # 기본 필터: 학교급 / 설립별 / 시군 / 읍면동 / 학교명 검색
    def _opts(col):
        return sorted([x for x in df_reshaped[col].dropna().unique().tolist()])

    col_map = {
        "학교급": "학교급",
        "설립별": "설립별",
        "시군명": "시군명",
        "읍면동": "읍면동",
    }
    sel_grade = st.multiselect("학교급 선택", options=_opts(col_map["학교급"]), default=_opts(col_map["학교급"]))
    sel_found = st.multiselect("설립별 선택", options=_opts(col_map["설립별"]), default=_opts(col_map["설립별"]))
    sel_city  = st.multiselect("시군 선택",  options=_opts(col_map["시군명"]), default=_opts(col_map["시군명"]))
    sel_town  = st.multiselect("읍면동 선택", options=_opts(col_map["읍면동"]), default=[])

    # 신설/휴원 상태(있으면)
    status_col = "신설휴원" if "신설휴원" in df_reshaped.columns else None
    if status_col:
        status_opts = ["신설", "휴원"]
        sel_status = st.multiselect("신설/휴원 상태", options=status_opts, default=[])
    else:
        sel_status = []

    # 학교명 검색
    q_school = st.text_input("학교명 검색", value="", placeholder="예) 천안, 중앙, 유치원 등")

    # 필터 적용
    df_filtered = df_reshaped.copy()
    if sel_year is not None:
        df_filtered = df_filtered[df_filtered[year_col] == sel_year]
    if sel_grade:
        df_filtered = df_filtered[df_filtered[col_map["학교급"]].isin(sel_grade)]
    if sel_found:
        df_filtered = df_filtered[df_filtered[col_map["설립별"]].isin(sel_found)]
    if sel_city:
        df_filtered = df_filtered[df_filtered[col_map["시군명"]].isin(sel_city)]
    if sel_town:
        df_filtered = df_filtered[df_filtered[col_map["읍면동"]].isin(sel_town)]
    if status_col and sel_status:
        df_filtered = df_filtered[df_filtered[status_col].fillna("").isin(sel_status)]
    if q_school:
        df_filtered = df_filtered[df_filtered["학교명"].str.contains(q_school, na=False)]

    # 세션 스토어: 이후 컬럼1~3에서 사용
    st.session_state["theme"] = theme
    st.session_state["sel_year"] = sel_year
    st.session_state["filters"] = {
        "학교급": sel_grade, "설립별": sel_found, "시군명": sel_city, "읍면동": sel_town,
        "신설휴원": sel_status, "학교명_query": q_school
    }
    st.session_state["df_filtered"] = df_filtered

    # 요약 표시
    with st.expander("현재 선택 요약", expanded=False):
        st.write(f"표시 행 수: **{len(df_filtered):,}**")
        st.write(st.session_state["filters"])

    # 초기화 버튼
    if st.button("필터 초기화"):
        st.experimental_rerun()



#######################
# Plots



#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

# with col[0]:


# with col[1]:



# with col[2]: