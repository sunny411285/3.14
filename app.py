with st.spinner("最新データを読み込み中..."):
    try:
        # 🟢 為替データの取得（期間を1ヶ月に延ばしてグラフにも使えるようにする）
        forex = yf.Ticker("JPY=X")
        forex_hist = forex.history(period="1mo") # 💡 1ヶ月分のデータを取得
        
        if not forex_hist.empty:
            valid_forex = forex_hist['Close'].dropna()
            usd_jpy = valid_forex.iloc[-1]
            prev_usd_jpy = valid_forex.iloc[-2]
            
            # 為替の前日比計算
            forex_pct_change = ((usd_jpy - prev_usd_jpy) / prev_usd_jpy) * 100
        else:
            usd_jpy = 150.0
            forex_pct_change = 0.0

        # 📈 【新機能】為替レート（ドル円）の表示エリア
        st.markdown("### 💴 為替レート（米ドル / 日本円）")
        with st.container(border=True):
            col_fx1, col_fx2, col_fx3 = st.columns([1, 1, 2])
            with col_fx1:
                st.metric(
                    label="現在の一替レート", 
                    value=f"1ドル = {usd_jpy:.2f} 円", 
                    delta=f"{forex_pct_change:.2f}%"
                )
            with col_fx2:
                st.write("") # 位置調整
                st.caption("※前日比がプラスの場合は円安ドル高、マイナスの場合は円高ドル安を意味します。")
            with col_fx3:
                # 💡 直近1ヶ月の為替推移をミニグラフで表示
                forex_chart_data = pd.DataFrame(valid_forex).reset_index()
                st.line_chart(
                    forex_chart_data, 
                    x="Date", 
                    y="Close", 
                    color="#e6550d", # 為替はオレンジ色にして株価と区別
                    height=100,
                    zoom_config=False
                )

        st.write("---") # 区切り線

        # 🟢 株価データの取得（これ以降は元のコードと同じ）
        stock_data = yf.Ticker(ticker)
        hist = stock_data.history(period=selected_period)
        
        # （以下、元の個別株のカード表示やグラフ表示のコードが続きます...）
