import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. SYSTEM CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="GROW // MOVE",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Seamless Dark/Light adaptive styling
st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        .brand-title {
            font-size: 2.8rem;
            font-weight: 900;
            letter-spacing: -1.5px;
            margin-bottom: 0rem;
            text-transform: uppercase;
        }
        .brand-subtitle {
            font-size: 0.95rem;
            color: #888888;
            margin-bottom: 2.5rem;
            text-transform: uppercase;
            letter-spacing: 3px;
        }
        .news-card {
            border: 1px solid #e0e0e0;
            padding: 1.2rem;
            border-radius: 4px;
            margin-bottom: 0.8rem;
            background-color: transparent;
        }
        @media (prefers-color-scheme: dark) {
            .news-card { border: 1px solid #262626; }
        }
    </style>
""", unsafe_allow_html=True)

# Securely fetch API key from Streamlit Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# ==========================================
# 2. SIDEBAR & WATCHLIST MANAGEMENT
# ==========================================
st.sidebar.markdown("# GROW // MOVE")
st.sidebar.markdown("### TERMINAL v1.0")
st.sidebar.write("---")

# Default core watchlist (Supports Indian & Global tickers)
default_tickers = ["SUZLON.NS", "JIOFIN.NS", "TATAPOWER.NS", "AAPL"]

custom_ticker = st.sidebar.text_input("➕ ADD TICKER TO WISHLIST:", "").upper().strip()
if custom_ticker and custom_ticker not in default_tickers:
    default_tickers.append(custom_ticker)

wishlist = st.sidebar.multiselect(
    "ACTIVE WATCHLIST:",
    options=default_tickers,
    default=default_tickers[:3]
)

st.sidebar.write("---")
st.sidebar.caption("Status: Connected to Cloud Terminal")
if GEMINI_API_KEY:
    st.sidebar.success("Gemini Engine: ACTIVE")
else:
    st.sidebar.error("Gemini Engine: KEY MISSING IN SECRETS")

# ==========================================
# 3. CORE ENGINES (DATA & AI)
# ==========================================
@st.cache_data(ttl=1800)  # Cache data for 30 minutes to optimize speed
def fetch_market_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="6mo")
        info = ticker.info
        news = ticker.news
        return hist, info, news
    except:
        return None, None, None

def generate_ai_intelligence(ticker, news_list):
    if not GEMINI_API_KEY:
        return "⚠️ Configure `GEMINI_API_KEY` in your Streamlit Advanced Secrets to enable live AI briefings."
    if not news_list:
        return "No recent media coverage found for this asset to analyze."
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        context = ""
        for item in news_list[:5]:
            context += f"- Title: {item.get('title')}\n  Publisher: {item.get('publisher')}\n\n"
            
        prompt = f"""
        You are a senior institutional equity research analyst. Analyze the recent headlines for ticker {ticker}:
        {context}
        
        Provide a sharp, definitive assessment. Break it down strictly into:
        1. SENTIMENT: (Bullish / Bearish / Neutral) with a 1-sentence core reason.
        2. CATALYSTS: Point out any underlying drivers (e.g., order books, macro shifts, management, or institutional volumes).
        Keep the prose raw, high-density, and professional. No conversational filler.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Intelligence Engine Error: {str(e)}"

def run_deep_research(ticker, query, info_dict):
    if not GEMINI_API_KEY:
        return "Please connect your API key."
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        m_cap = info_dict.get('marketCap', 'N/A')
        pe = info_dict.get('trailingPE', 'N/A')
        forward_pe = info_dict.get('forwardPE', 'N/A')
        
        prompt = f"""
        Context: Analyzing equity asset {ticker}. Market Cap: {m_cap}, Trailing P/E: {pe}, Forward P/E: {forward_pe}.
        User Inquiry: {query}
        
        Task: Provide an objective, fundamentals-driven analysis answering the inquiry. Look for operational risk, competitive moats, valuation sanity, and institutional alignment.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Research Lab Error: {str(e)}"

# ==========================================
# 4. INTERFACE DISPLAY
# ==========================================
st.markdown('<div class="brand-title">GROW // MOVE</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">Automated Stock Intelligence & Research Terminal</div>', unsafe_allow_html=True)

if not wishlist:
    st.info("Select or add ticker symbols in the sidebar to populate the terminal.")
else:
    tab_feed, tab_charts, tab_lab = st.tabs([
        "📡 AUTOMATED BRIEFING", 
        "📊 VISUAL INTERFACE", 
        "🧠 AI RESEARCH LAB"
    ])

    # TAB 1: AUTOMATED BRIEFING (HOMEPAGE)
    with tab_feed:
        st.markdown("### LIVE MARKET SATELLITE")
        for stock in wishlist:
            with st.expander(f"⚡ {stock} // INTELLIGENCE STREAM", expanded=True):
                hist, info, news = fetch_market_data(stock)
                
                c1, c2 = st.columns([5, 3])
                with c1:
                    st.caption("AI EVALUATION")
                    briefing = generate_ai_intelligence(stock, news)
                    st.write(briefing)
                with c2:
                    st.caption("RAW LOGS")
                    if news:
                        for item in news[:2]:
                            st.markdown(f"""
                            <div class="news-card">
                                <small style="color:#888;">{item.get('publisher')}</small><br>
                                <a href="{item.get('link')}" target="_blank" style="color:inherit; font-weight:600; text-decoration:none;">{item.get('title')}</a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("No raw feeds found.")

    # TAB 2: VISUAL INTERFACE (CHARTS)
    with tab_charts:
        target_stock = st.selectbox("CHOOSE VISUAL TARGET:", wishlist)
        if target_stock:
            hist, info, news = fetch_market_data(target_stock)
            if hist is not None and not hist.empty:
                # Top Metrics Strip
                m1, m2, m3, m4 = st.columns(4)
                cur = info.get('currency', 'INR')
                live_p = info.get('currentPrice', info.get('regularMarketPrice', hist['Close'].iloc[-1]))
                prev_c = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else live_p)
                delta = live_p - prev_c
                delta_pct = (delta / prev_c) * 100
                
                m1.metric("LAST PRICE", f"{live_p:,.2f} {cur}", f"{delta:+.2f} ({delta_pct:+.2f}%)")
                m2.metric("MARKET CAP", f"{info.get('marketCap', 0):,}")
                m3.metric("P/E RATIO", f"{info.get('trailingPE', 'N/A')}")
                m4.metric("52W HIGH", f"{info.get('fiftyTwoWeekHigh', 0):,.2f}")
                
                # Plotly Chart Minimalist configuration
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close', line=dict(color='#000000' if st.get_option("theme.base") != "dark" else '#FFFFFF', width=1.5)))
                fig.update_layout(
                    template="plotly_white" if st.get_option("theme.base") != "dark" else "plotly_dark",
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=400,
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#f0f0f0' if st.get_option("theme.base") != "dark" else '#1f1f1f')
                )
                st.plotly_chart(fig, use_container_width=True)

    # TAB 3: AI RESEARCH LAB
    with tab_lab:
        lab_target = st.selectbox("SELECT LAB TARGET:", wishlist, key="lab_select")
        query = st.text_input("INTERROGATION QUERY:", placeholder="Analyze the fundamental strength or recent order volume impacts...")
        if st.button("RUN DEEP ANALYTICS", type="primary"):
            if query:
                _, info, _ = fetch_market_data(lab_target)
                with st.spinner("Processing deep financial modeling..."):
                    result = run_deep_research(lab_target, query, info)
                    st.markdown("---")
                    st.markdown(f"#### ARCHIVE REPORT // {lab_target}")
                    st.write(result)
