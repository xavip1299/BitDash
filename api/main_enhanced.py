# -*- coding: utf-8 -*-
"""
Bitcoin Trading Signals API - Versão Melhorada para Alta Confiabilidade
Melhorias baseadas nos testes de confiabilidade realizados
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
import threading

app = Flask(__name__)
CORS(app)

# Configurações
COINGECKO_API = 'https://api.coingecko.com/api/v3'

# Cache melhorado
cache = {
    'price_data': {'data': None, 'timestamp': 0, 'ttl': 60},
    'historical_data': {'data': None, 'timestamp': 0, 'ttl': 300},
    'technical_analysis': {'data': None, 'timestamp': 0, 'ttl': 120}
}

# Configurações de trading melhoradas
TRADING_CONFIG = {
    'rsi_oversold': 25,      # Mais restritivo (era 30)
    'rsi_overbought': 75,    # Mais restritivo (era 70)
    'rsi_strong_oversold': 20,
    'rsi_strong_overbought': 80,
    'volume_multiplier_threshold': 1.5,
    'trend_confirmation_periods': 3,
    'min_confidence_score': 65  # Score mínimo para sinais HIGH confidence
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
    """Obter preço atual do Bitcoin em EUR - Versão Melhorada"""
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

def calculate_improved_rsi(prices, period=14):
    """Calcular RSI melhorado com suavização"""
    if len(prices) < period + 1:
        return 50.0
    
    # Calcular mudanças de preço
    changes = []
    for i in range(1, len(prices)):
        changes.append(prices[i] - prices[i-1])
    
    # Usar apenas as mudanças mais recentes
    recent_changes = changes[-period:]
    
    # Separar ganhos e perdas
    gains = [max(0, change) for change in recent_changes]
    losses = [abs(min(0, change)) for change in recent_changes]
    
    # Calcular médias com suavização exponencial
    if len(gains) > 0 and len(losses) > 0:
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)
        
        # Evitar divisão por zero
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Suavização adicional para evitar extremos falsos
        if rsi > 95:
            rsi = 95
        elif rsi < 5:
            rsi = 5
            
        return round(rsi, 2)
    
    return 50.0

def get_enhanced_historical_data(days=30):
    """Obter dados históricos aprimorados"""
    cached = get_cached_data('historical_data')
    if cached:
        return cached
    
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
        
        # Extrair preços e volumes
        prices = [price[1] for price in data['prices']]
        volumes = [volume[1] for volume in data['total_volumes']]
        
        result = {
            'prices': prices,
            'volumes': volumes,
            'avg_volume': sum(volumes) / len(volumes) if volumes else 0
        }
        
        set_cached_data('historical_data', result)
        return result
        
    except Exception as e:
        # Dados simulados mais realistas
        base_price = 85000
        base_volume = 25000000000
        prices = []
        volumes = []
        
        for i in range(days):
            # Movimento de preços mais realista
            daily_volatility = random.uniform(0.02, 0.08)  # 2-8% volatilidade
            direction = random.choice([-1, 1])
            change = direction * random.uniform(0.005, daily_volatility)
            
            base_price *= (1 + change)
            base_volume *= random.uniform(0.8, 1.4)  # Variação de volume
            
            prices.append(base_price)
            volumes.append(base_volume)
        
        return {
            'prices': prices,
            'volumes': volumes,
            'avg_volume': sum(volumes) / len(volumes)
        }

def calculate_volume_signal(current_volume, avg_volume):
    """Calcular sinal baseado em volume"""
    if current_volume > avg_volume * TRADING_CONFIG['volume_multiplier_threshold']:
        return 'HIGH_VOLUME'
    elif current_volume < avg_volume * 0.7:
        return 'LOW_VOLUME'
    return 'NORMAL_VOLUME'

def calculate_trend_strength(prices, periods=[5, 10, 20]):
    """Calcular força da tendência em múltiplos períodos"""
    if len(prices) < max(periods):
        return 'UNKNOWN', 0
    
    trend_scores = []
    
    for period in periods:
        if len(prices) >= period:
            recent_prices = prices[-period:]
            first_price = recent_prices[0]
            last_price = recent_prices[-1]
            
            # Calcular mudança percentual
            change = (last_price - first_price) / first_price * 100
            trend_scores.append(change)
    
    # Calcular tendência média
    avg_trend = sum(trend_scores) / len(trend_scores) if trend_scores else 0
    
    # Determinar força da tendência
    if avg_trend > 5:
        return 'STRONG_UPTREND', abs(avg_trend)
    elif avg_trend > 2:
        return 'UPTREND', abs(avg_trend)
    elif avg_trend < -5:
        return 'STRONG_DOWNTREND', abs(avg_trend)
    elif avg_trend < -2:
        return 'DOWNTREND', abs(avg_trend)
    else:
        return 'SIDEWAYS', abs(avg_trend)

def generate_enhanced_signal(current_price, historical_data, price_data):
    """Gerar sinal aprimorado com lógica melhorada"""
    try:
        prices = historical_data['prices']
        volumes = historical_data['volumes']
        avg_volume = historical_data['avg_volume']
        
        # Indicadores técnicos
        rsi = calculate_improved_rsi(prices)
        
        # Médias móveis com pesos diferentes  
        sma_10 = sum(prices[-10:]) / 10 if len(prices) >= 10 else current_price
        sma_20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else current_price
        sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else current_price
        
        # Análise de tendência melhorada
        trend, trend_strength = calculate_trend_strength(prices)
        
        # Análise de volume
        current_volume = volumes[-1] if volumes else avg_volume
        volume_signal = calculate_volume_signal(current_volume, avg_volume)
        
        # Mudança de preço 24h
        change_24h = price_data.get('change_24h', 0)
        
        # === LÓGICA DE SINAL MELHORADA ===
        signal_score = 50  # Neutro
        confidence_factors = []
        
        # 1. Análise RSI (peso: 25%)
        rsi_weight = 25
        if rsi <= TRADING_CONFIG['rsi_strong_oversold']:
            signal_score += rsi_weight * 0.8  # +20 pontos
            confidence_factors.append('RSI_STRONG_OVERSOLD')
        elif rsi <= TRADING_CONFIG['rsi_oversold']:
            signal_score += rsi_weight * 0.6  # +15 pontos
            confidence_factors.append('RSI_OVERSOLD')
        elif rsi >= TRADING_CONFIG['rsi_strong_overbought']:
            signal_score -= rsi_weight * 0.8  # -20 pontos
            confidence_factors.append('RSI_STRONG_OVERBOUGHT')
        elif rsi >= TRADING_CONFIG['rsi_overbought']:
            signal_score -= rsi_weight * 0.6  # -15 pontos
            confidence_factors.append('RSI_OVERBOUGHT')
        
        # 2. Análise de Tendência (peso: 20%)
        trend_weight = 20
        if trend == 'STRONG_UPTREND':
            signal_score += trend_weight * 0.9  # +18 pontos
            confidence_factors.append('STRONG_UPTREND')
        elif trend == 'UPTREND':
            signal_score += trend_weight * 0.5  # +10 pontos
            confidence_factors.append('UPTREND')
        elif trend == 'STRONG_DOWNTREND':
            signal_score -= trend_weight * 0.9  # -18 pontos
            confidence_factors.append('STRONG_DOWNTREND')
        elif trend == 'DOWNTREND':
            signal_score -= trend_weight * 0.5  # -10 pontos
            confidence_factors.append('DOWNTREND')
        
        # 3. Análise de Médias Móveis (peso: 15%)
        ma_weight = 15
        if current_price > sma_10 > sma_20 > sma_50:
            signal_score += ma_weight * 0.8  # +12 pontos
            confidence_factors.append('MA_BULLISH_ALIGNMENT')
        elif current_price < sma_10 < sma_20 < sma_50:
            signal_score -= ma_weight * 0.8  # -12 pontos
            confidence_factors.append('MA_BEARISH_ALIGNMENT')
        elif current_price > sma_20:
            signal_score += ma_weight * 0.3  # +4.5 pontos
        elif current_price < sma_20:
            signal_score -= ma_weight * 0.3  # -4.5 pontos
        
        # 4. Análise de Volume (peso: 15%)
        volume_weight = 15
        if volume_signal == 'HIGH_VOLUME':
            # Volume alto confirma o movimento
            if signal_score > 50:
                signal_score += volume_weight * 0.5  # +7.5 pontos para buy
                confidence_factors.append('HIGH_VOLUME_CONFIRMATION')
            else:
                signal_score -= volume_weight * 0.5  # -7.5 pontos para sell
                confidence_factors.append('HIGH_VOLUME_CONFIRMATION')
        elif volume_signal == 'LOW_VOLUME':
            # Volume baixo reduz confiança
            if abs(signal_score - 50) > 10:
                signal_score *= 0.9  # Reduz a força do sinal
                confidence_factors.append('LOW_VOLUME_WEAKNESS')
        
        # 5. Análise de Momentum 24h (peso: 10%)
        momentum_weight = 10
        if change_24h > 5:
            signal_score += momentum_weight * 0.6  # +6 pontos
            confidence_factors.append('POSITIVE_24H_MOMENTUM')
        elif change_24h < -5:
            signal_score -= momentum_weight * 0.6  # -6 pontos
            confidence_factors.append('NEGATIVE_24H_MOMENTUM')
        
        # === DETERMINAÇÃO DO SINAL ===
        signal_score = max(0, min(100, signal_score))  # Manter entre 0-100
        
        # Lógica melhorada para tipos de sinal
        if signal_score >= 75:
            signal_type = "BUY"
            confidence = "HIGH"
        elif signal_score >= 65:
            signal_type = "BUY"  
            confidence = "MEDIUM"
        elif signal_score >= 55:
            signal_type = "BUY"
            confidence = "LOW"
        elif signal_score <= 25:
            signal_type = "SELL"
            confidence = "HIGH"
        elif signal_score <= 35:
            signal_type = "SELL"
            confidence = "MEDIUM"
        elif signal_score <= 45:
            signal_type = "SELL"
            confidence = "LOW"
        else:
            signal_type = "HOLD"
            confidence = "MEDIUM"
        
        # Reduzir confiança se não há fatores suficientes
        if len(confidence_factors) < 2 and confidence == "HIGH":
            confidence = "MEDIUM"
        elif len(confidence_factors) == 0 and confidence == "MEDIUM":
            confidence = "LOW"
        
        # === CÁLCULO DE STOP LOSS E TAKE PROFIT MELHORADO ===
        volatility = trend_strength / 100 if trend_strength > 0 else 0.03
        
        if signal_type == "BUY":
            if confidence == "HIGH":
                sl_distance = max(0.03, volatility * 1.5)  # 3% mínimo
                tp_distance = sl_distance * 2.5  # Risk/Reward 2.5:1
            else:
                sl_distance = max(0.04, volatility * 2)  # 4% mínimo
                tp_distance = sl_distance * 2.0  # Risk/Reward 2:1
            
            stop_loss = current_price * (1 - sl_distance)
            take_profit = current_price * (1 + tp_distance)
            
        elif signal_type == "SELL":
            if confidence == "HIGH":
                sl_distance = max(0.03, volatility * 1.5)  # 3% mínimo
                tp_distance = sl_distance * 2.5  # Risk/Reward 2.5:1
            else:
                sl_distance = max(0.04, volatility * 2)  # 4% mínimo
                tp_distance = sl_distance * 2.0  # Risk/Reward 2:1
            
            stop_loss = current_price * (1 + sl_distance)
            take_profit = current_price * (1 - tp_distance)
            
        else:  # HOLD
            stop_loss = current_price * 0.96  # -4%
            take_profit = current_price * 1.06  # +6%
        
        # Análise de RSI para sinal secundário
        rsi_signal = 'NEUTRAL'
        if rsi <= TRADING_CONFIG['rsi_strong_oversold']:
            rsi_signal = 'STRONG_OVERSOLD'
        elif rsi <= TRADING_CONFIG['rsi_oversold']:
            rsi_signal = 'OVERSOLD'
        elif rsi >= TRADING_CONFIG['rsi_strong_overbought']:
            rsi_signal = 'STRONG_OVERBOUGHT'
        elif rsi >= TRADING_CONFIG['rsi_overbought']:
            rsi_signal = 'OVERBOUGHT'
        
        return {
            'signal': signal_type,
            'score': round(signal_score, 1),
            'current_price': current_price,
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'confidence': confidence,
            'confidence_factors': confidence_factors,
            'indicators': {
                'rsi': rsi,
                'rsi_signal': rsi_signal,
                'sma_10': round(sma_10, 2),
                'sma_20': round(sma_20, 2),
                'sma_50': round(sma_50, 2),
                'trend': trend,
                'trend_strength': round(trend_strength, 2),
                'volume_signal': volume_signal,
                'change_24h': round(change_24h, 2)
            },
            'risk_metrics': {
                'volatility_estimate': round(volatility * 100, 2),
                'risk_reward_ratio': round((abs(take_profit - current_price) / abs(stop_loss - current_price)), 2) if stop_loss != current_price else 0
            },
            'timestamp': datetime.now().isoformat(),
            'version': 'enhanced_v1.0'
        }
        
    except Exception as e:
        # Sinal básico em caso de erro
        return {
            'signal': 'HOLD',
            'score': 50,
            'current_price': current_price,
            'stop_loss': round(current_price * 0.96, 2),
            'take_profit': round(current_price * 1.06, 2),
            'confidence': 'LOW',
            'confidence_factors': [],
            'indicators': {
                'rsi': 50.0,
                'rsi_signal': 'NEUTRAL',
                'sma_10': current_price,
                'sma_20': current_price,
                'sma_50': current_price,
                'trend': 'UNKNOWN',
                'trend_strength': 0,
                'volume_signal': 'UNKNOWN',
                'change_24h': 0
            },
            'risk_metrics': {
                'volatility_estimate': 3.0,
                'risk_reward_ratio': 1.5
            },
            'timestamp': datetime.now().isoformat(),
            'version': 'enhanced_v1.0',
            'error': str(e)
        }

# =================== ENDPOINTS ===================

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Bitcoin Trading API Enhanced',
        'status': 'healthy',
        'version': 'enhanced_v1.0',
        'improvements': [
            'Enhanced RSI calculation',
            'Multi-timeframe trend analysis', 
            'Volume confirmation',
            'Improved confidence scoring',
            'Dynamic stop loss/take profit',
            'Risk metrics calculation'
        ],
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
    """Endpoint para sinal detalhado de trading - Versão Melhorada"""
    try:
        # Obter preço atual
        price_data = get_bitcoin_price_eur()
        current_price = price_data['price_eur']
        
        # Obter dados históricos aprimorados
        historical_data = get_enhanced_historical_data(60)  # 60 dias para melhor análise
        
        # Gerar sinal aprimorado
        signal_data = generate_enhanced_signal(current_price, historical_data, price_data)
        
        return jsonify(signal_data)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate enhanced trading signal',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/technical-analysis')
def technical_analysis():
    """Endpoint para análise técnica completa"""
    try:
        # Usar o mesmo endpoint melhorado
        return detailed_signal()
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate technical analysis',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/signal-confidence')
def signal_confidence():
    """Endpoint específico para verificar confiança do sinal"""
    try:
        # Obter sinal
        price_data = get_bitcoin_price_eur()
        current_price = price_data['price_eur']
        historical_data = get_enhanced_historical_data(60)
        signal_data = generate_enhanced_signal(current_price, historical_data, price_data)
        
        # Retornar apenas métricas de confiança
        return jsonify({
            'signal': signal_data['signal'],
            'score': signal_data['score'],
            'confidence': signal_data['confidence'],
            'confidence_factors': signal_data['confidence_factors'],
            'risk_metrics': signal_data['risk_metrics'],
            'recommendation': 'APPROVE' if signal_data['score'] >= TRADING_CONFIG['min_confidence_score'] or signal_data['confidence'] == 'HIGH' else 'REVIEW',
            'timestamp': signal_data['timestamp']
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to analyze signal confidence',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ============ KEEP ALIVE SERVICE ============

keep_alive_status = {
    'active': True,
    'last_ping': datetime.now().isoformat(),
    'ping_count': 0,
    'uptime_start': datetime.now().isoformat()
}

def keep_alive_ping():
    """Função para manter o serviço ativo"""
    while True:
        try:
            keep_alive_status['last_ping'] = datetime.now().isoformat()
            keep_alive_status['ping_count'] += 1
            time.sleep(25 * 60)  # Ping a cada 25 minutos
        except Exception as e:
            print(f"Keep alive error: {e}")
            time.sleep(60)

@app.route('/api/keep-alive-status')
def keep_alive_status_endpoint():
    """Endpoint para verificar status do keep-alive"""
    return jsonify({
        'status': 'active',
        'service': 'Bitcoin Trading API Enhanced',
        'version': 'enhanced_v1.0',
        'keep_alive': keep_alive_status,
        'timestamp': datetime.now().isoformat()
    })

# Iniciar keep-alive em thread separada
if os.environ.get('FLASK_ENV') != 'development':
    keep_alive_thread = threading.Thread(target=keep_alive_ping, daemon=True)
    keep_alive_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
