import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="GOLD INTELLIGENCE AI",
    page_icon="🥇",
    layout="wide"
)

st.title("🥇 GOLD INTELLIGENCE AI")
st.subheader("XAUUSD | Smart Market Analysis")

st.info(
    "Bu tizim tahlil va qaror qabul qilish uchun yordam beradi. "
    "Savdolar MT5 da qo'lda ochiladi. "
    "Hozircha avtomatik savdo hamda real vaqt ma'lumotlari ulanmagan."
)

# SIDEBAR
st.sidebar.header("⚙️ Analysis Settings")

symbol = st.sidebar.selectbox(
    "Instrument",
    ["XAUUSD — Gold"]
)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["H4", "H1", "M15", "M5"]
)

st.sidebar.caption(
    "Indikatorlar: BB 20,2 | MACD 12,26,9 | RSI 14 | ATR 14 | SMA 200"
)

# RISK MANAGEMENT
st.sidebar.header("🛡️ Risk Management")

balance = st.sidebar.number_input(
    "Account balance ($)",
    min_value=1.0,
    value=50.0,
    step=5.0
)

risk_percent = st.sidebar.slider(
    "Risk per trade (%)",
    min_value=0.25,
    max_value=2.0,
    value=0.5,
    step=0.25
)

risk_amount = balance * risk_percent / 100

st.sidebar.metric(
    "Planned risk",
    f"${risk_amount:.2f}"
)

# DATA INPUT
st.header("📊 Market Data")

st.write(
    "MT5 dan eksport qilingan OHLC CSV faylini yuklang. "
    "Faylda kamida quyidagi ustunlar bo'lishi kerak: "
    "open, high, low, close. Timestamp ixtiyoriy."
)

uploaded_file = st.file_uploader(
    "Upload XAUUSD CSV",
    type=["csv"]
)

# INDICATORS
def calculate_indicators(data):
    data = data.copy()

    for col in ["open", "high", "low", "close"]:
        data[col] = pd.to_numeric(
            data[col], errors="coerce"
        )

    data = data.dropna(
        subset=["open", "high", "low", "close"]
    )

    if len(data) < 30:
        raise ValueError(
            "Kamida 30 ta sham kerak. SMA200 uchun 200+ sham tavsiya etiladi."
        )

    close = data["close"]

    # Bollinger Bands (20,2)
    data["BB_MID"] = close.rolling(20).mean()
    std = close.rolling(20).std(ddof=0)

    data["BB_UPPER"] = data["BB_MID"] + 2 * std
    data["BB_LOWER"] = data["BB_MID"] - 2 * std

    # MACD (12,26,9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()

    data["MACD"] = ema12 - ema26
    data["MACD_SIGNAL"] = data["MACD"].ewm(
        span=9, adjust=False
    ).mean()

    data["MACD_HIST"] = (
        data["MACD"] - data["MACD_SIGNAL"]
    )

    # RSI (14), Wilder smoothing
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1/14, min_periods=14, adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1/14, min_periods=14, adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    data["RSI"] = 100 - (100 / (1 + rs))

    data.loc[
        (avg_loss == 0) & (avg_gain > 0), "RSI"
    ] = 100

    data.loc[
        (avg_gain == 0) & (avg_loss > 0), "RSI"
    ] = 0

    data.loc[
        (avg_gain == 0) & (avg_loss == 0), "RSI"
    ] = 50

    # ATR (14)
    prev_close = close.shift(1)

    tr = pd.concat(
        [
            data["high"] - data["low"],
            (data["high"] - prev_close).abs(),
            (data["low"] - prev_close).abs()
        ],
        axis=1
    ).max(axis=1)

    data["ATR"] = tr.ewm(
        alpha=1/14, min_periods=14, adjust=False
    ).mean()

    # SMA 200
    data["SMA200"] = close.rolling(200).mean()

    return data


if uploaded_file is None:
    st.warning(
        "⚠️ Hozircha bozor ma'lumotlari yuklanmagan. "
        "Shuning uchun tizim haqiqiy BUY yoki SELL signalini bermaydi."
    )

    st.subheader("🌍 Fundamental Analysis")

    st.write(
        "Quyidagi omillarni keyingi versiyada ma'lumot manbalari "
        "orqali integratsiya qilamiz:"
    )

    st.markdown(
        """
        - Federal Reserve (Fed) qarorlari
        - CPI va PCE inflyatsiyasi
        - NFP va ishsizlik statistikasi
        - AQSh dollari indeksi (DXY)
        - AQSh obligatsiyalari daromadliligi
        - Forex Factory iqtisodiy kalendari
        - Geosiyosiy xavflar
        """
    )

    st.info(
        "Signal: NO TRADE — ma'lumot yo'q. "
        "Bu bozor yo'nalishi aniqlanganini anglatmaydi."
    )

