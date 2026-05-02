import streamlit as st
import yfinance as yf
import pandas as pd
from openai import OpenAI
import pandas_ta as ta

st.set_page_config(page_title="Grok 股票全能分析", layout="wide")
st.title("🚀 Grok 技術 + 基本面 全能股票分析工具")

api_key = st.text_input("輸入你的 Grok API Key", type="password", value=st.session_state.get("grok_key", ""))
if api_key:
    st.session_state.grok_key = api_key

ticker = st.text_input("股票代碼（美股如 NVDA，台股如 2330.TW）", "NVDA")

if st.button("生成完整分析報告", type="primary"):
    if not api_key:
        st.error("請輸入 Grok API Key")
    else:
        with st.spinner("分析中..."):
            stock = yf.Ticker(ticker)
            info = stock.info
            df = stock.history(period="1y")
            
            # 技術指標
            df['SMA20'] = ta.sma(df['Close'], length=20)
            df['SMA50'] = ta.sma(df['Close'], length=50)
            df['SMA200'] = ta.sma(df['Close'], length=200)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            macd = ta.macd(df['Close'])
            df = pd.concat([df, macd], axis=1)
            
            latest = df.iloc[-1]
            
            # 基本面
            fundamentals = {
                "目前股價": f"{latest['Close']:.2f}",
                "市值": f"{info.get('marketCap', 0)/1e9:.1f}B",
                "Trailing PE": info.get('trailingPE'),
                "Forward PE": info.get('forwardPE'),
                "EPS": info.get('trailingEps'),
                "目標價": info.get('targetMeanPrice'),
                "產業": info.get('industry'),
            }
            
            # 顯示
            st.subheader(f"{info.get('longName', ticker)} ({ticker})")
            c1,c2,c3 = st.columns(3)
            c1.metric("股價", fundamentals["目前股價"])
            c2.metric("市值", fundamentals["市值"])
            c3.metric("Trailing PE", fundamentals["Trailing PE"])
            
            st.line_chart(df[['Close', 'SMA20', 'SMA50', 'SMA200']])
            
            # Grok 分析
            client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
            prompt = f"請整合技術面與基本面分析 {ticker}，目前股價 {latest['Close']:.2f}，指標：RSI={latest['RSI']:.1f} 等，提供專業報告。"
            
            response = client.chat.completions.create(
                model="grok-4.1-fast",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.65
            )
            
            st.subheader("Grok 綜合分析報告")
            st.markdown(response.choices[0].message.content)
