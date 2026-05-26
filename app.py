import streamlit as st
import yfinance as yf
import urllib.parse
import pandas as pd
from datetime import datetime
import pytz

# ページの設定（横幅を広くしてグラフを見やすくする）
st.set_page_config(layout="wide", page_title="米国株トレンドチェッカー PRO", page_icon="🇺🇸")

# --- 🚀 初期データの設定 ---
TICKERS = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "NFLX", "AVGO", "SBUX", "KO", "MCD", "V", "COST"]

COMPANY_NAMES = {
    "AAPL": "🍎 Apple", "MSFT": "💻 Microsoft", "NVDA": "🤖 NVIDIA", 
    "TSLA": "🚗 Tesla", "GOOGL": "🔍 Google", "AMZN": "📦 Amazon", 
    "META": "📱 Meta", "NFLX": "🍿 Netflix", "AVGO": "📡 Broadcom", 
    "SBUX": "☕ Starbucks", "KO": "🥤 Coca-Cola", "MCD": "🍟 McDonald's", 
    "V": "💳 Visa", "COST": "🛒 Costco"
}

# --- ⚙️ サイドバー：表示設定と並び替え機能 ---
st.sidebar.header("⚙️ 表示設定")

# 並び替え方法の選択
sort_method = st.sidebar.radio(
    "企業の並び替え：",
    ["標準（今のおすすめ・注目度順）", "アルファベット順 (A-Z)", "株価が高い順"]
)

# 選択された方法に応じてリストを並び替える処理
if sort_method == "アルファベット順 (A-Z)":
    sorted_tickers = sorted(TICKERS)
elif sort_method == "株価が高い順":
    with st.sidebar.spinner("株価順に並び替え中..."):
        price_list = []
        for t in TICKERS:
            try:
                tick_data = yf.Ticker(t).history(period="1d")
                current_p = tick_data['Close'].iloc[-1] if not tick_data.empty else 0
                price_list.append({"ticker": t, "price": current_p})
            except:
                price_list.append({"ticker": t, "price": 0})
        df_price = pd.DataFrame(price_list).sort_values(by="price", ascending=False)
        sorted_tickers = df_price["ticker"].tolist()
else:
    with st.sidebar.spinner("最新の市場データから注目順を計算中..."):
        recommend_list = []
        for t in TICKERS:
            try:
                tick_data = yf.Ticker(t).history(period="1d")
                if not tick_data.empty:
                    total_money = tick_data['Close'].iloc[-1] * tick_data['Volume'].iloc[-1]
                else:
                    total_money = 0
                recommend_list.append({"ticker": t, "score": total_money})
            except:
                recommend_list.append({"ticker": t, "score": 0})
        df_recommend = pd.DataFrame(recommend_list).sort_values(by="score", ascending=False)
        sorted_tickers = df_recommend["ticker"].tolist()

# セレクトボックスに表示するメニュー名を作成
display_options = []
for t in sorted_tickers:
    name = COMPANY_NAMES.get(t, f"🏢 企業")
    display_options.append(f"{name} ({t})")

selected_option = st.sidebar.selectbox("調べる企業を選んでください：", display_options)

# 選択されたメニュー名からティッカーを抽出
ticker = selected_option.split("(")[-1].replace(")", "").strip()
selected_company = selected_option

# 📊 株価チャートの期間設定
period_labels = {
    "1ヶ月": "1mo",
    "6ヶ月": "6mo",
    "1年": "1y",
    "5年": "5y"
}
selected_period_label = st.sidebar.radio("表示期間を変更できます：", list(period_labels.keys()), horizontal=False)
selected_period = period_labels[selected_period_label]

# --- 📱 メインコンテンツエリア ---
st.title("🇺🇸 米国株トレンドチェッカー PRO")
st.write("リアルタイム株価、円建て換算、最新ニュース、そして株価チャートをまとめてチェック！")

# 🟢 使い方ガイド
with st.expander("📘 このツールの使い方・見方のコツ", expanded=True):
    st.markdown(
        "- **企業を選ぶ**：左側のメニューから気になる企業を切り替えられます。\n"
        "- **期間を変える**：表示したいチャートの期間（1ヶ月〜5年）を自由に変更できます。\n"
        "- **データを見る**：チャートにマウスや指を乗せることで、詳細な株価が浮かび上がります。"
    )

# 🟢 営業時間に関する案内メッセージ
st.info("💡 **【アプリを見に来てくれた方へ】** 現在、画面には「直近の最終記録（確定データ）」を表示しています。アメリカの株式市場の営業時間内（平日の日本時間 22:30〜翌5:00、冬時間は23:30〜翌6:00）にアクセスすると、リアルタイムに株価が変動するチャートをご覧いただけます。")

