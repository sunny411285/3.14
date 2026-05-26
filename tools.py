import streamlit as st
import yfinance as yf
import pandas as pd

def show_additional_tools():
    st.write("---") 
    st.markdown("### 🇺🇸 米国株 投資分析＆シミュレーター総合ツール")

    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        "💰 ① 配当金生活シミュレーター", 
        "📈 ② 割安・成長株スクリーナー", 
        "📊 ③ 過去の積立シミュレーター"
    ])

    with sub_tab1:
        st.write("#### 毎月の不労所得（配当金）を計算")
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
        st.write("#### リアルタイム銘柄スクリーニング")
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
        st.write("#### 過去のインデックス投資・積立実績")
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
