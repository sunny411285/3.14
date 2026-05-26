import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# ページ全体の基本設定
st.set_page_config(page_title="米国株 投資分析＆シミュレーター総合ツール", layout="wide", page_icon="🇺🇸")

# カスタムCSSでボタンやデザインを装飾
st.markdown("""
<style>
    .reportview-container { background: #f0f2f6; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🇺🇸 米国株 投資分析＆シミュレーター総合ツール")
st.caption("あなたの投資目的に合わせて、リアルタイムデータから最適なシミュレーションを行います。")

# タブの作成（①②③を一画面に集約）
tab1, tab2, tab3 = st.tabs(["💰 ① 配当金生活シミュレーター", "📈 ② 割安・成長株スクリーナー", "📊 ③ 過去の積立シミュレーター"])

# ==========================================
# タブ①：配当金生活シミュレーター
# ==========================================
with tab1:
    st.header("毎月の不労所得（配当金）をシミュレーション")
    st.write("「毎月いくら欲しいか」から、必要な投資額と、米国の代表的な高配当・増配株ポートフォリオを自動計算します。")
    
    col_t1_1, col_t1_2 = st.columns(2)
    with col_t1_1:
        target_monthly_income = st.number_input("目標とする毎月の配当金 (万円)", min_value=1, value=10, step=1)
    with col_t1_2:
        assumed_yield = st.slider("想定する平均配当利回り (%)", min_value=2.0, max_value=7.0, value=4.5, step=0.1)
    
    # 計算ロジック (1ドル=150円、税金約28%考慮: 米国10%+国内20.315%)
    exchange_rate = 150.0 
    tax_factor = 0.72  # 税引後手取り
    
    target_annual_income_jpy = target_monthly_income * 12 * 10000
    required_annual_income_gross_jpy = target_annual_income_jpy / tax_factor
    required_capital_jpy = required_annual_income_gross_jpy / (assumed_yield / 100)
    required_capital_usd = required_capital_jpy / exchange_rate
    
    st.success(f"💡 **シミュレーション結果**: 毎月手取り **{target_monthly_income}万円** の配当金を得るには、年利 {assumed_yield}% の場合、約 **{required_capital_jpy/100000000:.2f} 億円** （${required_capital_usd:,.0f}）の投資資金が必要です。")
    
    st.subheader("🇺🇸 おすすめの高配当・増配銘柄（例）")
    example_div_data = {
        "ティッカー": ["KO", "JNJ", "PG", "VZ"],
        "企業名": ["コカ・コーラ", "ジョンソン＆ジョンソン", "プロクター＆ギャンブル", "ベライゾン"],
        "特徴": ["60年以上連続増配の王道", "ヘルスケアの超安定企業", "日用品世界最大手・連続増配", "連続増配中の高配当通信株"]
    }
    st.table(pd.DataFrame(example_div_data))
    
    # アフィリエイト動線（高配当・新NISA狙い向け）
    st.markdown("""
    <div style="background-color: #f0f7ff; padding: 20px; border-radius: 8px; border-left: 5px solid #1E3A8A; margin-top: 20px;">
        <h4>🚀 米国高配当株で一歩を踏み出そう</h4>
        <p>米株は日本の株と違い、<b>1株（数千円）から買えて年4回配当金</b>がもらえます。新NISAの成長投資枠を使って非課税でコツコツ買い増すのが王道です。</p>
        <a href="https://example.com" target="_blank" style="text-decoration: none;">
            <div style="background-color: #1E3A8A; color: white; padding: 12px; text-align: center; border-radius: 5px; font-weight: bold; width: 300px; margin-top: 10px;">
                🏆 SBI証券で口座開設（無料）
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# タブ②：割安・成長株スクリーナー
# ==========================================
with tab2:
    st.header("リアルタイム銘柄スクリーニング")
    st.write("設定した条件に合う米国株の指標をリアルタイムでチェックします。")
    
    # 主要銘柄のリスト（API負荷軽減のためあらかじめ定義）
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX"]
    
    col_t2_1, col_t2_2 = st.columns(2)
    with col_t2_1:
        max_pe = st.slider("許容する最大PER (割安度の目安)", min_value=10, max_value=80, value=40, step=5)
    with col_t2_2:
        min_div = st.slider("最低限ほしい配当利回り (%)", min_value=0.0, max_value=5.0, value=0.0, step=0.5)
        
    if st.button("🔍 条件に合う銘柄を検索（データ取得）"):
        with st.spinner("最新データを取得中..."):
            screened_data = []
            for t in tickers:
                try:
                    stock = yf.Ticker(t)
                    info = stock.info
                    pe = info.get("trailingPE", None)
                    dy = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
                    price = info.get("currentPrice", 0)
                    
                    # フィルタリング条件
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
                
    # アフィリエイト動線（分析・玄人向け）
    st.markdown("""
    <div style="background-color: #f0fdf4; padding: 20px; border-radius: 8px; border-left: 5px solid #10B981; margin-top: 20px;">
        <h4>📊 もっと多くの米国株をプロ並みに分析したいなら</h4>
        <p>エヌビディアやテスラなど、次世代の爆益成長株を見つけるにはリアルタイムの大口投資家の動きや板情報が不可欠です。最先端の米株分析アプリを無料で手に入れましょう。</p>
        <a href="https://example.com" target="_blank" style="text-decoration: none;">
            <div style="background-color: #10B981; color: white; padding: 12px; text-align: center; border-radius: 5px; font-weight: bold; width: 350px; margin-top: 10px;">
                📱 moomoo証券の次世代アプリを試す（無料）
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# タブ③：過去の積立シミュレーター
# ==========================================
with tab3:
    st.header("過去のインデックス投資・積立実績シミュレーション")
    st.write("もし過去10年間、毎月一定額を「S&P500（米国の代表的な指数）」に積み立てていたら、今いくらになっていたかを計算します。")
    
    col_t3_1, col_t3_2 = st.columns(2)
    with col_t3_1:
        monthly_investment_jpy = st.number_input("毎月の積立額 (万円)", min_value=1, value=3, step=1)
    with col_t3_2:
        years = st.slider("積立期間 (年間)", min_value=1, max_value=10, value=10, step=1)
        
    # 歴史的な平均リターン（S&P500の過去平均を約10%と仮定、複利計算）
    annual_return = 0.10
    monthly_return = (1 + annual_return) ** (1/12) - 1
    months = years * 12
    
    # 複利計算
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
        
    st.caption("※過去のデータに基づくシミュレーションであり、将来の成果を保証するものではありません。")
    
    # アフィリエイト動線（初心者・インデックス向け）
    st.markdown("""
    <div style="background-color: #fff7ed; padding: 20px; border-radius: 8px; border-left: 5px solid #F97316; margin-top: 20px;">
        <h4>🔰 ほったらかしで資産を増やすならクレカ積立</h4>
        <p>S&P500やオルカンへの積立は、三井住友カードや楽天カードを使った「クレカ積立」がお得です。投資しながらポイントが毎月自動で貯まります。</p>
        <a href="https://example.com" target="_blank" style="text-decoration: none;">
            <div style="background-color: #F97316; color: white; padding: 12px; text-align: center; border-radius: 5px; font-weight: bold; width: 300px; margin-top: 10px;">
                💳 楽天証券×楽天カードで始める
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)
