# -*- coding: utf-8 -*-
"""
Bitcoin Trading Signals API - Versão Simplificada
Sistema básico sem dependências pesadas (numpy, pandas, ta-lib)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
import time
import os
import random
import math

app = Flask(__name__)
CORS(app)

# Configurações
COINGECKO_API = 'https://api.coingecko.com/api/v3'

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
    """Obter preço atual do Bitcoin em EUR - Versão Simplificada"""
    cached = get_cached_data('price_data')
    if cached:
        return cached
    
    try:
        # CoinGecko API para preço atual
        url = f"{COINGECKO_API}/simple/price"
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'eur,usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'bitcoin' not in data:
            raise ValueError("Bitcoin data not found in response")
        
        bitcoin_data = data['bitcoin']
        
        result = {
            'price_eur': bitcoin_data.get('eur', 0),
            'price_usd': bitcoin_data.get('usd', 0),
            'change_24h': bitcoin_data.get('eur_24h_change', 0),
            'market_cap_eur': bitcoin_data.get('eur_market_cap', 0),
            'volume_24h_eur': bitcoin_data.get('eur_24h_vol', 0),
            'timestamp': datetime.now().isoformat(),
            'source': 'coingecko'
        }
        
        set_cached_data('price_data', result)
        return result
        
    except Exception as e:
        # Dados de fallback em caso de erro
        return {
            'price_eur': 85000.0,
            'price_usd': 92000.0,
            'change_24h': 0.0,
            'market_cap_eur': 1650000000000,
            'volume_24h_eur': 25000000000,
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback',
            'error': str(e)
        }

def calculate_simple_rsi(prices, period=14):
    """Calcular RSI simples sem pandas"""
    if len(prices) < period + 1:
        return 50.0  # Valor neutro se não há dados suficientes
    
    # Calcular mudanças de preço
    changes = []
    for i in range(1, len(prices)):
        changes.append(prices[i] - prices[i-1])
    
    # Separar ganhos e perdas
    gains = [max(0, change) for change in changes[-period:]]
    losses = [abs(min(0, change)) for change in changes[-period:]]
    
    # Calcular médias
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0.01  # Evitar divisão por zero
    
    # Calcular RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)

def get_historical_prices(days=30):
    """Obter preços históricos - Versão Simplificada"""
    try:
        url = f"{COINGECKO_API}/coins/bitcoin/market_chart"
        params = {
            'vs_currency': 'eur',
            'days': days,
            'interval': 'daily'
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Extrair apenas os preços
        prices = [price[1] for price in data['prices']]
        return prices
        
    except Exception as e:
        # Gerar dados simulados em caso de erro
        base_price = 85000
        prices = []
        for i in range(days):
            # Simulação simples de movimento de preços
            change = random.uniform(-0.05, 0.05)  # ±5% de mudança
            base_price *= (1 + change)
            prices.append(base_price)
        return prices

def generate_simple_signal(current_price, historical_prices):
    """Gerar sinal simples sem bibliotecas complexas"""
    try:
        # Calcular indicadores básicos
        rsi = calculate_simple_rsi(historical_prices)
        
        # Calcular médias móveis simples
        sma_20 = sum(historical_prices[-20:]) / 20 if len(historical_prices) >= 20 else current_price
        sma_50 = sum(historical_prices[-50:]) / 50 if len(historical_prices) >= 50 else current_price
        
        # Lógica de sinal simples
        signal_score = 50  # Neutro
        signal_type = "HOLD"
        confidence = "MEDIUM"
        
        # Análise RSI
        if rsi < 30:
            signal_score += 20  # Oversold - sinal de compra
        elif rsi > 70:
            signal_score -= 20  # Overbought - sinal de venda
        
        # Análise de médias móveis
        if current_price > sma_20 > sma_50:
            signal_score += 15  # Tendência de alta
        elif current_price < sma_20 < sma_50:
            signal_score -= 15  # Tendência de baixa
        
        # Análise de momentum (últimos 7 dias)
        if len(historical_prices) >= 7:
            recent_change = (historical_prices[-1] - historical_prices[-7]) / historical_prices[-7]
            if recent_change > 0.1:  # +10%
                signal_score += 10
            elif recent_change < -0.1:  # -10%
                signal_score -= 10
        
        # Determinar tipo de sinal
        if signal_score >= 70:
            signal_type = "BUY"
            confidence = "HIGH"
        elif signal_score >= 60:
            signal_type = "BUY"
            confidence = "MEDIUM"
        elif signal_score <= 30:
            signal_type = "SELL"
            confidence = "HIGH"
        elif signal_score <= 40:
            signal_type = "SELL"
            confidence = "MEDIUM"
        
        # Calcular Stop Loss e Take Profit
        if signal_type == "BUY":
            stop_loss = current_price * 0.95  # -5%
            take_profit = current_price * 1.10  # +10%
        elif signal_type == "SELL":
            stop_loss = current_price * 1.05  # +5%
            take_profit = current_price * 0.90  # -10%
        else:  # HOLD
            stop_loss = current_price * 0.97  # -3%
            take_profit = current_price * 1.05  # +5%
        
        return {
            'signal': signal_type,
            'score': max(0, min(100, signal_score)),  # Manter entre 0-100
            'current_price': current_price,
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'confidence': confidence,
            'indicators': {
                'rsi': rsi,
                'rsi_signal': 'OVERSOLD' if rsi < 30 else 'OVERBOUGHT' if rsi > 70 else 'NEUTRAL',
                'sma_20': round(sma_20, 2),
                'sma_50': round(sma_50, 2),
                'trend': 'UPTREND' if current_price > sma_20 > sma_50 else 'DOWNTREND' if current_price < sma_20 < sma_50 else 'SIDEWAYS'
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        # Sinal básico em caso de erro
        return {
            'signal': 'HOLD',
            'score': 50,
            'current_price': current_price,
            'stop_loss': round(current_price * 0.97, 2),
            'take_profit': round(current_price * 1.05, 2),
            'confidence': 'LOW',
            'indicators': {
                'rsi': 50.0,
                'rsi_signal': 'NEUTRAL',
                'sma_20': current_price,
                'sma_50': current_price,
                'trend': 'UNKNOWN'
            },
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

# =================== ENDPOINTS ===================

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Bitcoin Trading API',
        'status': 'healthy',
        'version': '2.0-simplified',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/bitcoin-price')
def bitcoin_price():
    """Endpoint para obter preço atual do Bitcoin"""
    try:
        data = get_bitcoin_price_eur()
        return jsonify(data)
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch Bitcoin price',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/detailed-signal')
def detailed_signal():
    """Endpoint para sinal detalhado de trading"""
    try:
        # Obter preço atual
        price_data = get_bitcoin_price_eur()
        current_price = price_data['price_eur']
        
        # Obter preços históricos
        historical_prices = get_historical_prices(30)
        
        # Gerar sinal
        signal_data = generate_simple_signal(current_price, historical_prices)
        
        return jsonify(signal_data)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate trading signal',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/technical-analysis')
def technical_analysis():
    """Endpoint para análise técnica completa"""
    try:
        # Obter dados de preço
        price_data = get_bitcoin_price_eur()
        current_price = price_data['price_eur']
        
        # Obter preços históricos
        historical_prices = get_historical_prices(50)
        
        # Calcular indicadores
        rsi = calculate_simple_rsi(historical_prices)
        sma_20 = sum(historical_prices[-20:]) / 20 if len(historical_prices) >= 20 else current_price
        sma_50 = sum(historical_prices[-50:]) / 50 if len(historical_prices) >= 50 else current_price
        
        # Calcular suporte e resistência básicos
        recent_prices = historical_prices[-14:] if len(historical_prices) >= 14 else historical_prices
        support = min(recent_prices) if recent_prices else current_price * 0.95
        resistance = max(recent_prices) if recent_prices else current_price * 1.05
        
        # Determinar tendência
        if current_price > sma_20 > sma_50:
            trend = "UPTREND"
        elif current_price < sma_20 < sma_50:
            trend = "DOWNTREND"
        else:
            trend = "SIDEWAYS"
        
        return jsonify({
            'price': current_price,
            'trend': trend,
            'indicators': {
                'rsi': rsi,
                'rsi_signal': 'OVERSOLD' if rsi < 30 else 'OVERBOUGHT' if rsi > 70 else 'NEUTRAL',
                'sma_20': round(sma_20, 2),
                'sma_50': round(sma_50, 2),
                'momentum': 'BULLISH' if current_price > sma_20 else 'BEARISH' if current_price < sma_20 else 'NEUTRAL'
            },
            'support_resistance': {
                'support': round(support, 2),
                'resistance': round(resistance, 2)
            },
            'market_data': {
                'change_24h': price_data.get('change_24h', 0),
                'volume_24h_eur': price_data.get('volume_24h_eur', 0),
                'market_cap_eur': price_data.get('market_cap_eur', 0)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to perform technical analysis',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/')
def root():
    """Root endpoint - informações básicas"""
    return jsonify({
        'service': 'Bitcoin Trading API',
        'version': '2.0-simplified',
        'status': 'online',
        'endpoints': [
            '/api/health',
            '/api/bitcoin-price',
            '/api/detailed-signal',
            '/api/technical-analysis'
        ],
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Iniciando Bitcoin Trading API na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
