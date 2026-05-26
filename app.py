import streamlit as st
import yfinance as yf
import pandas as pd

# =====================================================================
# 【基盤】元々あったベースの画面（ここを変更せず残しています）
# =====================================================================

# ページ全体の基本設定
st.set_page_config(page_title="米国株 投資分析＆診断ツール", layout="wide", page_icon="🇺🇸")

st.title("🇺🇸 米国株 簡易銘柄分析シミュレーター")
st.caption("調べたい米国株のティッカーを入力すると、最新の指標を自動で取得します。")

# 1. ユーザーの入力エリア（サイドバー）
st.sidebar.header("条件設定")
ticker_input = st.sidebar.text_input("ティッカーを入力 (例: AAPL, NVDA, KO)", "AAPL").upper()
investment_amount = st.sidebar.number_input("想定投資額 ($)", min_value=100, value=1000, step=100)

# 2. データ取得とメイン処理
if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # データの抽出
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
            st.metric(label="PER (割安度の指標)", value=f"{pe_ratio}")
        with col3:
            st.metric(label="予想配当利回り", value=f"{div_yield:.2f}%")
            
        # 購入シミュレーション
        shares = investment_amount / current_price if current_price > 0 else 0
        est_annual_div = (investment_amount * (div_yield / 100)) if div_yield > 0 else 0
        
        st.info(f"💡 **シミュレーション結果**: ${investment_amount:,} を投資すると、約 **{shares:.2f} 株** 購入可能。年間で約 **${est_annual_div:.2f}** の配当金が期待できます。")

    except Exception as e:
        st.error("銘柄データの取得に失敗しました。ティッカーが正しいか確認してください。")

# --- ここからアフィリエイト動線 ---
st.write("---")
st.subheader("🚀 米国株への投資を始めるなら")
st.write("米国株は1株から少額で購入可能です。手数料が安く、初心者にもおすすめの証券会社はこちら。")

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


# =====================================================================
# 【追加機能】①②③をまとめたタブ（元の画面のすぐ下にくっつきます）
# =====================================================================

st.write("---") 
st.markdown("## 🇺🇸 米国株 投資分析＆シミュレーター総合ツール")
st.caption("あなたの投資目的に合わせて、追加のシミュレーションを行えます。")

# タブの作成（重複を避けるために独立したタブを用意）
sub_tab1, sub_tab2, sub_tab3 = st.tabs([
    "💰 ① 配当金生活シミュレーター", 
    "📈 ② 割安・成長株スクリーナー", 
    "📊 ③ 過去の積立シミュレーター"
])