else:
    try:
        raw = pd.read_csv(uploaded_file)

        raw.columns = [
            str(c).strip().lower() for c in raw.columns
        ]

        required = ["open", "high", "low", "close"]

        missing = [
            col for col in required if col not in raw.columns
        ]

        if missing:
            st.error(
                "CSV faylda quyidagi ustunlar yetishmayapti: "
                + ", ".join(missing)
            )
            st.stop()

        if "timestamp" in raw.columns:
            raw["timestamp"] = pd.to_datetime(
                raw["timestamp"], errors="coerce"
            )
            raw = raw.sort_values("timestamp")

        elif "time" in raw.columns:
            raw["time"] = pd.to_datetime(
                raw["time"], errors="coerce"
            )
            raw = raw.sort_values("time")

        data = calculate_indicators(raw)

        last = data.iloc[-1]
        previous = data.iloc[-2]

        if data[["BB_MID", "MACD", "MACD_SIGNAL",
                 "RSI", "ATR"]].iloc[-1].isna().any():
            st.error(
                "Indikatorlar uchun ma'lumot yetarli emas."
            )
            st.stop()

        price = float(last["close"])
        macd = float(last["MACD"])
        macd_signal = float(last["MACD_SIGNAL"])
        rsi = float(last["RSI"])
        atr = float(last["ATR"])

        # TREND
        if price > last["BB_MID"]:
            bb_trend = "BUY tomonga"
        else:
            bb_trend = "SELL tomonga"

        macd_bull = macd > macd_signal
        rsi_ok_buy = 50 <= rsi < 70
        rsi_ok_sell = 30 < rsi <= 50

        # Breakout confirmation
        buy_breakout = (
            price > last["BB_UPPER"]
            and previous["close"] <= previous["BB_UPPER"]
        )

        sell_breakout = (
            price < last["BB_LOWER"]
            and previous["close"] >= previous["BB_LOWER"]
        )

        # SIGNAL: confirmed close outside band
        signal = "NO TRADE"
        reasons = []

        if (
            buy_breakout
            and macd_bull
            and rsi_ok_buy
        ):
            signal = "BUY SETUP"
            reasons.append(
                "Yuqori Bollinger chizig'idan breakout tasdiqlandi."
            )
            reasons.append(
                "MACD bullish va RSI 50–70 oralig'ida."
            )

        elif (
            sell_breakout
            and not macd_bull
            and rsi_ok_sell
        ):
            signal = "SELL SETUP"
            reasons.append(
                "Quyi Bollinger chizig'idan breakout tasdiqlandi."
            )
            reasons.append(
                "MACD bearish va RSI 30–50 oralig'ida."
            )

        else:
            reasons.append(
                "Breakout va indikatorlar shartlari birgalikda bajarilmadi."
            )

        # DASHBOARD
        st.header("📈 Market Overview")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Latest close", f"{price:.2f}")
        c2.metric("RSI (14)", f"{rsi:.2f}")
        c3.metric("MACD", f"{macd:.3f}")
        c4.metric("ATR (14)", f"{atr:.3f}")

        st.write(f"**Instrument:** {symbol}")
        st.write(f"**Selected timeframe:** {timeframe}")
        st.write(f"**Bollinger context:** {bb_trend}")

        st.subheader("🎯 Trade Setup")

        if signal == "BUY SETUP":
            st.success("BUY SETUP — tekshirish uchun nomzod")

        elif signal == "SELL SETUP":
            st.error("SELL SETUP — tekshirish uchun nomzod")

        else:
            st.info("NO TRADE — hozircha tasdiqlangan setup yo'q")

        for reason in reasons:
            st.write("• " + reason)

        st.warning(
            "Bu dastlabki texnik filtr, foyda kafolati emas. "
            "Breakout fake bo'lishi mumkin. "
            "Signal real vaqt narxi yoki fundamental tahlil bilan "
            "hali tasdiqlanmagan."
        )

        # SUPPORT / RESISTANCE
        st.subheader("📍 Support & Resistance")

        support = float(data["low"].tail(20).min())
        resistance = float(data["high"].tail(20).max())

        c1, c2 = st.columns(2)
        c1.metric("Approx. Support", f"{support:.2f}")
        c2.metric("Approx. Resistance", f"{resistance:.2f}")

        # RISK CALCULATOR
        st.subheader("🛡️ Risk Calculator")

        stop_distance = st.number_input(
            "Stop-loss distance (price units)",
            min_value=0.01,
            value=max(round(atr, 2), 0.01),
            step=0.1
        )

        st.write(f"**Planned risk:** ${risk_amount:.2f}")

        st.write(
            f"**SL distance:** {stop_distance:.2f} price units"
        )

        st.write(
            "Lot hajmini hisoblash uchun brokerning XAUUSD "
            "contract size, tick value, minimal lot va lot step "
            "parametrlari kerak. Ular ulanmagani sababli lot "
            "hajmi avtomatik tavsiya qilinmaydi."
        )

        # CHART
        st.subheader("📉 Price & Bollinger Bands")

        chart = data.tail(150)

        chart_columns = [
            "close", "BB_UPPER", "BB_MID", "BB_LOWER"
        ]

        st.line_chart(chart[chart_columns])

        st.subheader("📋 Recent Indicator Data")

        st.dataframe(
            data.tail(10).iloc[::-1],
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Ma'lumotni qayta ishlashda xato: {e}")

st.divider()

st.caption(
    "GOLD INTELLIGENCE AI | Analysis only | "
    "Automatic trading disabled | Educational use"
)
