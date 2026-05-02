import streamlit as st
import yfinance as yf
from openai import OpenAI

st.title("🚀 Grok 股票分析工具 - 極簡版")

api_key = st.text_input("輸入你的 Grok API Key", type="password")

ticker = st.text_input("股票代碼", "NVDA")

if st.button("開始分析"):
    if not api_key:
        st.error("請輸入 Grok API Key")
    else:
        with st.spinner("正在抓取資料並請 Grok 分析..."):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                st.success(f"已取得 {ticker} 資料")
                st.subheader(info.get('longName', ticker))
                st.write(f"目前股價：**{info.get('currentPrice', 'N/A')}**")
                
                # 呼叫 Grok
                client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
                
                prompt = f"請用繁體中文專業分析股票 {ticker}，包含技術面和基本面建議。"
                
                response = client.chat.completions.create(
                    model="grok-4.1-fast",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.subheader("Grok 分析報告")
                st.markdown(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"錯誤: {str(e)}")