# -----------------------------------------------------------------
# ① 配当金生活シミュレーター
# -----------------------------------------------------------------
with sub_tab1:
    st.write("### 毎月の不労所得（配当金）を計算")
    col_t1_1, col_t1_2 = st.columns(2)
    with col_t1_1:
        target_monthly_income = st.number_input("目標とする毎月の配当金 (万円)", min_value=1, value=10, step=1, key="add_t1_inc")
    with col_t1_2:
        assumed_yield = st.slider("想定する平均配当利回り (%)", min_value=2.0, max_value=7.0, value=4.5, step=0.1, key="add_t1_yld")
    
    # 計算ロジック (1ドル=150円、税金約28%考慮: 米国10%+国内20.315%)
    exchange_rate = 150.0 
    tax_factor = 0.72  
    
    target_annual_income_jpy = target_monthly_income * 12 * 10000
    required_annual_income_gross_jpy = target_annual_income_jpy / tax_factor
    required_capital_jpy = required_annual_income_gross_jpy / (assumed_yield / 100)
    required_capital_usd = required_capital_jpy / exchange_rate
    
    st.success(f"💡 **シミュレーション結果**: 毎月手取り **{target_monthly_income}万円** の配当金を得るには、年利 {assumed_yield}% の場合、約 **{required_capital_jpy/100000000:.2f} 億円** （${required_capital_usd:,.0f}）の投資資金が必要です。")
    
    st.markdown("""
    <div style="background-color: #f0f7ff; padding: 15px; border-radius: 8px; border-left: 5px solid #1E3A8A; margin-top: 15px;">
        <p style="margin: 0; font-size: 14px;"><b>🚀 米国高配当株で一歩を踏み出そう</b><br>
        米株は1株（数千円）から買えて年4回配当金がもらえます。新NISAでコツコツ始めるなら手数料最安のSBI証券が王道です。</p>
        <a href="https://example.com" target="_blank" style="text-decoration: none; display: inline-block; background-color: #1E3A8A; color: white; padding: 8px 16px; border-radius: 5px; font-weight: bold; margin-top: 10px; font-size: 13px;">🏆 SBI証券で口座開設（無料）</a>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# ② 割安・成長株スクリーナー
# -----------------------------------------------------------------
with sub_tab2:
    st.write("### リアルタイム銘柄スクリーニング")
    # 主要銘柄のリスト
    tickers_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX"]
    
    col_t2_1, col_t2_2 = st.columns(2)
    with col_t2_1:
        max_pe = st.slider("許容する最大PER (割安度の目安)", min_value=10, max_value=80, value=40, step=5, key="add_t2_pe")
    with col_t2_2:
        min_div = st.slider("最低限ほしい配当利回り (%)", min_value=0.0, max_value=5.0, value=0.0, step=0.5, key="add_t2_div")
        
    if st.button("🔍 条件に合う銘柄を検索（データ取得）", key="add_t2_btn"):
        with st.spinner("最新データを取得中..."):
            screened_data = []
            for t in tickers_list:
                try:
                    stock = yf.Ticker(t)
                    info = stock.info
                    pe = info.get("trailingPE", None)
                    dy = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
                    price = info.get("currentPrice", 0)
                    
                    if pe and pe <= max_pe and dy >= min_div:
                        screened_data.append({
                            "銘柄名": info.get("longName", t),
                            "ティッカー": t,
                            "現在の株価": f"${price:,.2f}",
                            "PER": round(pe, 1),
                            "配当利回り": f"{dy:.2f}%"
                        })
                except:
                    continue
            
            if screened_data:
                st.dataframe(pd.DataFrame(screened_data), use_container_width=True)
            else:
                st.warning("条件に一致する銘柄が見つかりませんでした。条件を緩めてみてください。")
                
    st.markdown("""
    <div style="background-color: #f0fdf4; padding: 15px; border-radius: 8px; border-left: 5px solid #10B981; margin-top: 15px;">
        <p style="margin: 0; font-size: 14px;"><b>📊 もっと多くの米国株をプロ並みに分析したいなら</b><br>
        エヌビディアやテスラなど、次世代の成長株を見つけるにはリアルタイムの板情報が不可欠。最先端の米株分析アプリを無料で手に入れましょう。</p>
        <a href="https://example.com" target="_blank" style="text-decoration: none; display: inline-block; background-color: #10B981; color: white; padding: 8px 16px; border-radius: 5px; font-weight: bold; margin-top: 10px; font-size: 13px;">📱 moomoo証券の次世代アプリを試す（無料）</a>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# ③ 過去の積立シミュレーター
# -----------------------------------------------------------------
with sub_tab3:
    st.write("### 過去のインデックス投資・積立実績")
    col_t3_1, col_t3_2 = st.columns(2)
    with col_t3_1:
        monthly_investment_jpy = st.number_input("毎月の積立額 (万円)", min_value=1, value=3, step=1, key="add_t3_amt")
    with col_t3_2:
        years = st.slider("積立期間 (年間)", min_value=1, max_value=10, value=10, step=1, key="add_t3_yrs")
        
    # 歴史的な平均リターン（S&P500の過去平均を約10%と仮定、複利計算）
    annual_return = 0.10
    monthly_return = (1 + annual_return) ** (1/12) - 1
    months = years * 12
    
    total_invested = monthly_investment_jpy * months
    total_future_value = 0
    for i in range(months):
        total_future_value = (total_future_value + monthly_investment_jpy) * (1 + monthly_return)
        
    profit = total_future_value - total_invested
    
    st.info(f"📈 **{years}年間の積立シミュレーション結果** (年利10%想定)")
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("元本（投資した総額）", f"{total_invested:,} 万円")
    with col_res2:
        st.metric("最終的な資産額", f"{int(total_future_value):,} 万円")
    with col_res3:
        st.metric("増えた運用益", f"+{int(profit):,} 万円", delta=f"{int((profit/total_invested)*100)}%")
        
    st.markdown("""
    <div style="background-color: #fff7ed; padding: 15px; border-radius: 8px; border-left: 5px solid #F97316; margin-top: 15px;">
        <p style="margin: 0; font-size: 14px;"><b>🔰 ほったらかしで資産を増やすならクレカ積立</b><br>
        S&P500への積立は、カード決済でポイントが自動で貯まる「クレカ積立」が絶対にお得です。</p>
        <a href="https://example.com" target="_blank" style="text-decoration: none; display: inline-block; background-color: #F97316; color: white; padding: 8px 16px; border-radius: 5px; font-weight: bold; margin-top: 10px; font-size: 13px;">💳 楽天証券×楽天カードで始める</a>
    </div>
    """, unsafe_allow_html=True)
st.write("---") 

sub_tab1, sub_tab2, sub_tab3 = st.tabs([
    "💰 ① 配当金生活シミュレーター", 
    "📈 ② 割安・成長株スクリーナー", 
    "📊 ③ 過去の積立シミュレーター"
])

with sub_tab1:
    st.write("### 毎月の不労所得（配当金）を計算")
    col_t1_1, col_t1_2 = st.columns(2)
    with col_t1_1:
        target_monthly_income = st.number_input("目標とする毎月の配当金 (万円)", min_value=1, value=10, step=1, key="add_t1_inc")
    with col_t1_2:
        assumed_yield = st.slider("想定する平均配当利回り (%)", min_value=2.0, max_value=7.0, value=4.5, step=0.1, key="add_t1_yld")
    
    exchange_rate = 150.0 
    tax_factor = 0.72  
    
    target_annual_income_jpy = target_monthly_income * 12 * 10000
    required_annual_income_gross_jpy = target_annual_income_jpy / tax_factor
    required_capital_jpy = required_annual_income_gross_jpy / (assumed_yield / 100)
    required_capital_usd = required_capital_jpy / exchange_rate
    
    st.success(f"💡 **シミュレーション結果**: 毎月手取り **{target_monthly_income}万円** の配当金を得るには、年利 {assumed_yield}% の場合、約 **{required_capital_jpy/100000000:.2f} 億円** （${required_capital_usd:,.0f}）の投資資金が必要です。")
    
    st.markdown("""
    <div style="background-color: #f0f7ff; padding: 15px; border-radius: 8px; border-left: 5px solid #1E3A8A; margin-top: 15px;">
        <p style="margin: 0; font-size: 14px; color: #1E3A8A;"><b>🚀 米国高配当株で一歩を踏み出そう</b><br>
        米株は1株（数千円）から買えて年4回配当金がもらえます。新NISAでコツコツ始めるなら手数料最安のSBI証券が王道です。</p>
        <a href="https://example.com" target="_blank" style="text-decoration: none; display: inline-block; background-color: #1E3A8A; color: white; padding: 8px 16px; border-radius: 5px; font-weight: bold; margin-top: 10px; font-size: 13px;">🏆 SBI証券で口座開設（無料）</a>
    </div>
    """, unsafe_allow_html=True)

with sub_tab2:
    st.write("### リアルタイム銘柄スクリーニング")
    tickers_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX"]
    
    col_t2_1, col_t2_2 = st.columns(2)
    with col_t2_1:
        max_pe = st.slider("許容する最大PER (割安度の目安)", min_value=10, max_value=80, value=40, step=5, key="add_t2_pe")
    with col_t2_2:
        min_div = st.slider("最低限ほしい配当利回り (%)", min_value=0.0, max_value=5.0, value=0.0, step=0.5, key="add_t2_div")
        
    if st.button("🔍 条件に合う銘柄を検索（データ取得）", key="add_t2_btn"):
        with st.spinner("最新データを取得中..."):
            screened_data = []
            for t in tickers_list:
                try:
                    stock = yf.Ticker(t)
                    info = stock.info
                    pe = info.get("trailingPE", None)
                    dy = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
                    price = info.get("currentPrice", 0)
                    
                    if pe and pe <= max_pe and dy >= min_div:
                        screened_data.append({
                            "銘柄名": info.get("longName", t),
                            "ティッカー": t,
                            "現在の株価": f"${price:,.2f}",
                            "PER": round(pe, 1),
                            "配当利回り": f"{dy:.2f}%"
                        })
                except:
                    continue
            
            if screened_data:
                st.dataframe(pd.DataFrame(screened_data), use_container_width=True)
            else:
                st.warning("条件に一致する銘柄が見つかりませんでした。条件を緩めてみてください。")
                
    st.markdown("""
    <div style="background-color: #f0fdf4; padding: 15px; border-radius: 8px; border-left: 5px solid #10B981; margin-top: 15px;">
        <p style="margin: 0; font-size: 14px; color: #10B981;"><b>📊 もっと多くの米国株をプロ並みに分析したいなら</b><br>
        エヌビディアやテスラなど、次世代の成長株を見つけるにはリアルタイムの板情報が不可欠。最先端の米株分析アプリを無料で手に入れましょう。</p>
        <a href="https://example.com" target="_blank" style="text-decoration: none; display: inline-block; background-color: #10B981; color: white; padding: 8px 16px; border-radius: 5px; font-weight: bold; margin-top: 10px; font-size: 13px;">📱 moomoo証券の次世代アプリを試す（無料）</a>
    </div>
    """, unsafe_allow_html=True)

with sub_tab3:
    st.write("### 過去のインデックス投資・積立実績")
    col_t3_1, col_t3_2 = st.columns(2)
    with col_t3_1:
        monthly_investment_jpy = st.number_input("毎月の積立額 (万円)", min_value=1, value=3, step=1, key="add_t3_amt")
    with col_t3_2:
        years = st.slider("積立期間 (年間)", min_value=1, max_value=10, value=10, step=1, key="add_t3_yrs")
        
    annual_return = 0.10
    monthly_return = (1 + annual_return) ** (1/12) - 1
    months = years * 12
    
    total_invested = monthly_investment_jpy * months
    total_future_value = 0
    for i in range(months):
        total_future_value = (total_future_value + monthly_investment_jpy) * (1 + monthly_return)
        
    profit = total_future_value - total_invested
    
    st.info(f"📈 **{years}年間の積立シミュレーション結果** (年利10%想定)")
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("元本（投資した総額）", f"{total_invested:,} 万円")
    with col_res2:
        st.metric("最終的な資産額", f"{int(total_future_value):,} 万円")
    with col_res3:
        st.metric("増えた運用益", f"+{int(profit):,} 万円", delta=f"{int((profit/total_invested)*100)}%")
        
    st.markdown("""
    <div style="background-color: #fff7ed; padding: 15px; border-radius: 8px; border-left: 5px solid #F97316; margin-top: 15px;">
        <p style="margin: 0; font-size: 14px; color: #F97316;"><b>🔰 ほったらかしで資産を増やすならクレカ積立</b><br>
        S&P500への積立は、カード決済でポイントが自動で貯まる「クレカ積立」が絶対にお得です。</p>
        <a href="https://example.com" target="_blank" style="text-decoration: none; display: inline-block; background-color: #F97316; color: white; padding: 8px 16px; border-radius: 5px; font-weight: bold; margin-top: 10px; font-size: 13px;">💳 楽天証券×楽天カードで始める</a>
    </div>
    """, unsafe_allow_html=True)

