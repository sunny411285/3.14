import streamlit as st
import yfinance as yf
import urllib.parse
import pandas as pd

# ページの設定
st.set_page_config(layout="wide", page_title="米国株トレンドチェッカー PRO", page_icon="🇺🇸")

# --- 🚀 初期データの設定 ---
TICKERS = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "NFLX", "AVGO", "SBUX", "KO", "MCD", "V", "COST"]
COMPANY_NAMES = {
    "AAPL": "🍎 Apple", "MSFT": "💻 Microsoft", "NVDA": "🤖 NVIDIA", "TSLA": "🚗 Tesla", 
    "GOOGL": "🔍 Google", "AMZN": "📦 Amazon", "META": "📱 Meta", "NFLX": "🍿 Netflix", 
    "AVGO": "📡 Broadcom", "SBUX": "☕ Starbucks", "KO": "🥤 Coca-Cola", "MCD": "🍟 McDonald's", 
    "V": "💳 Visa", "COST": "🛒 Costco"
}

# ==========================================
# 1. サイドバー：メインメニュー
# ==========================================
st.sidebar.title("📌 メインメニュー")
page_choice = st.sidebar.radio("表示機能を選択：", ["📊 米国株チェッカー", "💡 初心者向けナビ", "❓ よくある質問(FAQ)"])
st.sidebar.markdown("---")

# --- 【メイン機能】米国株トレンドチェッカー ---
if page_choice == "📊 米国株チェッカー":
    st.sidebar.header("⚙️ 表示設定")
    sort_method = st.sidebar.radio("並び替え：", ["標準（注目順）", "アルファベット順 (A-Z)", "株価が高い順"])

    if sort_method == "アルファベット順 (A-Z)":
        sorted_tickers = sorted(TICKERS)
    elif sort_method == "株価が高い順":
        with st.sidebar.spinner("株価順に並び替え中..."):
            price_list = []
            for t in TICKERS:
                try:
                    p = yf.Ticker(t).history(period="1d")['Close'].iloc[-1]
                    price_list.append({"t": t, "p": p})
                except: price_list.append({"t": t, "p": 0})
            sorted_tickers = pd.DataFrame(price_list).sort_values(by="p", ascending=False)["t"].tolist()
    else:
        with st.sidebar.spinner("注目順を計算中..."):
            recom_list = []
            for t in TICKERS:
                try:
                    h = yf.Ticker(t).history(period="1d")
                    score = h['Close'].iloc[-1] * h['Volume'].iloc[-1] if not h.empty else 0
                    recom_list.append({"t": t, "s": score})
                except: recom_list.append({"t": t, "s": 0})
            sorted_tickers = pd.DataFrame(recom_list).sort_values(by="s", ascending=False)["t"].tolist()

    display_options = [f"{COMPANY_NAMES.get(t, '🏢 企業')} ({t})" for t in sorted_tickers]
    selected_option = st.sidebar.selectbox("企業を選んでください：", display_options)
    ticker = selected_option.split("(")[-1].replace(")", "").strip()
    selected_company = selected_option

    st.sidebar.markdown("---")
    period_labels = {"1ヶ月": "1mo", "6ヶ月": "6mo", "1年": "1y", "5年": "5y"}
    selected_p_label = st.sidebar.radio("表示期間を変更：", list(period_labels.keys()))
    selected_period = period_labels[selected_p_label]

    st.title("🇺🇸 米国株トレンドチェッカー PRO")
    with st.expander("📘 ツールの見方のコツ", expanded=True):
        st.markdown("- **企業選択**：左メニューから気になる企業を切り替え可能\n- **期間変更**：チャートの表示期間を自由に変更可能\n- **データ確認**：チャートに触れると詳細な株価を表示")

    st.info("💡 現在は「直近の確定データ」を表示しています。米市場の営業時間（日本時間 平日夜）にアクセスするとリアルタイムに株価が動きます。")

    with st.spinner("データ読み込み中..."):
        try:
            forex = yf.Ticker("JPY=X").history(period="1mo")
            if not forex.empty:
                v_fx = forex['Close'].dropna()
                usd_jpy, prev_fx = v_fx.iloc[-1], v_fx.iloc[-2]
                fx_change = ((usd_jpy - prev_fx) / prev_fx) * 100
            else: usd_jpy, fx_change = 150.0, 0.0

            st.markdown("### 💴 為替レート（米ドル / 日本円）")
            with st.container(border=True):
                c_fx1, c_fx2 = st.columns(2)
                c_fx1.metric(label="確定為替レート", value=f"1ドル = {usd_jpy:.2f} 円", delta=f"{fx_change:.2f}% (前日比)")
                fx_data = pd.DataFrame(v_fx).reset_index()
                fx_data['Date'] = fx_data['Date'].dt.strftime('%Y-%m-%d')
                with c_fx2: st.line_chart(fx_data, x="Date", y="Close", color="#e6550d", height=120)

            st.write("---")
            hist = yf.Ticker(ticker).history(period=selected_period)
            if hist is not None and not hist.empty:
                hist = hist.dropna(subset=['Close'])
                if len(hist) >= 2:
                    cur_usd = hist['Close'].iloc[-1]
                    prev_usd = hist['Close'].iloc[-2]
                    pct_change = ((cur_usd - prev_usd) / prev_usd) * 100
                    cur_jpy = cur_usd * usd_jpy

                    st.markdown(f"### 📍 {selected_company} の現在値（直近終値）")
                    with st.container(border=True):
                        col1, col2, col3 = st.columns(3)
                        col1.metric(label="株価 (ドル)", value=f"${cur_usd:.2f}")
                        col2.metric(label="株価 (日本円)", value=f"約 {int(cur_jpy):,} 円")
                        col3.metric(label="前日比 (%)", value=f"{pct_change:.2f}%", delta=f"{pct_change:.2f}%")

                    st.markdown(f"### 📈 過去{selected_p_label}の株価の動き")
                    chart_data = pd.DataFrame(hist['Close']).reset_index()
                    chart_data['Date'] = chart_data['Date'].dt.strftime('%Y-%m-%d')
                    st.line_chart(chart_data, x="Date", y="Close", color="#2b83ba")
                else: st.warning("⚠️ 表示できるデータが不足しています。")
            else: st.warning("⚠️ データを読み込めません。リロードしてください。")
        except Exception as e: st.warning("⚠️ 一時的な通信エラーが発生しました。")

    st.write("---")
    st.markdown(f"### 📰 {selected_company} の最新情報をチェック")
    with st.container(border=True):
        keyword = f"{ticker} ニュース"
        g_url = "https://google.com?" + urllib.parse.urlencode({"q": keyword, "tbm": "nws"})
        y_url = "https://yahoo.co.jp?" + urllib.parse.urlencode({"p": keyword})
        b2 = st.columns(2)
        b2.link_button("🇯🇵 Yahoo! JAPANで検索する", y_url, use_container_width=True)

    st.write("---")
    st.markdown("### 🎁 米国株を始めるなら！おすすめの証券会社")
    with st.container(border=True):
        adv1, adv2 = st.columns(2)
        adv1.markdown("**💡 SBI証券が選ばれる理由**\n- **業界最安水準の手数料**：コストを徹底的に抑制\n- **数千円から株主に**：大物米国株を1株から購入可能\n- **便利な定期積立**：自動で毎月コツコツ買い付け可能")
        with adv2:
            st.write(""); st.write("")
            st.link_button("🔥 無料で口座開設する (SBI証券)", "https://sbisec.co.jp", use_container_width=True, type="primary")

