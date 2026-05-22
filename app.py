import streamlit as st
import yfinance as yf
import feedparser
import urllib.parse
import pandas as pd

# ページの設定（横幅を広くしてグラフを見やすくする）
st.set_page_config(layout="wide")

st.title("🇺🇸 米国株トレンドチェッカー PRO")
st.write("リアルタイム株価、円建て換算、最新ニュース、そして株価チャートをまとめてチェック！")

# 1. 企業のリスト
companies = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA"
}

selected_company = st.selectbox("調べる企業を選んでください：", list(companies.keys()))
ticker = companies[selected_company]

with st.spinner("最新データを読み込み中..."):
    # 為替データの取得
    forex = yf.Ticker("JPY=X")
    usd_jpy = forex.history(period="1d")['Close'].iloc[-1]

    # 株価データの取得（過去1ヶ月分）
    stock_data = yf.Ticker(ticker)
    hist = stock_data.history(period="1mo")

    if len(hist) >= 2:
        current_price_usd = hist['Close'].iloc[-1]
        prev_price_usd = hist['Close'].iloc[-2]
        
        pct_change = ((current_price_usd - prev_price_usd) / prev_price_usd) * 100
        current_price_jpy = current_price_usd * usd_jpy

        # 上部の数字表示
        col1, col2, col3 = st.columns(3)
        col1.metric(label="株価 (ドル)", value=f"${current_price_usd:.2f}")
        col2.metric(label="株価 (日本円)", value=f"約 {int(current_price_jpy):,} 円")
        col3.metric(label="前日比 (%)", value=f"{pct_change:.2f}%", delta=f"{pct_change:.2f}%")
        st.caption(f"現在の為替レート: 1ドル = {usd_jpy:.2f}円")

        # 📊 過去1ヶ月の株価の折れ線グラフ
        st.write("### 📊 過去1ヶ月の株価の動き")
        chart_data = pd.DataFrame(hist['Close'])
        st.line_chart(chart_data)

    else:
        st.error("株価データの取得に失敗しました。")

    # ニュースの表示
    st.write(f"### 📰 {selected_company} の関連ニュース")
    encoded_keyword = urllib.parse.quote(selected_company)
    url = f"https://google.com{encoded_keyword}"
    
    feed = feedparser.parse(url)
    
    if feed.entries:
        for entry in feed.entries[:3]:
            st.markdown(f"**[{entry.title}]({entry.link})**")
            st.write("-" * 20)
    else:
        st.write("現在、関連ニュースはありません。")
