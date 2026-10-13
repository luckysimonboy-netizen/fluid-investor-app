import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import sys
from pathlib import Path

# --- 核心修复：防止云端部署时找不到 config 文件夹 ---
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config.settings import DEFAULT_PORTFOLIO, MASTER_QUOTES

# --- 1. 页面配置与 ColorOS 17 流体 CSS 注入 ---
st.set_page_config(page_title="流体透镜 | 价值投资", layout="wide", page_icon="💧")

st.markdown("""
<style>
    /* 隐藏原生多余元素 */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 核心：ColorOS 17 Aquamorphic (水生/流体质感) 卡片 */
    .metric-box {
        background: rgba(12, 22, 39, 0.55);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 24px;
        border-radius: 28px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        margin-bottom: 20px;
        transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1), background 0.4s ease;
    }
    
    /* 绝佳的轻盈悬浮交互反馈 */
    .metric-box:hover {
        transform: translateY(-6px);
        background: rgba(16, 30, 50, 0.7);
        border: 1px solid rgba(0, 180, 185, 0.3);
    }
    
    .metric-title { color: #7B8B9E; font-size: 13px; font-weight: 500; letter-spacing: 0.5px; }
    .metric-value { 
        color: #00B4B9; 
        font-size: 32px; 
        font-weight: 600; 
        margin-top: 8px; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 大师语录的流体渐变容器 */
    .quote-box {
        background: linear-gradient(135deg, rgba(0, 180, 185, 0.15) 0%, rgba(12, 22, 39, 0) 100%);
        border-left: 4px solid #00B4B9;
        padding: 20px 24px;
        font-family: "PingFang SC", "OPPO Sans", sans-serif;
        color: #D1E0EB;
        border-radius: 0 24px 24px 0;
        margin: 24px 0;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        font-size: 16px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. 数据获取 ---
@st.cache_data(ttl=3600)
def fetch_stock_data(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="5y", interval="1mo")
        return info, hist
    except Exception as e:
        return None, None

# --- 3. 侧边栏 ---
with st.sidebar:
    st.markdown("<h2 style='color:#00B4B9; font-weight:700;'>💧 Aquamorphic<br>Master Lens</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#7B8B9E;'>用最轻盈的视觉，看最硬核的商业模式。</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    selected_ticker = st.selectbox("自选资产池 (个股与宽基)", DEFAULT_PORTFOLIO)
    custom_ticker = st.text_input("搜寻其他标的 (如 TSLA)").upper()
    
    target_ticker = custom_ticker if custom_ticker else selected_ticker

# --- 4. 主渲染逻辑 ---
if target_ticker:
    info, hist = fetch_stock_data(target_ticker)
    
    if info is None or 'shortName' not in info:
        st.error(f"暂未获取到 {target_ticker} 的数据，系统可能将其视为了无效代码。")
    else:
        name = info.get('shortName', target_ticker)
        price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        market_cap = info.get('marketCap', 0)
        fcf = info.get('freeCashflow', 0)
        roe = info.get('returnOnEquity', 0)
        pe = info.get('trailingPE', 0)
        margin = info.get('operatingMargins', 0)
        
        fcf_yield = (fcf / market_cap * 100) if market_cap and fcf else 0
        roe_pct = roe * 100 if roe else 0
        margin_pct = margin * 100 if margin else 0

        st.markdown(f"<h1 style='font-weight: 700; margin-bottom: 0;'>{name} <span style='color: #7B8B9E; font-size:24px;'>{target_ticker}</span></h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #00B4B9; margin-top: 5px;'>${price}</h3>", unsafe_allow_html=True)
        
        st.markdown(f'<div class="quote-box">{MASTER_QUOTES["safety"]}</div>', unsafe_allow_html=True)

        st.markdown("### 🧬 核心财务基因")
        col1, col2, col3, col4 = st.columns(4)
        
        def render_fluid_card(title, value, suffix=""):
            return f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}{suffix}</div>
            </div>
            """
            
        if "QQQ" in target_ticker or "SPY" in target_ticker:
            col1.markdown(render_fluid_card("资产属性", "指数 ETF"), unsafe_allow_html=True)
            col2.markdown(render_fluid_card("市盈率 (估值水位)", f"{pe:.1f}" if pe else "N/A"), unsafe_allow_html=True)
            col3.markdown(render_fluid_card("分红率 (TTM)", f"{info.get('yield', 0)*100:.2f}", "%"), unsafe_allow_html=True)
            col4.markdown(render_fluid_card("资产规模", f"${info.get('totalAssets', 0)/1e9:.1f}B"), unsafe_allow_html=True)
        else:
            col1.markdown(render_fluid_card("护城河深度 (ROE)", f"{roe_pct:.1f}", "%"), unsafe_allow_html=True)
            col2.markdown(render_fluid_card("造血能力 (FCF Yield)", f"{fcf_yield:.1f}", "%"), unsafe_allow_html=True)
            col3.markdown(render_fluid_card("行业定价权 (利润率)", f"{margin_pct:.1f}", "%"), unsafe_allow_html=True)
            col4.markdown(render_fluid_card("情绪钟摆 (PE)", f"{pe:.1f}" if pe else "N/A"), unsafe_allow_html=True)

        st.markdown("### 🌊 长期流体趋势 (5年)")
        if not hist.empty:
            fig = go.Figure(data=go.Scatter(
                x=hist.index, 
                y=hist['Close'],
                mode='lines',
                line=dict(color='#00B4B9', width=3, shape='spline'),
                fill='tozeroy',
                fillcolor='rgba(0, 180, 185, 0.1)'
            ))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False, color="#7B8B9E"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#7B8B9E"),
                height=380,
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
