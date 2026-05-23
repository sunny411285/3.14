import streamlit as st
import yfinance as yf
import urllib.parse
import pandas as pd

# ページの設定（横幅を広くしてグラフを見やすくする）
st.set_page_config(layout="wide", page_title="米国株トレンドチェッカー PRO")

st.title("🇺🇸 米国株トレンドチェッカー PRO")
st.write("リアルタイム株価、円建て換算、最新ニュース、そして株価チャートをまとめてチェック！")

# 1. 企業のリスト
companies = {
    "🍎 Apple (AAPL)": "AAPL",
    "💻 Microsoft (MSFT)": "MSFT",
    "🤖 NVIDIA (NVDA)": "NVDA",
    "🚗 Tesla (TSLA)": "TSLA",
    "🔍 Google (GOOGL)": "GOOGL",
    "📦 Amazon (AMZN)": "AMZN",
    "📺 Netflix (NFLX)": "NFLX",
    "☕ Starbucks (SBUX)": "SBUX"
}

selected_company = st.selectbox("調べる企業を選んでください：", list(companies.keys()))
ticker = companies[selected_company]

with st.spinner("最新データを読み込み中..."):
    try:
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

            # 🟢 見栄えアップ：枠線付きのカード（Container）で数字を囲む
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)
                col1.metric(label="株価 (ドル)", value=f"${current_price_usd:.2f}")
                col2.metric(label="株価 (日本円)", value=f"約 {int(current_price_jpy):,} 円")
                col3.metric(label="前日比 (%)", value=f"{pct_change:.2f}%", delta=f"{pct_change:.2f}%")
                st.caption(f"現在の為替レート: 1ドル = {usd_jpy:.2f}円")

            # 📊 過去1ヶ月の株価の折れ線グラフ
            st.markdown(f"### 📊 {selected_company} 過去1ヶ月の株価の動き")
            chart_data = pd.DataFrame(hist['Close'])
            # 🟢 見栄えアップ：エリアチャートにしてグラデーションをつける
            st.area_chart(chart_data)

        else:
            st.error("株価データの取得に失敗しました。時間をおいて試してください。")
            
    except Exception as e:
        st.error("Yahoo Financeの通信エラーが発生しました。リロードするか時間を置いてください。")

    # 🟢 見栄えアップ：エラーが出ない安全なニュースリンクボタンに変更
    st.markdown(f"### 📰 {selected_company} の最新情報をチェック")
    with st.container(border=True):
        st.write("外部サイトで最新の関連ニュースや企業情報を確認できます。")
        encoded_keyword = urllib.parse.quote(f"{selected_company} ニュース")
        
        # GoogleニュースとYahooファイナンスへのリンクボタンを横並びに配置
        btn_col1, btn_col2, _ = st.columns([1, 1, 2])
        with btn_col1:
            st.link_button("🌐 Googleニュースで見る", f"https://google.com{encoded_keyword}&hl=ja&gl=JP&ceid=JP:ja")
        with btn_col2:
            st.link_button("📈 Yahoo!ファイナンスで見る", f"https://yahoo.co.jp")