with st.spinner("最新データを読み込み中..."):
    try:
        # 🟢 為替データの取得
        forex = yf.Ticker("JPY=X")
        forex_hist = forex.history(period="1mo")
        
        if not forex_hist.empty:
            valid_forex = forex_hist['Close'].dropna()
            usd_jpy = valid_forex.iloc[-1]
            prev_usd_jpy = valid_forex.iloc[-2]
            forex_pct_change = ((usd_jpy - prev_usd_jpy) / prev_usd_jpy) * 100
        else:
            usd_jpy = 150.0
            forex_pct_change = 0.0

        # 📈 為替レート（ドル円）表示エリア
        st.markdown("### 💴 為替レート（米ドル / 日本円）")
        with st.container(border=True):
            col_fx1, col_fx2 = st.columns(2)
            with col_fx1:
                st.metric(
                    label="直近の確定為替レート", 
                    value=f"1ドル = {usd_jpy:.2f} 円", 
                    delta=f"{forex_pct_change:.2f}% (前日比)"
                )
                st.caption("プラス ＝ 円安ドル高 / マイナス ＝ 円高ドル安")
            with col_fx2:
                # 🛠️ エラーの原因だった引数をすべて削除！
                forex_chart_data = pd.DataFrame(valid_forex).reset_index()
                # 日付を固定の文字列（テキスト）に変えることで、右端が絶対に削られないチャートにします
                forex_chart_data['Date'] = forex_chart_data['Date'].dt.strftime('%Y-%m-%d')
                st.line_chart(
                    forex_chart_data, 
                    x="Date", 
                    y="Close", 
                    color="#e6550d", 
                    height=120
                )

        st.write("---")

        # 🟢 個別株データの取得
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

                # 個別株カード表示
                st.markdown(f"### 📍 {selected_company} の現在値（または直近終値）")
                with st.container(border=True):
                    col1, col2, col3 = st.columns(3)
                    col1.metric(label="株価 (ドル)", value=f"${current_price_usd:.2f}")
                    col2.metric(label="株価 (日本円)", value=f"約 {int(current_price_jpy):,} 円")
                    col3.metric(label="前日比 (%)", value=f"{pct_change:.2f}%", delta=f"{pct_change:.2f}%")
                    st.caption(f"換算為替レート: 1ドル = {usd_jpy:.2f}円")

                # 個別株の折れ線グラフ
                st.markdown(f"### 📈 過去{selected_period_label}の株価の動き")
                chart_data = pd.DataFrame(hist['Close']).reset_index()
                # 日付を固定の文字列（テキスト）に変えることで、右端が絶対に削られないチャートにします
                chart_data['Date'] = chart_data['Date'].dt.strftime('%Y-%m-%d')
                st.line_chart(
                    chart_data, 
                    x="Date", 
                    y="Close", 
                    color="#2b83ba"
                )
            else:
                st.warning("⚠️ 表示できる株価データが不足しています。期間を延ばして試してください。")
        else:
            st.warning("⚠️ Yahoo Financeのアクセス制限により、現在株価データを一時的に読み込めません。時間を置いてからリロードしてください。")
            
    except Exception as e:
        st.warning("⚠️ データの取得中に一時的な通信エラーが発生しました。時間を置いてリロードしてください。")

# --- 🟢 アフィリエイト広告エリア ---
st.write("---")
st.markdown("### 🎁 米国株を始めるなら！おすすめの証券会社")
with st.container(border=True):
    col_adv1, col_adv2 = st.columns(2)
    with col_adv1:
        st.write("**💡 なぜ米国株投資で「SBI証券」が選ばれるのか？**")
        st.markdown(
            "- **業界最安水準の手数料**：無駄なコストを徹底的に抑えて投資できます。\n"
            "- **数千円から株主に**：アップルやエヌビディアの株を1株から購入可能。\n"
            "- **便利な米国株積立**：自動で毎月コツコツ買い付けできる機能が非常に便利。"
        )
    with col_adv2:
        st.write("") 
        st.write("")
        my_affiliate_url = "https://sbisec.co.jp" 
        st.link_button("🔥 無料で口座開設する (SBI証券)", my_affiliate_url, use_container_width=True, type="primary")

# --- 📰 ニュースリンクボタン ---
st.write("---")
st.markdown(f"### 📰 {selected_company} の最新情報をチェック")
with st.container(border=True):
    st.write("外部サイトで最新の関連ニュースや企業情報を確認できます。")
    
    search_keyword = f"{ticker} ニュース"
    google_url = "https://google.com?" + urllib.parse.urlencode({"q": search_keyword, "tbm": "nws"})
    yahoo_url = "https://yahoo.co.jp?" + urllib.parse.urlencode({"p": search_keyword})
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.link_button("🌐 Googleニュースで見る", google_url, use_container_width=True)
    with btn_col2:
        st.link_button("📈 Yahoo!ニュースで見る", yahoo_url, use_container_width=True)
