#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="충남 교육기관 현황 대시보드",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# 1. Background Image (인터넷 이미지 URL 사용)
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://www.alamy.com/stock-photo/primary-school-elementary-school.html?blackwhite=1"); /* 위 이미지 대표 URL (Alamy) */
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 전반적인 텍스트 색상을 진한 회색 또는 검정으로 설정 */
    .stApp, .stApp * {
        color: #000000 !important;
    }

    /* 메트릭 카드 스타일 (반투명 흰 배경 + 그림자) */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.85);
        color: #000 !important;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 1px 1px 6px rgba(0,0,0,0.2);
    }

    /* 사이드바 배경 처리 (밝은 반투명) */
    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.9) !important;
    }

    /* 데이터프레임 배경 스타일 */
    [data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.9);
        color: #000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


#######################
# Load data
df_reshaped = pd.read_csv("aa.csv", encoding="cp949")

#######################
# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ 분석 설정")
    color_theme = st.selectbox(
        "색상 테마 선택",
        ["blues", "greens", "reds", "purples", "viridis", "plasma", "cividis"],
        index=0,
        help="지도/차트에 적용할 팔레트"
    )

    st.markdown("### 🔎 필터")
    df = df_reshaped.copy()

    # 숫자형 변환
    for _col in ["학생수", "학급수"]:
        if _col in df.columns:
            df[_col] = pd.to_numeric(df[_col], errors="coerce")

    # 학교급 필터
    levels = sorted(df["학교급"].dropna().unique().tolist())
    sel_levels = st.multiselect("학교급", options=levels, default=levels)

    # 설립별 필터
    founders = sorted(df["설립별"].dropna().unique().tolist())
    sel_founders = st.multiselect("설립별", options=founders, default=founders)

    # 시군 필터
    siguns_all = sorted(df["시군명"].dropna().unique().tolist())
    sel_siguns = st.multiselect("시군(복수 선택 가능)", options=siguns_all, default=siguns_all)

    # 읍면동 필터
    eupmyeon_pool = []
    if sel_siguns:
        eupmyeon_pool = df[df["시군명"].isin(sel_siguns)]["읍면동"].dropna().unique().tolist()
    else:
        eupmyeon_pool = df["읍면동"].dropna().unique().tolist()
    sel_eupmyeon = st.multiselect("읍면동", options=sorted(eupmyeon_pool), default=[])

    # 학교명 검색
    search_name = st.text_input("학교명 검색", placeholder="예) 천안, 중앙, ○○초 등")

    # 학생수 범위
    s_min, s_max = int(df["학생수"].min()), int(df["학생수"].max())
    sel_student_range = st.slider("학생수 범위", min_value=s_min, max_value=s_max,
                                  value=(s_min, s_max), step=1)

    # 학급수 범위
    c_min, c_max = int(df["학급수"].min()), int(df["학급수"].max())
    sel_class_range = st.slider("학급수 범위", min_value=c_min, max_value=c_max,
                                value=(c_min, c_max), step=1)

    # 신설휴원 상태
    status_opts = ["전체"] + sorted(df["신설휴원"].dropna().unique().tolist())
    sel_status = st.selectbox("신설·휴원 상태", options=status_opts, index=0)

    # 필터 적용
    df_filtered = df.copy()
    if sel_levels:
        df_filtered = df_filtered[df_filtered["학교급"].isin(sel_levels)]
    if sel_founders:
        df_filtered = df_filtered[df_filtered["설립별"].isin(sel_founders)]
    if sel_siguns:
        df_filtered = df_filtered[df_filtered["시군명"].isin(sel_siguns)]
    if sel_eupmyeon:
        df_filtered = df_filtered[df_filtered["읍면동"].isin(sel_eupmyeon)]
    if search_name:
        df_filtered = df_filtered[df_filtered["학교명"].str.contains(search_name, case=False, na=False)]
    lo, hi = sel_student_range
    df_filtered = df_filtered[df_filtered["학생수"].between(lo, hi, inclusive="both")]
    lo, hi = sel_class_range
    df_filtered = df_filtered[df_filtered["학급수"].between(lo, hi, inclusive="both")]
    if sel_status != "전체":
        df_filtered = df_filtered[df_filtered["신설휴원"] == sel_status]

    st.markdown("---")
    st.caption(f"선택된 조건에 해당하는 기관 수: **{len(df_filtered):,}개**")
    with st.expander("데이터 미리보기", expanded=False):
        st.dataframe(df_filtered.head(20), use_container_width=True)

#######################
# Plots

df_plot = df_filtered.copy()

# KPI
total_students = int(df_plot["학생수"].sum())
total_classes  = int(df_plot["학급수"].sum())
avg_stu_per_class = round(total_students / total_classes, 1) if total_classes else 0
num_schools    = len(df_plot)
num_new   = int(df_plot["신설휴원"].fillna("").str.contains("신설").sum())
num_closed = int(df_plot["신설휴원"].fillna("").str.contains("휴원").sum())

kpi = {
    "기관 수": num_schools,
    "총 학생 수": total_students,
    "총 학급 수": total_classes,
    "평균 학생/학급": avg_stu_per_class,
    "신설 수": num_new,
    "휴원 수": num_closed,
}