# --- 💡 投資初心者向けナビ ---
elif page_choice == "💡 初心者向けナビ":
    st.title("💡 投資初心者向け 米国株スタートガイド")
    st.info("💡 左メニューから「📊 米国株チェッカー」を選べばいつでも株価分析に戻れます。")
    
    st.markdown("## 🛠️ 米国株を始める3ステップ")
    st1, st2, st3 = st.columns(3)
    st1.markdown("### 1. 証券口座を選ぶ\n手数料が圧倒的に安い**「ネット証券」**の口座をオンラインで開設します。")
    st2.markdown("### 2. 資金を入金する\n口座に日本円を入金。日本円のまま米国株を買える「円貨決済」があるので両替の手間は不要です。")
    st3.markdown("### 3. 1株から購入する\n米国株は**1株（数千円〜）**で購入可能！本サイト掲載の大企業も少額ですぐ株主になれます。")

    st.markdown("---")
    st.markdown("## 📊 おすすめの2大ネット証券会社")
    bk1, bk2 = st.columns(2)
    with bk1:
        with st.container(border=True):
            st.subheader("👑 SBI証券 (人気・実績No.1)")
            st.markdown("- **手数料**: 業界最安水準\n- **強み**: 毎月自動で株を買い足す**「定期買付」**が非常に優秀\n- **おすすめ**: コツコツ積立貯金感覚で始めたい方")
            st.link_button("🚀 SBI証券で口座開設する（無料）", "https://sbisec.co.jp", type="primary", use_container_width=True)
    with bk2:
        with st.container(border=True):
            st.subheader("🔴 楽天証券 (使いやすさNo.1)")
            st.markdown("- **手数料**: 業界最安水準\n- **強み**: アプリ**「iSPEED」**が抜群に見やすく初心者向け。楽天ポイント利用も可能\n- **おすすめ**: 楽天経済圏の方や操作性を重視する方")
            st.link_button("👉 楽天証券で口座開設する（無料）", "https://rakuten-sec.co.jp", use_container_width=True)

