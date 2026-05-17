import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Radar 1M - Tiro Supremo", layout="wide")
st.title("🎯 Analista de Mercado 1M - Estratégia Futura")

# 5 CONDIÇÕES DE OURO (SISTEMA DE SCORE)
def calcular_sinal(df):
    ema_fast = ta.ema(df['close'], length=10)
    ema_slow = ta.ema(df['close'], length=21)
    avg_range = (df['high'] - df['low']).rolling(20).mean().iloc[-1]
    
    # 1. TENDÊNCIA
    tendencia_alta = df['close'].iloc[-1] > ema_fast.iloc[-1]
    
    # 2. LATERALIDADE (Filtro de Volatilidade)
    last_range = df['high'].iloc[-1] - df['low'].iloc[-1]
    is_lateral = last_range < (avg_range * 0.5)

    # 3. VELA ELEFANTE (Exaustão)
    is_elephant = last_range > (avg_range * 2.2)

    # 4. REJEIÇÃO DE PAVIO (Força de Reversão)
    body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
    lower_wick = min(df['open'].iloc[-1], df['close'].iloc[-1]) - df['low'].iloc[-1]
    upper_wick = df['high'].iloc[-1] - max(df['open'].iloc[-1], df['close'].iloc[-1])

    # LÓGICA DE DECISÃO
    if tendencia_alta and not is_lateral and not is_elephant:
        if lower_wick > body * 1.1:
            return "🔥 CALL (FORTE)", "#00FF00"
    
    if not tendencia_alta and not is_lateral and not is_elephant:
        if upper_wick > body * 1.1:
            return "❄️ PUT (FORTE)", "#FF0000"

    return "⚠️ AGUARDANDO", "#808080"

# CONEXÃO BINANCE
def get_data(symbol):
    exchange = ccxt.binance()
    bars = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=50)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
    return df

# PAINEL DE MONITORAMENTO
moedas = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
cols = st.columns(4)

for i, coin in enumerate(moedas):
    with cols[i]:
        try:
            dados = get_data(coin)
            sinal, cor = calcular_sinal(dados)
            st.metric(label=coin, value=f"{dados['close'].iloc[-1]:.2f}")
            st.markdown(f"<div style='background-color:{cor}; padding:10px; border-radius:5px; text-align:center; color:white; font-weight:bold;'>{sinal}</div>", unsafe_allow_html=True)
        except:
            st.error(f"Erro em {coin}")

st.divider()
st.caption("Estratégia Tiro Supremo configurada para 1M na Corretora Futura.")