# Plot 색상
plotly_seq_name = color_theme.capitalize()
altair_scheme = color_theme
try:
    plotly_seq = getattr(px.colors.sequential, plotly_seq_name)
except AttributeError:
    plotly_seq = px.colors.sequential.Blues

# 설립별 학생수 비중
founder_share = (
    df_plot.assign(설립별=df_plot["설립별"].fillna("미상"))
           .groupby("설립별", as_index=False)["학생수"].sum()
)
chart_founder_pie = px.pie(
    founder_share, names="설립별", values="학생수", hole=0.55,
    color_discrete_sequence=plotly_seq, title="설립별 학생수 비중"
)

# 신설휴원 현황
status_cnt = (
    df_plot.assign(신설휴원=df_plot["신설휴원"].fillna("해당없음"))
           .groupby("신설휴원", as_index=False)["학교명"].count()
           .rename(columns={"학교명": "기관수"})
)
chart_status_donut = px.pie(
    status_cnt, names="신설휴원", values="기관수", hole=0.6,
    color_discrete_sequence=plotly_seq, title="신설·휴원 현황"
)

# 시군별 학생수
region_agg = (
    df_plot.groupby("시군명", as_index=False)
           .agg(학생수=("학생수", "sum"), 학급수=("학급수", "sum"))
           .sort_values("학생수", ascending=False)
)
chart_region_bar = px.bar(
    region_agg.head(15),
    x="학생수", y="시군명", orientation="h",
    color="학생수", color_continuous_scale=plotly_seq_name,
    title="시군별 학생수 (상위 15)"
)

# 히트맵
heat = (
    df_plot.pivot_table(index="시군명", columns="학교급",
                        values="학생수", aggfunc="sum", fill_value=0)
          .reset_index()
)
heat_melt = heat.melt(id_vars="시군명", var_name="학교급", value_name="학생수")
chart_heatmap = (
    alt.Chart(heat_melt)
       .mark_rect()
       .encode(
           x=alt.X("학교급:N", title="학교급"),
           y=alt.Y("시군명:N", title="시군"),
           color=alt.Color("학생수:Q", title="학생수", scale=alt.Scale(scheme=altair_scheme)),
           tooltip=["시군명:N", "학교급:N", alt.Tooltip("학생수:Q", format=",")]
       )
       .properties(title="시군 × 학교급 학생수 히트맵", height=450)
)

# Top 학교
top_students = df_plot.sort_values("학생수", ascending=False).head(10)[["학교명", "학생수", "학교급", "시군명"]]
chart_top_schools_students = px.bar(
    top_students.sort_values("학생수", ascending=True),
    x="학생수", y="학교명", orientation="h",
    color="학생수", color_continuous_scale=plotly_seq_name,
    title="학생수 상위 10개 학교", hover_data=["학교급", "시군명"]
)
top_classes = df_plot.sort_values("학급수", ascending=False).head(10)[["학교명", "학급수", "학교급", "시군명"]]
chart_top_schools_classes = px.bar(
    top_classes.sort_values("학급수", ascending=True),
    x="학급수", y="학교명", orientation="h",
    color="학급수", color_continuous_scale=plotly_seq_name,
    title="학급수 상위 10개 학교", hover_data=["학교급", "시군명"]
)

#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown("### 📌 주요 지표 요약")
    st.metric(label="총 학생 수", value=f"{kpi['총 학생 수']:,} 명")
    st.metric(label="총 학급 수", value=f"{kpi['총 학급 수']:,} 학급")
    st.metric(label="평균 학생 / 학급", value=f"{kpi['평균 학생/학급']}")
    st.metric(label="기관 수", value=f"{kpi['기관 수']:,} 개")
    st.metric(label="신설 기관", value=f"{kpi['신설 수']} 개")
    st.metric(label="휴원 기관", value=f"{kpi['휴원 수']} 개")
    st.markdown("---")
    st.plotly_chart(chart_founder_pie, use_container_width=True)
    st.plotly_chart(chart_status_donut, use_container_width=True)

with col[1]:
    st.markdown("### 🗺️ 지역별 학생 분포")
    st.plotly_chart(chart_region_bar, use_container_width=True)
    st.markdown("---")
    st.markdown("### 🔥 시군 × 학교급 히트맵")
    st.altair_chart(chart_heatmap, use_container_width=True)

with col[2]:
    st.markdown("### 🏫 Top 학교 랭킹")
    st.plotly_chart(chart_top_schools_students, use_container_width=True)
    st.plotly_chart(chart_top_schools_classes, use_container_width=True)
    st.markdown("---")
    st.markdown("### 📋 상세 데이터")
    st.dataframe(
        df_filtered[["학교명", "학교급", "설립별", "시군명", "읍면동", "학급수", "학생수"]],
        use_container_width=True,
        height=400
    )
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption("""
    - 데이터 출처: 충청남도 교육청 공개 자료  
    - 본 대시보드는 학교급·지역별 학생 분포와 주요 기관 현황을 시각화하여
      교육 정책 및 학교 현황 분석에 도움을 주기 위해 제작되었습니다.
    """)
