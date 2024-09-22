# 이동평균선 추가
import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from datetime import date, timedelta


# Streamlit 앱 제목 설정
st.title("주식 차트 분석기")

# 종목 선택
stocks = {
    "애플": "AAPL",
    "마이크로소프트": "MSFT",
    "구글": "GOOGL",
    "아마존": "AMZN",
    "테슬라": "TSLA",
    "삼성전자": "005930.KS",
    "네이버": "035420.KS",
    "카카오": "035720.KS",
}

selected_stock = st.selectbox("종목을 선택하세요", list(stocks.keys()))

# 날짜 범위 선택
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "시작 날짜를 선택하세요", date.today() - timedelta(days=365)
    )
with col2:
    end_date = st.date_input("종료 날짜를 선택하세요", date.today())

# 이동평균선 토글 버튼
st.subheader("이동평균선 설정")
col1, col2, col3 = st.columns(3)
with col1:
    show_ma5 = st.checkbox("5일 이동평균선", value=True)
with col2:
    show_ma20 = st.checkbox("20일 이동평균선", value=True)
with col3:
    show_ma120 = st.checkbox("120일 이동평균선", value=True)


# 주식 데이터 가져오기
@st.cache_data
def get_stock_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    data["MA5"] = data["Close"].rolling(window=5).mean()
    data["MA20"] = data["Close"].rolling(window=20).mean()
    data["MA120"] = data["Close"].rolling(window=120).mean()
    return data


# 선택된 종목, 시작 날짜, 종료 날짜가 모두 유효할 때 데이터를 가져오고 차트를 업데이트합니다
if selected_stock and start_date and end_date:
    data = get_stock_data(stocks[selected_stock], start_date, end_date)

    if not data.empty:
        # 주식 차트 생성
        fig = go.Figure()

        # 캔들스틱 차트 추가
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name="주가",
            )
        )

        # 이동평균선 추가
        if show_ma5:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["MA5"],
                    name="5일 이동평균",
                    line=dict(color="blue"),
                )
            )
        if show_ma20:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["MA20"],
                    name="20일 이동평균",
                    line=dict(color="orange"),
                )
            )
        if show_ma120:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["MA120"],
                    name="120일 이동평균",
                    line=dict(color="red"),
                )
            )

        fig.update_layout(
            title=f"{selected_stock} 주식 차트",
            yaxis_title="주가",
            xaxis_title="날짜",
            xaxis_rangeslider_visible=False,
        )

        # Streamlit에 차트 표시
        st.plotly_chart(fig, use_container_width=True)
        
        

        # 주식 정보 표시
        st.subheader("주식 정보")
        st.write(data.tail())

        # 기본 통계 정보 추가
        st.subheader("기본 통계")
        stock_stats = data["Close"].describe()
        st.write(stock_stats)

        # 수익률 계산
        if len(data) > 1:
            total_return = (
                (data["Close"].iloc[-1] - data["Close"].iloc[0])
                / data["Close"].iloc[0]
                * 100
            )
            st.write(f"기간 수익률: {total_return:.2f}%")
    else:
        st.warning("선택한 날짜 범위에 데이터가 없습니다. 다른 날짜를 선택해 주세요.")
else:
    st.warning("종목, 시작 날짜, 종료 날짜를 모두 선택해 주세요.")
