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

# Custom High-Contrast UI styling
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

# Pull API key silently from Streamlit Secrets 
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# ==========================================
# 2. SIDEBAR & WATCHLIST SYSTEM
# ==========================================
st.sidebar.markdown("# GROW // MOVE")
st.sidebar.markdown("### TERMINAL v1.2")
st.sidebar.write("---")

# Default Indian and Global equities
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
st.sidebar.caption("System Status: Cloud Engine Active")
if GEMINI_API_KEY:
    st.sidebar.success("Gemini Engine: ONLINE")
else:
    st.sidebar.error("Gemini Engine: KEY MISSING IN SECRETS")

# ==========================================
# 3. CORE PROCESSING ENGINES
# ==========================================
@st.cache_data(ttl=1800)  # Caches market numbers for 30 mins
def fetch_market_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="6mo")
        info = ticker.info
        news = ticker.news
        return hist, info, news
    except Exception:
        return None, None, None

@st.cache_data(ttl=1800)  # NEW: Caches the AI output so it stops triggering 429 limits
def generate_ai_intelligence(ticker, news_list, info_dict, hist_df):
    if not GEMINI_API_KEY:
        return "⚠️ Configure `GEMINI_API_KEY` in your Streamlit Advanced Secrets to see live AI briefings."
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # PATH A: News is available
        if news_list and len(news_list) > 0:
            context = ""
            for item in news_list[:5]:
                context += f"- Title: {item.get('title')}\n  Publisher: {item.get('publisher')}\n\n"
                
            prompt = f"""
            You are an elite institutional stock research analyst. Analyze the recent headlines for ticker {ticker}:
            {context}
            
            Provide a sharp assessment broken down into:
            1. SENTIMENT: (Bullish / Bearish / Neutral) with a clear 1-sentence reasoning.
            2. KEY CATALYSTS: Focus strictly on fundamentals (order volumes, capacity, institutional movements, or macro changes).
            Keep it direct, punchy, and professional. Avoid conversational fluff.
            """
        
        # PATH B: News feed is down -> Technical & Fundamental Fallback
        else:
            m_cap = info_dict.get('marketCap', 'N/A') if info_dict else 'N/A'
            pe = info_dict.get('trailingPE', 'N/A') if info_dict else 'N/A'
            live_price = info_dict.get('currentPrice', 'N/A') if info_dict else 'N/A'
            
            if hist_df is not None and not hist_df.empty and len(hist_df) > 10:
                recent_close = hist_df['Close'].iloc[-1]
                prev_close_10d = hist_df['Close'].iloc[-10]
                price_change = ((recent_close - prev_close_10d) / prev_close_10d) * 100
                trend_str = f"{price_change:+.2f}% over the last 10 trading sessions"
                if live_price == 'N/A':
                    live_price = round(recent_close, 2)
            else:
                trend_str = "Data insufficient to map short-term directional trends."

            prompt = f"""
            You are an elite institutional equity researcher. No recent media articles were indexed for ticker {ticker}.
            Generate a pure market footprint data briefing instead using these parameters:
            - Current Spot Price: {live_price}
            - 10-Day Trajectory: {trend_str}
            - Market Cap Structure: {m_cap}
            - Valuation Multiple (P/E): {pe}
            
            Provide an analytical assessment structured exactly as:
            1. MARKET FOOTPRINT: Note whether this exhibits high-velocity momentum or structural stabilization, backing it with the valuation multiple or trend data listed above.
            2. INSTITUTIONAL PERSPECTIVE: Outline what an investor tracking order books, defense/infrastructure tailwinds, or large-scale promoter stakes should watch for under these pricing parameters.
            Keep it high-density and institutional. No generic filler words.
            """
            
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Intelligence Engine Error: {str(e)}"

