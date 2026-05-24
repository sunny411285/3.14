import streamlit as st
import yfinance as yf
import urllib.parse
import pandas as pd
from datetime import datetime
import pytz

# ページの設定（横幅を広くしてグラフを見やすくする）
st.set_page_config(layout="wide", page_title="米国株トレンドチェッカー PRO", page_icon="🇺🇸")

# --- 🚀 デザイン強化：サイドバーに設定を集約 ---
st.sidebar.header("⚙️ 表示設定")

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
selected_company = st.sidebar.selectbox("調べる企業を選んでください：", list(companies.keys()))
ticker = companies[selected_company]

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

# 🟢 アフィリエイト広告エリア（信頼感とメリットを大幅強化）
st.markdown("### 🎁 米国株を始めるなら！おすすめの証券会社")
with st.container(border=True):
    col_adv1, col_adv2 = st.columns([2, 1]) # 💡 比率を2:1に修正してエラーを解決
    with col_adv1:
        st.write("**💡 なぜ米国株投資で「SBI証券」が選ばれるのか？**")
        st.markdown(
            "- **業界最安水準**の手数料でコストを徹底的に抑られる\n"
            "- 1株（数千円）から**アップルやエヌビディアの株主**になれる\n"
            "- 自動で毎月コツコツ買える**「米国株積立」**が非常に便利"
        )
    with col_adv2:
        st.write("") # 上下の位置微調整用
        st.write("")
        my_affiliate_url = "https://sbisec.co.jp" # ⚠️ A8.netの「メール用URL」が届いたらここを書き換えてください
        st.link_button("🔥 無料で口座開設する (SBI証券)", my_affiliate_url, use_container_width=True, type="primary")

st.write("---")

# 🟢 見る人へ：今が営業時間外（土日など）か自動判定して説明を出す
jst = pytz.timezone('Asia/Tokyo')
now_jst = datetime.now(jst)
weekday = now_jst.weekday()  # 0=月, 1=火, 2=水, 3=木, 4=金, 5=土, 6=日
hour = now_jst.hour
minute = now_jst.minute

# 現在の月をもとに夏時間（3月〜10月）か冬時間（11月〜2月）かを判定
is_summer_time = 3 <= now_jst.month <= 10

if is_summer_time:
    # 夏時間：22:30 〜 翌05:00
    start_h, start_m = 22, 30
    end_h = 5
    guide_time_str = "22:30〜翌5:00（夏時間）"
else:
    # 冬時間：23:30 〜 翌06:00
    start_h, start_m = 23, 30
    end_h = 6
    guide_time_str = "23:30〜翌6:00（冬時間）"

# 1. まず「市場が今リアルタイムに開いているか」を判定する
is_market_open = False

# 火・水・木・金・土（1, 2, 3, 4, 5）の深夜（0:00〜朝5時/6時まで）は、米国時間の平日のため動いている
if weekday in [1, 2, 3, 4, 5]: # 💡 曜日リストの抜けを修正
    if hour < end_h:
        is_market_open = True

# 月・火・水・木・金（0, 1, 2, 3, 4）の夜（22:30/23:30以降〜24:00まで）は、市場が開いている
if weekday in [0, 1, 2, 3, 4]: # 💡 曜日リストの抜けを修正
    if hour > start_h or (hour == start_h and minute >= start_m):
        is_market_open = True

# 2. 開いていないなら「営業時間外」とする
is_market_closed = not is_market_open

# 営業時間外の場合だけ案内を表示（最後の記録を映している旨を追記）
if is_market_closed:
    st.info(f"💡 **【アプリを見に来てくれた方へ】** 現在、アメリカの株式市場は営業時間外（または定休日）です。画面には「直近の最終記録」を表示しています。平日の夜（日本時間 **{guide_time_str}**）にアクセスすると、リアルタイムに動くチャートをご覧いただけます！")

