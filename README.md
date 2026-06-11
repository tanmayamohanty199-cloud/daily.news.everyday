# GROW // MOVE | Market Intelligence Terminal

A minimal, high-contrast stock visualization and AI intelligence terminal built using **Streamlit**, **Yahoo Finance (yfinance)**, and the **Google Gemini Pro API**.

## Features
- **Dynamic Watchlist:** Add custom domestic (NSE/BSE via `.NS`) or global equity tickers on the fly.
- **Automated AI Briefings:** Leverages `gemini-1.5-flash` to process unstructured financial media feeds into instant institutional-grade sentiment metrics.
- **Minimalist Data Visualization:** Stripped-down interactive high-contrast charts that native-sync with your light/dark system themes.
- **Interactive Deep Research Lab:** Query the AI model on targeted company fundamentals, macro trends, or capital structures.

## Installation & Deployment
1. Clone this repository to your local setup.
2. Ensure you have a `requirements.txt` listing:
   ```text
   streamlit
   yfinance
   google-generativeai
   pandas
   plotly
