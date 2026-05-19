import streamlit as st
import ccxt
import pandas as pd
import ta
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Tiro Supremo - Radar OKX", layout="wide")
st.title("🎯 Tiro Supremo - Analista OKX")

st_autorefresh(interval=30000, key="radar_refresh")

@st.cache_resource
def get_exchange():
    return ccxt.okx({
        "enableRateLimit": True,
        "timeout": 20000,
        "options": {"defaultType": "swap"},
        "verbose": False
    })

def calcular_sinal(df):
    try:
        if len(df) < 22:
            return "⚠️ AGUARDANDO DADOS", "#808080"

        ema_fast = ta.trend.ema_indicator(df['close'], window=10).fillna(0)
        ema_slow = ta.trend.ema_indicator(df['close'], window=21).fillna(0)

        avg_range = (df['high'] - df['low']).rolling(20).mean().iloc[-2]
        if pd.isna(avg_range) or avg_range == 0:
            return "⚠️ AGUARDANDO", "#808080"

        tendencia_alta = df['close'].iloc[-2] > ema_fast.iloc[-2]
        tendencia_macro = ema_fast.iloc[-2] > ema_slow.iloc[-2]

        last_range = df['high'].iloc[-2] - df['low'].iloc[-2]
        is_lateral = last_range < (avg_range * 0.5)
        is_elephant = last_range > (avg_range * 2.2)

        body = abs(df['close'].iloc[-2] - df['open'].iloc[-2])
        lower_wick = min(df['open'].iloc[-2], df['close'].iloc[-2]) - df['low'].iloc[-2]
        upper_wick = df['high'].iloc[-2] - max(df['open'].iloc[-2], df['close'].iloc[-2])

        if tendencia_alta and tendencia_macro and not is_lateral and not is_elephant:
            if body > 0 and lower_wick > body * 1.1:
                return "🔥 CALL (FORTE)", "#00FF00"

        if not tendencia_alta and not tendencia_macro and not is_lateral and not is_elephant:
            if body > 0 and upper_wick > body * 1.1:
                return "❄️ PUT (FORTE)", "#FF0000"

        return "⚠️ AGUARDANDO", "#808080"

    except Exception:
        return "⚠️ ERRO CÁLCULO", "#808080"

def get_data(symbol):
    try:
        exchange = get_exchange()
        bars = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=50)

        if not bars or len(bars) < 50:
            return None

        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        df[['open','high','low','close','vol']] = df[['open','high','low','close','vol']].apply(pd.to_numeric)
        df['timestamp'] = pd.to_datetime(df['time'], unit='ms').dt.strftime('%H:%M')

        return df

    except Exception as e:
        # Blindagem absoluta contra strings nulas
        st.caption(f"Aviso técnico de rede em {str(symbol)}: {repr(e)}")
        return None

def painel():
    moedas = [
        'BTC/USDT:USDT-SWAP',
        'ETH/USDT:USDT-SWAP',
        'SOL/USDT:USDT-SWAP',
        'BNB/USDT:USDT-SWAP'
    ]
    cols = st.columns(4)

    for i, coin in enumerate(moedas):
        with cols[i]:
            dados = get_data(coin)
            nome = str(coin).split('/')[0]

            if dados is not None:
                status, cor = calcular_sinal(dados)
                preco_atual = dados['close'].iloc[-1]
                ultimo_candle = dados['timestamp'].iloc[-2]

                st.subheader(f"💰 {nome}")
                st.metric("Preço", f"${preco_atual:,.2f}")
                st.markdown(
                    f"<div style='background-color:{cor}22; padding:10px; "
                    f"border-radius:5px; text-align:center; border:1px solid {cor};'>"
                    f"<h3 style='color:{cor}; margin:0;'>{status}</h3>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.caption(f"Confirmado às: {ultimo_candle}")
            else:
                st.warning(f"⏳ {nome} — sem resposta da OKX...")

    agora = datetime.now().strftime("%H:%M:%S")
    st.markdown("---")
    st.caption(f"🕐 Última varredura: {agora} · Atualização a cada 30s")

painel()
