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
    "📱 Meta (META)": "META",
    "🍿 Netflix (NFLX)": "NFLX",
    "☕ Starbucks (SBUX)": "SBUX" ,
    "🥤 Coca-Cola (KO)": "KO",
    "🍟 McDonald's (MCD)": "MCD",
    "💳 Visa (V)": "V"
}

selected_company = st.selectbox("調べる企業を選んでください：", list(companies.keys()))
ticker = companies[selected_company]

# 📊 株価チャートの設定
st.write("### 📊 株価チャートの設定")
period_labels = {
    "1ヶ月": "1mo",
    "6ヶ月": "6mo",
    "1年": "1y",
    "5年": "5y"
}
selected_period_label = st.radio("表示期間を変更できます：", list(period_labels.keys()), horizontal=True)
selected_period = period_labels[selected_period_label]

with st.spinner("最新データを読み込み中..."):
    try:
        # 為替データの取得
        forex = yf.Ticker("JPY=X")
        usd_jpy = forex.history(period="1d")['Close'].iloc[-1]

        # 株価データの取得（選択された期間で取得）
        stock_data = yf.Ticker(ticker)
        hist = stock_data.history(period=selected_period)

        if len(hist) >= 2:
            current_price_usd = hist['Close'].iloc[-1]
            prev_price_usd = hist['Close'].iloc[-2]
            
            pct_change = ((current_price_usd - prev_price_usd) / prev_price_usd) * 100
            current_price_jpy = current_price_usd * usd_jpy

            # 見栄えアップ：枠線付きのカード（Container）で数字を囲む
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)
                col1.metric(label="株価 (ドル)", value=f"${current_price_usd:.2f}")
                col2.metric(label="株価 (日本円)", value=f"約 {int(current_price_jpy):,} 円")
                col3.metric(label="前日比 (%)", value=f"{pct_change:.2f}%", delta=f"{pct_change:.2f}%")
                st.caption(f"現在の為替レート: 1ドル = {usd_jpy:.2f}円")

            # 過去の株価の折れ線グラフ
            st.markdown(f"### 📈 {selected_company} 過去{selected_period_label}の株価の動き")
            chart_data = pd.DataFrame(hist['Close'])
            st.area_chart(chart_data)

        else:
            st.error("株価データの取得に失敗しました。時間をおいて試してください。")
            
    except Exception as e:
        st.error("Yahoo Financeの通信エラーが発生しました。リロードするか時間を置いてください。")

    # ニュースリンクボタン
    st.markdown(f"### 📰 {selected_company} の最新情報をチェック")
    with st.container(border=True):
        st.write("外部サイトで最新の関連ニュースや企業情報を確認できます。")
        encoded_keyword = urllib.parse.quote(f"{selected_company} ニュース")
        
        # ★修正箇所：st.columns() の中に「3」を入れて列数を正しく指定しました
        btn_col1, btn_col2, _ = st.columns(3)
        with btn_col1:
            st.link_button("🌐 Googleニュースで見る", f"https://google.com{encoded_keyword}&hl=ja&gl=JP&ceid=JP:ja")
        with btn_col2:
            st.link_button("📈 Yahoo!ファイナンスで見る", f"https://yahoo.co.jp")

