import streamlit as st
import ccxt
import pandas as pd
import ta
import time

st.set_page_config(page_title="Radar 1M - Tiro Supremo", layout="wide")
st.title("🎯 Analista de Mercado 1M - Estratégia Futura")

def calcular_sinal(df):
    ema_fast = ta.trend.ema_indicator(df['close'], window=10)
    avg_range = (df['high'] - df['low']).rolling(20).mean().iloc[-1]
    tendencia_alta = df['close'].iloc[-1] > ema_fast.iloc[-1]
    last_range = df['high'].iloc[-1] - df['low'].iloc[-1]
    is_lateral = last_range < (avg_range * 0.5)
    is_elephant = last_range > (avg_range * 2.2)
    body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
    lower_wick = min(df['open'].iloc[-1], df['close'].iloc[-1]) - df['low'].iloc[-1]
    upper_wick = df['high'].iloc[-1] - max(df['open'].iloc[-1], df['close'].iloc[-1])

    if tendencia_alta and not is_lateral and not is_elephant:
        if lower_wick > body * 1.1:
            return "🔥 CALL (FORTE)", "#00FF00"
    if not tendencia_alta and not is_lateral and not is_elephant:
        if upper_wick > body * 1.1:
            return "❄️ PUT (FORTE)", "#FF0000"
    return "⚠️ AGUARDANDO", "#808080"

def get_data(symbol):
    try:
        exchange = ccxt.binanceusdm()
        symbol_futures = symbol.replace('/USDT', '/USDT:USDT')
        bars = exchange.fetch_ohlcv(symbol_futures, timeframe='1m', limit=50)
        df = pd.DataFrame(bars, columns=['time','open','high','low','close','vol'])
        return df
    except:
        return None

moedas = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']

# PLACEHOLDER garante que o conteúdo aparece antes do rerun
placeholder = st.empty()

with placeholder.container():
    cols = st.columns(4)
    for i, coin in enumerate(moedas):
        with cols[i]:
            dados = get_data(coin)
            if dados is not None:
                status, cor = calcular_sinal(dados)
                preco = dados['close'].iloc[-1]
                st.subheader(f"💰 {coin}")
                st.metric("Preço", f"${preco:,.2f}")
                st.markdown(
                    f"<h2 style='color:{cor};'>{status}</h2>",
                    unsafe_allow_html=True
                )
            else:
                st.error(f"Erro ao carregar {coin}")

time.sleep(10)
st.rerun()