with st.spinner("最新データを読み込み中..."):
    try:
        # 🟢 為替データの取得（期間を1ヶ月にしてグラフに対応）
        forex = yf.Ticker("JPY=X")
        forex_hist = forex.history(period="1mo")
        
        if not forex_hist.empty:
            valid_forex = forex_hist['Close'].dropna()
            usd_jpy = valid_forex.iloc[-1]
            prev_usd_jpy = valid_forex.iloc[-2]
            
            # 為替の前日比計算
            forex_pct_change = ((usd_jpy - prev_usd_jpy) / prev_usd_jpy) * 100
        else:
            usd_jpy = 150.0
            forex_pct_change = 0.0

        # 📈 為替レート（ドル円）表示エリア
        st.markdown("### 💴 為替レート（米ドル / 日本円）")
        with st.container(border=True):
            col_fx1, col_fx2 = st.columns([1, 1]) # 💡 比率を明示
            with col_fx1:
                st.metric(
                    label="直近の確定為替レート", 
                    value=f"1ドル = {usd_jpy:.2f} 円", 
                    delta=f"{forex_pct_change:.2f}% (前日比)"
                )
                st.caption("※プラス＝円安ドル高 / マイナス＝円高ドル安")
            with col_fx2:
                # 直近1ヶ月の為替推移ミニグラフ
                forex_chart_data = pd.DataFrame(valid_forex).reset_index()
                st.line_chart(
                    forex_chart_data, 
                    x="Date", 
                    y="Close", 
                    color="#e6550d", # 為替はオレンジ色
                    height=100,
                    zoom_config=False
                )

        st.write("---")

        # 🟢 個別株データの取得
        stock_data = yf.Ticker(ticker)
        hist = stock_data.history(period=selected_period)

        if hist is not None and not hist.empty:
            # 空白の行を完全に除外して、最後の記録を確実に残す
            hist = hist.dropna(subset=['Close'])
            
            if len(hist) >= 2:
                current_price_usd = hist['Close'].iloc[-1]
                prev_price_usd = hist['Close'].iloc[-2]
                
                # 万が一最新値が異常値（0以下）だった場合のガード
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
                st.line_chart(
                    chart_data, 
                    x="Date", 
                    y="Close", 
                    color="#2b83ba", # 株価は青色
                    zoom_config=False
                )
            else:
                st.warning("⚠️ 表示できる株価データが不足しています。期間を延ばして試してください。")
        else:
            st.warning("⚠️ Yahoo Financeのアクセス制限により、現在株価データを一時的に読み込めません。時間を置いてからリロードしてください。")
            
    except Exception as e:
        st.warning("⚠️ データの取得中に一時的な通信エラーが発生しました。時間を置いてリロードしてください。")

    # 📘 使い方ガイド（折りたたみ表示）
    with st.expander("📘 このツールの使い方・見方のコツ"):
        st.markdown(
            "1. 左側のメニューから**気になる企業**と**期間**を選びます。\n"
            "2. 前日比（%）がプラスなら緑色で表示され、マイナスなら赤色で表示されます。\n"
            "3. チャートにマウスを乗せると、その日の詳細な株価がピンポイントで確認できます。"
        )

    # ニュースリンクボタン（バグ修正・スマホ最適化済み）
    st.markdown(f"### 📰 {selected_company} の最新情報をチェック")
    with st.container(border=True):
        st.write("外部サイトで最新の関連ニュースや企業情報を確認できます。")
        encoded_keyword = urllib.parse.quote(f"{selected_company}")
        
        btn_col1, btn_col2, _ = st.columns(3)
        with btn_col1:
            st.link_button("🌐 Googleニュースで見る", f"https://google.com{encoded_keyword}&hl=ja&gl=JP&ceid=JP:ja", use_container_width=True)
        with btn_col2:
            st.link_button("📈 Yahoo!ファイナンスで見る", f"https://yahoo.co.jp{encoded_keyword}", use_container_width=True)
