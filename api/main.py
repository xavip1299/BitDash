# -*- coding: utf-8 -*-
"""
Bitcoin Trading Signals API
Sistema completo de análise técnica e sinais de trading
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import ta
import pytz
import os

app = Flask(__name__)
CORS(app)

# Configurações
COINGECKO_API = 'https://api.coingecko.com/api/v3'
EUR_TIMEZONE = pytz.timezone('Europe/Lisbon')

# Cache simples
cache = {
    'price_data': {'data': None, 'timestamp': 0, 'ttl': 60},
    'technical_analysis': {'data': None, 'timestamp': 0, 'ttl': 180}
}

def get_cached_data(key: str):
    """Retorna dados do cache se ainda válidos"""
    if key in cache:
        data = cache[key]
        if time.time() - data['timestamp'] < data['ttl']:
            return data['data']
    return None

def set_cached_data(key: str, data):
    """Armazena dados no cache"""
    cache[key]['data'] = data
    cache[key]['timestamp'] = time.time()

def get_bitcoin_price_eur():
    """Obter preço atual do Bitcoin em EUR"""
    cached = get_cached_data('price_data')
    if cached:
        return cached
    
    try:
        url = f"{COINGECKO_API}/simple/price"
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'eur',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            btc_data = data.get('bitcoin', {})
            
            price_data = {
                'price': btc_data.get('eur', 0),
                'change_24h': btc_data.get('eur_24h_change', 0),
                'volume_24h': btc_data.get('eur_24h_vol', 0),
                'timestamp': datetime.now(EUR_TIMEZONE).isoformat(),
                'currency': 'EUR'
            }
            
            set_cached_data('price_data', price_data)
            return price_data
    
    except Exception as e:
        print(f"Erro ao obter preço: {e}")
    
    return None

def get_ohlcv_data(days=7):
    """Obter dados OHLCV para análise técnica"""
    try:
        url = f"{COINGECKO_API}/coins/bitcoin/ohlc"
        params = {
            'vs_currency': 'eur',
            'days': str(days)
        }
        
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            
            # Converter para DataFrame
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
    
    except Exception as e:
        print(f"Erro ao obter dados OHLCV: {e}")
    
    return None

def calculate_technical_indicators(df):
    """Calcular indicadores técnicos"""
    if df is None or len(df) < 20:
        return None
    
    try:
        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        
        # MACD
        macd_indicator = ta.trend.MACD(df['close'])
        df['macd'] = macd_indicator.macd()
        df['macd_signal'] = macd_indicator.macd_signal()
        df['macd_histogram'] = macd_indicator.macd_diff()
        
        # Bollinger Bands
        bb_indicator = ta.volatility.BollingerBands(df['close'])
        df['bb_upper'] = bb_indicator.bollinger_hband()
        df['bb_middle'] = bb_indicator.bollinger_mavg()
        df['bb_lower'] = bb_indicator.bollinger_lband()
        
        # Moving Averages
        df['sma_20'] = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
        df['sma_50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
        df['ema_12'] = ta.trend.EMAIndicator(df['close'], window=12).ema_indicator()
        df['ema_26'] = ta.trend.EMAIndicator(df['close'], window=26).ema_indicator()
        
        # Stochastic
        stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        
        return df
    
    except Exception as e:
        print(f"Erro no cálculo de indicadores: {e}")
        return None

def generate_trading_signal(df, current_price):
    """Gerar sinal de trading com score de 0-100"""
    if df is None or len(df) < 2:
        return {
            'signal': 'NEUTRAL',
            'score': 50,
            'stop_loss': None,
            'take_profit': None,
            'reasoning': 'Dados insuficientes'
        }
    
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    
    # Calcular score baseado em múltiplos indicadores
    score = 50  # Neutro
    signals = []
    
    # RSI (30 pontos máximo)
    if not pd.isna(latest['rsi']):
        if latest['rsi'] < 30:
            score += 15
            signals.append("RSI oversold (+15)")
        elif latest['rsi'] > 70:
            score -= 15
            signals.append("RSI overbought (-15)")
        elif latest['rsi'] < 50:
            score += 5
            signals.append("RSI bullish (+5)")
        else:
            score -= 5
            signals.append("RSI bearish (-5)")
    
    # MACD (20 pontos máximo)
    if not pd.isna(latest['macd']) and not pd.isna(latest['macd_signal']):
        if latest['macd'] > latest['macd_signal'] and previous['macd'] <= previous['macd_signal']:
            score += 20
            signals.append("MACD bullish cross (+20)")
        elif latest['macd'] < latest['macd_signal'] and previous['macd'] >= previous['macd_signal']:
            score -= 20
            signals.append("MACD bearish cross (-20)")
        elif latest['macd'] > latest['macd_signal']:
            score += 10
            signals.append("MACD above signal (+10)")
        else:
            score -= 10
            signals.append("MACD below signal (-10)")
    
    # Bollinger Bands (15 pontos máximo)
    if not pd.isna(latest['bb_lower']) and not pd.isna(latest['bb_upper']):
        if current_price <= latest['bb_lower']:
            score += 15
            signals.append("Price at BB lower (+15)")
        elif current_price >= latest['bb_upper']:
            score -= 15
            signals.append("Price at BB upper (-15)")
    
    # Moving Averages (15 pontos máximo)
    if not pd.isna(latest['sma_20']) and not pd.isna(latest['sma_50']):
        if latest['sma_20'] > latest['sma_50']:
            score += 10
            signals.append("SMA20 > SMA50 (+10)")
        else:
            score -= 10
            signals.append("SMA20 < SMA50 (-10)")
    
    # Price vs EMA (10 pontos máximo)
    if not pd.isna(latest['ema_12']):
        if current_price > latest['ema_12']:
            score += 5
            signals.append("Price > EMA12 (+5)")
        else:
            score -= 5
            signals.append("Price < EMA12 (-5)")
    
    # Stochastic (10 pontos máximo)
    if not pd.isna(latest['stoch_k']) and not pd.isna(latest['stoch_d']):
        if latest['stoch_k'] < 20 and latest['stoch_d'] < 20:
            score += 10
            signals.append("Stoch oversold (+10)")
        elif latest['stoch_k'] > 80 and latest['stoch_d'] > 80:
            score -= 10
            signals.append("Stoch overbought (-10)")
    
    # Limitar score entre 0-100
    score = max(0, min(100, score))
    
    # Determinar sinal
    if score >= 70:
        signal_type = 'STRONG_BUY'
        color = '🟢'
    elif score >= 60:
        signal_type = 'BUY'
        color = '🟢'
    elif score >= 40:
        signal_type = 'NEUTRAL'
        color = '🟡'
    elif score >= 30:
        signal_type = 'SELL'
        color = '🔴'
    else:
        signal_type = 'STRONG_SELL'
        color = '🔴'
    
    # Calcular Stop Loss e Take Profit
    volatility = df['close'].pct_change().std() * 100
    
    if score > 50:  # Bullish
        stop_loss = current_price * (1 - volatility * 0.02)
        take_profit = current_price * (1 + volatility * 0.04)
    else:  # Bearish
        stop_loss = current_price * (1 + volatility * 0.02)
        take_profit = current_price * (1 - volatility * 0.04)
    
    return {
        'signal': signal_type,
        'score': round(score, 1),
        'color': color,
        'stop_loss': round(stop_loss, 2),
        'take_profit': round(take_profit, 2),
        'current_price': current_price,
        'reasoning': signals,
        'timestamp': datetime.now(EUR_TIMEZONE).isoformat()
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(EUR_TIMEZONE).isoformat(),
        'service': 'Bitcoin Trading API'
    })

@app.route('/api/bitcoin-price', methods=['GET'])
def get_price():
    """Endpoint para obter preço atual do Bitcoin"""
    price_data = get_bitcoin_price_eur()
    
    if price_data:
        return jsonify({
            'success': True,
            'data': price_data
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Erro ao obter dados de preço'
        }), 500

@app.route('/api/technical-analysis', methods=['GET'])
def get_technical_analysis():
    """Endpoint para análise técnica completa"""
    cached = get_cached_data('technical_analysis')
    if cached:
        return jsonify(cached)
    
    # Obter dados
    df = get_ohlcv_data(days=7)
    price_data = get_bitcoin_price_eur()
    
    if df is None or price_data is None:
        return jsonify({
            'success': False,
            'error': 'Erro ao obter dados para análise'
        }), 500
    
    # Calcular indicadores
    df_with_indicators = calculate_technical_indicators(df)
    
    if df_with_indicators is None:
        return jsonify({
            'success': False,
            'error': 'Erro no cálculo de indicadores'
        }), 500
    
    current_price = price_data['price']
    latest = df_with_indicators.iloc[-1]
    
    analysis = {
        'success': True,
        'data': {
            'current_price': current_price,
            'currency': 'EUR',
            'indicators': {
                'rsi': round(latest['rsi'], 2) if not pd.isna(latest['rsi']) else None,
                'macd': {
                    'macd': round(latest['macd'], 2) if not pd.isna(latest['macd']) else None,
                    'signal': round(latest['macd_signal'], 2) if not pd.isna(latest['macd_signal']) else None,
                    'histogram': round(latest['macd_histogram'], 2) if not pd.isna(latest['macd_histogram']) else None
                },
                'bollinger_bands': {
                    'upper': round(latest['bb_upper'], 2) if not pd.isna(latest['bb_upper']) else None,
                    'middle': round(latest['bb_middle'], 2) if not pd.isna(latest['bb_middle']) else None,
                    'lower': round(latest['bb_lower'], 2) if not pd.isna(latest['bb_lower']) else None
                },
                'moving_averages': {
                    'sma_20': round(latest['sma_20'], 2) if not pd.isna(latest['sma_20']) else None,
                    'sma_50': round(latest['sma_50'], 2) if not pd.isna(latest['sma_50']) else None,
                    'ema_12': round(latest['ema_12'], 2) if not pd.isna(latest['ema_12']) else None,
                    'ema_26': round(latest['ema_26'], 2) if not pd.isna(latest['ema_26']) else None
                },
                'stochastic': {
                    'k': round(latest['stoch_k'], 2) if not pd.isna(latest['stoch_k']) else None,
                    'd': round(latest['stoch_d'], 2) if not pd.isna(latest['stoch_d']) else None
                }
            },
            'timestamp': datetime.now(EUR_TIMEZONE).isoformat()
        }
    }
    
    set_cached_data('technical_analysis', analysis)
    return jsonify(analysis)

@app.route('/api/detailed-signal', methods=['GET'])
def get_detailed_signal():
    """Endpoint principal para sinal completo com score"""
    # Obter dados
    df = get_ohlcv_data(days=7)
    price_data = get_bitcoin_price_eur()
    
    if df is None or price_data is None:
        return jsonify({
            'success': False,
            'error': 'Erro ao obter dados'
        }), 500
    
    # Calcular indicadores
    df_with_indicators = calculate_technical_indicators(df)
    
    if df_with_indicators is None:
        return jsonify({
            'success': False,
            'error': 'Erro no cálculo de indicadores'
        }), 500
    
    # Gerar sinal
    current_price = price_data['price']
    signal = generate_trading_signal(df_with_indicators, current_price)
    
    # Adicionar dados de preço
    signal.update({
        'price_change_24h': price_data['change_24h'],
        'volume_24h': price_data['volume_24h'],
        'currency': 'EUR'
    })
    
    return jsonify({
        'success': True,
        'data': signal
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
