import streamlit as st
import ccxt
import pandas as pd
import ta
from datetime import datetime

st.set_page_config(page_title="Radar 1M - Tiro Supremo", layout="wide")
st.title("🎯 Analista de Mercado 1M - Estratégia Futura")

@st.cache_resource
def get_exchange():
    exchange = ccxt.bybit({        # ← BYBIT (sem bloqueio geo)
        "enableRateLimit": True,
        "timeout": 10000,
    })
    return exchange

def calcular_sinal(df):
    ema_fast = ta.trend.ema_indicator(df['close'], window=10)
    ema_slow = ta.trend.ema_indicator(df['close'], window=21)

    avg_range = (df['high'] - df['low']).rolling(20).mean().iloc[-2]

    tendencia_alta = df['close'].iloc[-2] > ema_fast.iloc[-2]
    tendencia_macro = ema_fast.iloc[-2] > ema_slow.iloc[-2]

    last_range = df['high'].iloc[-2] - df['low'].iloc[-2]
    is_lateral = last_range < (avg_range * 0.5)
    is_elephant = last_range > (avg_range * 2.2)

    body = abs(df['close'].iloc[-2] - df['open'].iloc[-2])
    lower_wick = min(df['open'].iloc[-2], df['close'].iloc[-2]) - df['low'].iloc[-2]
    upper_wick = df['high'].iloc[-2] - max(df['open'].iloc[-2], df['close'].iloc[-2])

    if tendencia_alta and tendencia_macro and not is_lateral and not is_elephant:
        if lower_wick > body * 1.1:
            return "🔥 CALL (FORTE)", "#00FF00"

    if not tendencia_alta and not tendencia_macro and not is_lateral and not is_elephant:
        if upper_wick > body * 1.1:
            return "❄️ PUT (FORTE)", "#FF0000"

    return "⚠️ AGUARDANDO", "#808080"

def get_data(symbol):
    try:
        exchange = get_exchange()
        bars = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=50)

        if not bars or len(bars) < 50:
            return None

        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        df['timestamp'] = pd.to_datetime(df['time'], unit='ms').dt.strftime('%H:%M')

        return df

    except Exception as e:
        st.warning(f"⚠️ {symbol} — {e}")
        return None

@st.fragment(run_every="30s")
def painel():
    moedas = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
    cols = st.columns(4)

    for i, coin in enumerate(moedas):
        with cols[i]:
            dados = get_data(coin)
            if dados is not None:
                status, cor = calcular_sinal(dados)
                preco_atual = dados['close'].iloc[-1]
                ultimo_candle = dados['timestamp'].iloc[-2]

                st.subheader(f"💰 {coin}")
                st.metric("Preço", f"${preco_atual:,.2f}")
                st.markdown(
                    f"<h2 style='color:{cor};'>{status}</h2>",
                    unsafe_allow_html=True
                )
                st.caption(f"Candle fechado: {ultimo_candle}")
            else:
                st.warning(f"⏳ {coin} — aguardando dados...")

    agora = datetime.now().strftime("%H:%M:%S")
    st.caption(f"🕐 Última atualização: {agora} · Próxima em 30s")

painel()
