import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="영화 데이터 그래프 도감 2", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "1년간 박스오피스 10위권에 든 영화 가운데, 이 기간에 개봉한 216편의 데이터를 "
    "이용해 여러 가지 분포와 관계를 살펴봅니다."
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 장르: '|' 기호로 여러 개 적힌 경우 첫 번째 장르만 사용
    df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    # 개봉일(여덟 자리 숫자) -> 날짜형
    df["openDt"] = pd.to_datetime(df["openDt"].astype(str), format="%Y%m%d", errors="coerce")

    return df


df = load_data()

with st.expander("원본 데이터 미리 보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# -----------------------------------------------------------------------------
# 1. 장르별 영화 편수 - 도넛 그래프
# -----------------------------------------------------------------------------
st.header("1. 장르별 영화 편수")

genre_count = df["genre"].value_counts().reset_index()
genre_count.columns = ["genre", "count"]

fig1 = px.pie(
    genre_count,
    names="genre",
    values="count",
    hole=0.5,
)
fig1.update_traces(
    textinfo="label+percent",
    hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig1.update_layout(legend_title_text="장르")

st.plotly_chart(fig1, use_container_width=True)

st.text_area(
    "이 그래프로 알 수 있는 것",
    placeholder="예: 가장 많은 영화가 제작된 장르는 ○○이고, 전체의 약 ○○%를 차지한다.",
    key="insight_1",
)

st.divider()

# -----------------------------------------------------------------------------
# 2. 장르 안 영화 - 트리맵 (칸 크기: 총 관객수)
# -----------------------------------------------------------------------------
st.header("2. 장르 안에 담긴 영화들 - 트리맵")

fig_tree = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
)
fig_tree.update_traces(
    hovertemplate="영화명: %{label}<br>총 관객: %{value:,}명<extra></extra>",
    root_color="lightgrey",
)

st.plotly_chart(fig_tree, use_container_width=True)

st.text_area(
    "이 그래프로 알 수 있는 것",
    placeholder="예: ○○ 장르 안에서는 <영화명>이 총 관객수 기준으로 가장 큰 비중을 차지한다.",
    key="insight_tree",
)

st.divider()

# -----------------------------------------------------------------------------
# 3. 총 관객수 분포 - 히스토그램
# -----------------------------------------------------------------------------
st.header("3. 총 관객수 분포")

fig2 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    labels={"total_audi": "총 관객수(명)"},
)
fig2.update_traces(
    hovertemplate="관객수 구간: %{x}<br>영화 편수: %{y}<extra></extra>"
)
fig2.update_layout(yaxis_title="영화 편수")

st.plotly_chart(fig2, use_container_width=True)

# 가장 영화가 많이 몰린 구간 계산
audi_bin = pd.cut(df["total_audi"], bins=30, include_lowest=True)
top_bin = audi_bin.value_counts().idxmax()
top_bin_count = audi_bin.value_counts().max()

# 총 관객수가 가장 많은 영화
top_movie_row = df.loc[df["total_audi"].idxmax()]

st.markdown(
    f"- 영화가 가장 많이 몰린 총 관객수 구간은 **{int(top_bin.left):,}명 ~ {int(top_bin.right):,}명**"
    f"이며, 이 구간에 **{top_bin_count}편**이 속해 있습니다.\n"
    f"- 총 관객수가 가장 많은 영화는 **{top_movie_row['movieNm']}**"
    f"(총 관객 {int(top_movie_row['total_audi']):,}명)입니다."
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    placeholder="예: 대부분의 영화는 총 관객수가 ○○명 이하에 몰려 있고, 일부만 큰 흥행을 한다.",
    key="insight_2",
)

st.divider()

# -----------------------------------------------------------------------------
# 4. 개봉 스크린수와 총 관객수의 관계 - 산점도
# -----------------------------------------------------------------------------
st.header("4. 개봉 스크린수와 총 관객수의 관계")

fig3 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객수(명)", "genre": "장르"},
)

st.plotly_chart(fig3, use_container_width=True)

st.text_area(
    "이 그래프로 알 수 있는 것",
    placeholder="예: 개봉일 스크린수가 많을수록 대체로 총 관객수도 늘어나는 경향이 있다.",
    key="insight_3",
)

st.divider()

# -----------------------------------------------------------------------------
# 5. 장르별 총 관객수 분포 - 박스플롯 (영화 10편 이상인 장르만)
# -----------------------------------------------------------------------------
st.header("5. 장르별 총 관객수 분포 (영화 10편 이상 장르만)")

genre_movie_count = df["genre"].value_counts()
major_genres = genre_movie_count[genre_movie_count >= 10].index
df_major_genre = df[df["genre"].isin(major_genres)]

fig5 = px.box(
    df_major_genre,
    x="genre",
    y="total_audi",
    points="outliers",
    hover_data={"movieNm": True, "genre": False, "total_audi": ":,"},
    labels={"genre": "장르", "total_audi": "총 관객수(명)"},
)

st.plotly_chart(fig5, use_container_width=True)

st.text_area(
    "이 그래프로 알 수 있는 것",
    placeholder="예: ○○ 장르는 관객수의 중앙값이 높고 편차도 큰 편이다.",
    key="insight_5",
)

st.divider()

# -----------------------------------------------------------------------------
# 6. 개봉일 스크린수 vs 총 관객수 - 버블 그래프 (점 크기: 첫 주 관객)
# -----------------------------------------------------------------------------
st.header("6. 개봉 스크린수 · 총 관객수 · 첫 주 관객수 - 버블 그래프")

fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=40,
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수(명)",
        "first_week_audi": "첫 주 관객수",
        "genre": "장르",
    },
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.text_area(
    "이 그래프로 알 수 있는 것",
    placeholder="예: 첫 주 관객이 많았던 영화(큰 점)는 대체로 총 관객수도 많다.",
    key="insight_bubble",
)

st.divider()

# -----------------------------------------------------------------------------
# 7. 제작 국가별 영화 편수
# -----------------------------------------------------------------------------
st.header("7. 제작 국가별 영화 편수")

nation_count = df["nation"].value_counts().reset_index()
nation_count.columns = ["nation", "count"]

fig4 = px.bar(
    nation_count,
    x="nation",
    y="count",
    labels={"nation": "제작 국가", "count": "영화 편수"},
)
fig4.update_traces(hovertemplate="국가: %{x}<br>편수: %{y}편<extra></extra>")

st.plotly_chart(fig4, use_container_width=True)

st.text_area(
    "이 그래프로 알 수 있는 것",
    placeholder="예: ○○ 영화가 전체의 대부분을 차지하며, 그 다음으로 ○○이 많다.",
    key="insight_4",
)

st.divider()

# -----------------------------------------------------------------------------
# 8. 10위권 유지 일수 분포
# -----------------------------------------------------------------------------
st.header("8. 박스오피스 10위권 유지 일수 분포")

fig6 = px.histogram(
    df,
    x="days_in_top10",
    nbins=20,
    labels={"days_in_top10": "10위권 유지 일수"},
)
fig6.update_layout(yaxis_title="영화 편수")
fig6.update_traces(
    hovertemplate="유지 일수 구간: %{x}<br>영화 편수: %{y}<extra></extra>"
)

st.plotly_chart(fig6, use_container_width=True)

st.text_area(
    "이 그래프로 알 수 있는 것",
    placeholder="예: 대부분의 영화는 10위권에 ○○일 이하로 머무르고, 장기 흥행작은 드물다.",
    key="insight_6",
)
