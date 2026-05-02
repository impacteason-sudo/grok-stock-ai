import streamlit as st
import yfinance as yf
from openai import OpenAI
import pandas as pd
import pandas_ta as ta

st.title("🚀 Grok 股票分析工具（簡化版）")

api_key = st.text_input("輸入 Grok API Key", type="password")

ticker = st.text_input("股票代碼", "NVDA")

if st.button("開始分析"):
    if not api_key:
        st.error("請輸入 Grok API Key")
    else:
        with st.spinner("正在分析..."):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                df = stock.history(period="6mo")
                
                # 基本顯示
                st.subheader(f"{info.get('longName', ticker)} ({ticker})")
                st.metric("目前股價", f"{df['Close'].iloc[-1]:.2f}")
                
                st.line_chart(df['Close'])
                
                # 簡單技術指標
                df['SMA20'] = ta.sma(df['Close'], length=20)
                st.line_chart(df[['Close', 'SMA20']])
                
                # Grok 分析
                client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
                
                prompt = f"請分析股票 {ticker}，目前股價 {df['Close'].iloc[-1]:.2f}，提供技術面與基本面綜合建議。用繁體中文。"
                
                response = client.chat.completions.create(
                    model="grok-4.1-fast",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.subheader("Grok 分析報告")
                st.write(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"發生錯誤: {str(e)}")
