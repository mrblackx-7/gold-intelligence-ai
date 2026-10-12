import streamlit as st

st.set_page_config(
    page_title="GOLD INTELLIGENCE AI",
    page_icon="🥇",
    layout="wide"
)

st.title("🥇 GOLD INTELLIGENCE AI")
st.subheader("XAUUSD — Smart Market Analysis")

st.info(
    "Bu tizim bozorni tahlil qilish va qaror qabul qilishga "
    "yordam beradi. Savdolar MT5 da qo'lda ochiladi."
)

st.sidebar.header("⚙️ Analysis Settings")

symbol = st.sidebar.selectbox(
    "Instrument",
    ["XAUUSD — Gold"]
)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["H4", "H1", "M15", "M5"]
)

st.markdown("---")
st.header("📊 Market Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Instrument", "XAUUSD")

with col2:
    st.metric("Selected Timeframe", timeframe)

with col3:
    st.metric("Trading Mode", "Manual")

st.markdown("---")
st.header("📈 Technical Analysis")

st.write("**Bollinger Bands:** 20, 2")
st.write("**MACD:** 12, 26, 9")
st.write("**RSI:** 14")
st.write("**ATR:** 14")
st.write("**SMA:** 200")

st.warning(
    "Market data hali ulanmagan. Hozircha BUY yoki SELL "
    "signali berilmaydi."
)

st.markdown("---")
st.header("🌍 Fundamental Analysis")

st.write("Bu bo'limda keyinchalik quyidagilarni birlashtiramiz:")

st.write("- Federal Reserve (Fed) yangiliklari")
st.write("- CPI va PCE inflyatsiya ma'lumotlari")
st.write("- NFP va ishsizlik statistikasi")
st.write("- AQSh dollari indeksi (DXY)")
st.write("- Forex Factory iqtisodiy kalendari")

st.markdown("---")
st.header("🎯 Trade Setup")

st.info(
    "Signal: NO TRADE\n\n"
    "Sabab: Jonli bozor ma'lumotlari va indikatorlar "
    "hali to'liq ulanmagan."
)

st.caption(
    "GOLD INTELLIGENCE AI | Analysis only — "
    "automatic trading disabled."
)
