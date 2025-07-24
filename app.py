import streamlit as st
from signal_generator import generate_signals

st.set_page_config(page_title="Insider Signal Dashboard", layout="wide")

st.title("Trending Insider Signals")

if st.button("Refresh Signals"):
    st.rerun()

signals = generate_signals()

if signals.empty:
    st.error("No signals available. Check data source or network settings.")
else:
    st.dataframe(signals)
    st.download_button("Download CSV", signals.to_csv(index=False), "signals.csv")
    st.download_button("Download JSON", signals.to_json(orient="records"), "signals.json")