def run_deep_research(ticker, query, info_dict):
    if not GEMINI_API_KEY:
        return "Please connect your API key via Secrets."
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        m_cap = info_dict.get('marketCap', 'N/A')
        pe = info_dict.get('trailingPE', 'N/A')
        forward_pe = info_dict.get('forwardPE', 'N/A')
        
        prompt = f"""
        Context: Analyzing equity asset {ticker}. Market Cap: {m_cap}, Trailing P/E: {pe}, Forward P/E: {forward_pe}.
        User Inquiry: {query}
        
        Task: Provide an analytical, data-driven report answering the inquiry. Scan for risk factors, valuation sanity, operational shifts, or structural market moats.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Research Lab Error: {str(e)}"

# ==========================================
# 4. INTERFACE ARCHITECTURE
# ==========================================
st.markdown('<div class="brand-title">GROW // MOVE</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">Automated Stock Intelligence & Research Terminal</div>', unsafe_allow_html=True)

if not wishlist:
    st.info("Add or select ticker symbols in the sidebar to populate the terminal panels.")
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
                    st.caption("AI BRIEFING & EVALUATION")
                    briefing = generate_ai_intelligence(stock, news, info, hist)
                    st.write(briefing)
                with c2:
                    st.caption("RAW MEDIA FEEDS")
                    if news and len(news) > 0:
                        for item in news[:2]:
                            st.markdown(f"""
                            <div class="news-card">
                                <small style="color:#888;">{item.get('publisher')}</small><br>
                                <a href="{item.get('link')}" target="_blank" style="color:inherit; font-weight:600; text-decoration:none;">{item.get('title')}</a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Yahoo media scraper returned empty index logs for this ticker. AI data briefing active on the left.")

    # TAB 2: VISUAL INTERFACE (CHARTS & METRICS)
    with tab_charts:
        target_stock = st.selectbox("CHOOSE VISUAL TARGET:", wishlist)
        if target_stock:
            hist, info, news = fetch_market_data(target_stock)
            if hist is not None and not hist.empty:
                m1, m2, m3, m4 = st.columns(4)
                cur = info.get('currency', 'INR') if info else 'INR'
                
                live_p = info.get('currentPrice', info.get('regularMarketPrice', hist['Close'].iloc[-1])) if info else hist['Close'].iloc[-1]
                prev_c = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else live_p) if info else hist['Close'].iloc[-2]
                delta = live_p - prev_c
                delta_pct = (delta / prev_c) * 100
                
                m1.metric("LAST PRICE", f"{live_p:,.2f} {cur}", f"{delta:+.2f} ({delta_pct:+.2f}%)")
                m2.metric("MARKET CAP", f"{info.get('marketCap', 0):,}" if info else "N/A")
                m3.metric("P/E RATIO", f"{info.get('trailingPE', 'N/A')}" if info else "N/A")
                m4.metric("52W HIGH", f"{info.get('fiftyTwoWeekHigh', 0):,.2f}" if info else "N/A")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist.index, 
                    y=hist['Close'], 
                    mode='lines', 
                    name='Close Price',
                    line=dict(color='#000000' if st.get_option("theme.base") != "dark" else '#FFFFFF', width=1.5)
                ))
                fig.update_layout(
                    template="plotly_white" if st.get_option("theme.base") != "dark" else "plotly_dark",
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=450,
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#f0f0f0' if st.get_option("theme.base") != "dark" else '#1f1f1f')
                )
                st.plotly_chart(fig, use_container_width=True)

    # TAB 3: AI RESEARCH LAB
    with tab_lab:
        lab_target = st.selectbox("SELECT LAB TARGET:", wishlist, key="lab_select")
        query = st.text_input("INTERROGATION QUERY:", placeholder="e.g., Analyze the fundamental strength or recent order volume impacts...")
        if st.button("RUN DEEP ANALYTICS", type="primary"):
            if query:
                _, info, _ = fetch_market_data(lab_target)
                with st.spinner("Processing deep financial modeling vectors..."):
                    result = run_deep_research(lab_target, query, info if info else {})
                    st.markdown("---")
                    st.markdown(f"#### ARCHIVE REPORT // {lab_target}")
                    st.write(result)
