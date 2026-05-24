import streamlit as st
import yfinance as yf
import urllib.parse
import pandas as pd
from datetime import datetime
import pytz

# ページの設定（横幅を広くしてグラフを見やすくする）
st.set_page_config(layout="wide", page_title="米国株トレンドチェッカー PRO")

st.title("🇺🇸 米国株トレンドチェッカー PRO")
st.write("リアルタイム株価、円建て換算、最新ニュース、そして株価チャートをまとめてチェック！")

# 🟢 アフィリエイト広告エリア（文言をさらに魅力的に最適化）
st.markdown("### 🎁 投資を始めるなら！おすすめの証券会社")
with st.container(border=True):
    col_adv1, col_adv2 = st.columns([2, 1])  # 💡 比率を調整してボタンを押しやすく
    with col_adv1:
        st.write("**「自分も米国株を買ってみたい！」と思ったら**")
        st.caption("このアプリで紹介しているAppleやNVIDIAの株は、日本のネット証券から数千円で簡単に購入できます。今なら口座開設キャンペーン実施中！")
    with col_adv2:
        # ⚠️ A8.netで取得した「メール用URL」をここに貼り付けます
        my_affiliate_url = "https://a8.net..." 
        st.link_button("🔥 無料で口座開設する (SBI証券)", my_affiliate_url, use_container_width=True, type="primary")

st.write("---")

# 🟢 見る人へ：今が営業時間外（土日など）か自動判定して説明を出す
jst = pytz.timezone('Asia/Tokyo')
now_jst = datetime.now(jst)
weekday = now_jst.weekday()  # 0=月, 5=土, 6=日
hour = now_jst.hour

is_market_closed = False
if weekday == 5 or weekday == 6:
    is_market_closed = True
elif weekday == 0 and hour < 22:
    is_market_closed = True
elif hour >= 6 and hour < 22:
    is_market_closed = True

if is_market_closed:
    st.info("💡 **【アプリを見に来てくれた方へ】** 現在、アメリカの株式市場は**営業時間外（または定休日）**です。そのため最新の動きやグラフが一部更新されない場合があります。平日の夜（日本時間 23:30〜翌6:00 ※夏時間は22:30〜）にアクセスすると、リアルタイムにグングン動くチャートをご覧いただけます！")

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
        forex_hist = forex.history(period="5d")
        
        if not forex_hist.empty:
            valid_forex = forex_hist['Close'].dropna()
            usd_jpy = valid_forex.iloc[-1]
        else:
            usd_jpy = 150.0

        # 株価データの取得
        stock_data = yf.Ticker(ticker)
        hist = stock_data.history(period=selected_period)

        if hist is not None and not hist.empty:
            hist = hist.dropna(subset=['Close'])
            
            if len(hist) >= 2:
                current_price_usd = hist['Close'].iloc[-1]
                prev_price_usd = hist['Close'].iloc[-2]
                
                if current_price_usd <= 0.01 and len(hist) >= 3:
                    current_price_usd = hist['Close'].iloc[-2]
                    prev_price_usd = hist['Close'].iloc[-3]
                
                pct_change = ((current_price_usd - prev_price_usd) / prev_price_usd) * 100
                current_price_jpy = current_price_usd * usd_jpy

                # カード表示
                with st.container(border=True):
                    col1, col2, col3 = st.columns(3)
                    col1.metric(label="株価 (ドル)", value=f"${current_price_usd:.2f}")
                    col2.metric(label="株価 (日本円)", value=f"約 {int(current_price_jpy):,} 円")
                    col3.metric(label="前日比 (%)", value=f"{pct_change:.2f}%", delta=f"{pct_change:.2f}%")
                    st.caption(f"現在の為替レート: 1ドル = {usd_jpy:.2f}円")

                # 過去の株価の折れ線グラフ
                st.markdown(f"### 📈 {selected_company} 過去{selected_period_label}の株価の動き")
                
                chart_data = pd.DataFrame(hist['Close']).reset_index()
                st.line_chart(
                    chart_data, 
                    x="Date", 
                    y="Close", 
                    color="#2b83ba", 
                    zoom_config=False
                )
            else:
                st.warning("⚠️ 表示できる株価データが不足しています。期間を延ばして試してください。")
        else:
            st.warning("⚠️ Yahoo Financeのアクセス制限により、現在株価データを一時的に読み込めません。時間を置いてからリロードしてください。")
            
    except Exception as e:
        st.warning("⚠️ データの取得中に一時的な通信エラーが発生しました。時間を置いてリロードしてください。")

    # ニュースリンクボタン（バグ修正済み）
    st.markdown(f"### 📰 {selected_company} の最新情報をチェック")
    with st.container(border=True):
        st.write("外部サイトで最新の関連ニュースや企業情報を確認できます。")
        encoded_keyword = urllib.parse.quote(f"{selected_company}")
        
        btn_col1, btn_col2, _ = st.columns(3)
        with btn_col1:
            # 🛠️ Googleニュースの検索URLのバグを修正
            st.link_button("🌐 Googleニュースで見る", f"https://google.com{encoded_keyword}&hl=ja&gl=JP&ceid=JP:ja", use_container_width=True)
        with btn_col2:
            # 🛠️ 選択された企業に応じたYahoo!ファイナンスのページURLに動的に対応
            st.link_button("📈 Yahoo!ファイナンスで見る", f"https://yahoo.co.jp{encoded_keyword}", use_container_width=True)
