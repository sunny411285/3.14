import streamlit as st
import yfinance as yf
import pandas as pd

# ---------------------------------------------------------
# 1. ページの設定（最初の状態のまま）
# ---------------------------------------------------------
st.set_page_config(page_title="米国株 投資分析＆診断ツール", layout="wide")

st.title("🇺🇸 米国株 簡易銘柄分析シミュレーター")
st.caption("調べたい米国株のティッカーを入力すると、最新の指標を自動で取得します。")

# ---------------------------------------------------------
# 2. 条件設定エリア（サイドバー）
# ---------------------------------------------------------
st.sidebar.header("条件設定")

# 【修正ポイント】入力された文字を自動で大文字（.upper()）にして、ヤフーファイナンスが100%反応するようにしました
ticker_input = st.sidebar.text_input("ティッカーを入力 (例: AAPL, NVDA, KO)", "AAPL").upper()
investment_amount = st.sidebar.number_input("想定投資額 ($)", min_value=100, value=1000, step=100)

# ---------------------------------------------------------
# 3. ヤフーファイナンスのデータ取得と表示
# ---------------------------------------------------------
# 【修正ポイント】ボタンの有無に関わらず、入力されたティッカーで「常に最新の状態」を調べるように直しました
if ticker_input:
    try:
        with st.spinner("最新データを取得中..."):
            stock = yf.Ticker(ticker_input)
            info = stock.info
            
            # 各データの抽出
            current_price = info.get("currentPrice", 0)
            pe_ratio = info.get("trailingPE", "N/A")
            div_yield = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
            long_name = info.get("longName", "不明な銘柄")
            
            # 画面への表示（3カラム構成）
            st.subheader(f"📊 {long_name} ({ticker_input}) の分析結果")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(label="現在の株価", value=f"${current_price:,.2f}")
            with col2:
                # 数値の場合は小数点第1位までに丸める
                if isinstance(pe_ratio, (int, float)):
                    pe_ratio = round(pe_ratio, 1)
                st.metric(label="PER (割安度の指標)", value=f"{pe_ratio}")
            with col3:
                st.metric(label="予想配当利回り", value=f"{div_yield:.2f}%")
                
            # 購入シミュレーションの計算
            shares = investment_amount / current_price if current_price > 0 else 0
            est_annual_div = (investment_amount * (div_yield / 100)) if div_yield > 0 else 0
            
            st.info(f"💡 **シミュレーション結果**: ${investment_amount:,} を投資すると、約 **{shares:.2f} 株** 購入可能。年間で約 **${est_annual_div:.2f}** の配当金が期待できます。")

    except Exception as e:
        st.error("銘柄データの取得に失敗しました。ティッカーコード（英字）が正しいか確認してください。")

# ---------------------------------------------------------
# 4. アフィリエイト広告エリア（一番下）
# ---------------------------------------------------------
st.write("---")
st.subheader("🚀 米国株への投資を始めるなら")
st.write("米国株は1株から少額で購入可能です。手数料が安く、初心者にもおすすめの証券会社はこちら。")

# ※ここの「href=」のURLだけ、ご自身のアフィリエイトリンクに書き換えてください
affiliate_html = """
<div style="display: flex; gap: 20px; margin-top: 10px; margin-bottom: 30px;">
    <a href="https://example.com" target="_blank" style="text-decoration: none; flex: 1;">
        <div style="background-color: #1E3A8A; color: white; padding: 15px; text-align: center; border-radius: 8px; font-weight: bold; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
            🏆 SBI証券 で口座開設（無料）<br><span style="font-size: 11px; font-weight: normal;">米国株の取扱数・人気No.1！</span>
        </div>
    </a>
    <a href="https://example.com" target="_blank" style="text-decoration: none; flex: 1;">
        <div style="background-color: #10B981; color: white; padding: 15px; text-align: center; border-radius: 8px; font-weight: bold; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
            📱 moomoo証券 で詳細な神分析ツールを使う<br><span style="font-size: 11px; font-weight: normal;">最先端の米株アプリ・取引も可能</span>
        </div>
    </a>
</div>
"""
st.markdown(affiliate_html, unsafe_allow_html=True)


