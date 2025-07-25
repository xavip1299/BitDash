# -*- coding: utf-8 -*-
"""
Multi-Crypto Trading Signals API - Bitcoin, Ethereum & XRP
Sistema otimizado com solução para rate limiting
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

# Suporte a múltiplas criptomoedas
SUPPORTED_CRYPTOS = {
    'bitcoin': {
        'id': 'bitcoin',
        'symbol': 'BTC',
        'name': 'Bitcoin',
        'emoji': '₿',
        'color': '#f7931a'
    },
    'ethereum': {
        'id': 'ethereum',
        'symbol': 'ETH',
        'name': 'Ethereum',
        'emoji': '⟠',
        'color': '#627eea'
    },
    'xrp': {
        'id': 'ripple',
        'symbol': 'XRP',
        'name': 'XRP',
        'emoji': '◆',
        'color': '#23292f'
    }
}

# Cache melhorado com TTL mais longos para evitar rate limiting
cache = {}
last_request_time = 0
REQUEST_DELAY = 2  # 2 segundos entre requests para evitar rate limiting

def init_cache():
    """Inicializar cache para todas as criptomoedas"""
    for crypto_key in SUPPORTED_CRYPTOS.keys():
        cache[crypto_key] = {
            'price_data': {'data': None, 'timestamp': 0, 'ttl': 120},  # 2 minutos (aumentado)
            'historical_data': {'data': None, 'timestamp': 0, 'ttl': 900},  # 15 minutos (muito aumentado)
            'technical_analysis': {'data': None, 'timestamp': 0, 'ttl': 300}  # 5 minutos (aumentado)
        }

# Configurações de trading melhoradas
TRADING_CONFIG = {
    'rsi_oversold': 25,
    'rsi_overbought': 75,
    'rsi_strong_oversold': 20,
    'rsi_strong_overbought': 80,
    'volume_multiplier_threshold': 1.5,
    'trend_confirmation_periods': 3,
    'min_confidence_score': 65
}

def get_cached_data(crypto: str, key: str):
    """Retorna dados do cache se ainda válidos"""
    if crypto in cache and key in cache[crypto]:
        data = cache[crypto][key]
        if time.time() - data['timestamp'] < data['ttl']:
            return data['data']
    return None

def set_cached_data(crypto: str, key: str, data):
    """Armazena dados no cache"""
    if crypto not in cache:
        init_cache()
    cache[crypto][key] = {
        'data': data,
        'timestamp': time.time(),
        'ttl': cache[crypto][key]['ttl']
    }

def rate_limit_delay():
    """Aplicar delay para evitar rate limiting"""
    global last_request_time
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    if time_since_last < REQUEST_DELAY:
        sleep_time = REQUEST_DELAY - time_since_last
        print(f"Rate limiting delay: {sleep_time:.1f}s")
        time.sleep(sleep_time)
    
    last_request_time = time.time()

def fetch_all_prices_batch():
    """Buscar preços de todas as criptomoedas em uma única request"""
    try:
        # Verificar se temos cache válido para pelo menos uma crypto
        cached_count = 0
        for crypto_id in SUPPORTED_CRYPTOS.keys():
            if get_cached_data(crypto_id, 'price_data'):
                cached_count += 1
        
        # Se temos cache válido para todas, não fazer request
        if cached_count == len(SUPPORTED_CRYPTOS):
            return True
        
        rate_limit_delay()
        
        # Buscar todos os preços em uma única request
        all_ids = ','.join([info['id'] for info in SUPPORTED_CRYPTOS.values()])
        url = f"{COINGECKO_API}/simple/price"
        params = {
            'ids': all_ids,
            'vs_currencies': 'usd,eur',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true'
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        # Armazenar dados para cada criptomoeda
        for crypto_key, crypto_info in SUPPORTED_CRYPTOS.items():
            if crypto_info['id'] in data:
                crypto_data = data[crypto_info['id']]
                
                result = {
                    'price_usd': crypto_data['usd'],
                    'price_eur': crypto_data['eur'],
                    'change_24h': crypto_data['usd_24h_change'],
                    'volume_24h': crypto_data['usd_24h_vol'],
                    'market_cap': crypto_data['usd_market_cap'],
                    'timestamp': datetime.now().isoformat(),
                    'crypto': crypto_key,
                    'symbol': crypto_info['symbol']
                }
                
                set_cached_data(crypto_key, 'price_data', result)
        
        return True
        
    except Exception as e:
        print(f"Erro ao buscar preços em batch: {e}")
        return False

def fetch_crypto_price(crypto_id: str):
    """Buscar preço atual de uma criptomoeda"""
    cached = get_cached_data(crypto_id, 'price_data')
    if cached:
        return cached
    
    # Tentar buscar em batch primeiro
    if fetch_all_prices_batch():
        cached = get_cached_data(crypto_id, 'price_data')
        if cached:
            return cached
    
    # Fallback: buscar individual com delay
    try:
        rate_limit_delay()
        
        url = f"{COINGECKO_API}/simple/price"
        params = {
            'ids': SUPPORTED_CRYPTOS[crypto_id]['id'],
            'vs_currencies': 'usd,eur',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true'
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        crypto_data = data[SUPPORTED_CRYPTOS[crypto_id]['id']]
        
        result = {
            'price_usd': crypto_data['usd'],
            'price_eur': crypto_data['eur'],
            'change_24h': crypto_data['usd_24h_change'],
            'volume_24h': crypto_data['usd_24h_vol'],
            'market_cap': crypto_data['usd_market_cap'],
            'timestamp': datetime.now().isoformat(),
            'crypto': crypto_id,
            'symbol': SUPPORTED_CRYPTOS[crypto_id]['symbol']
        }
        
        set_cached_data(crypto_id, 'price_data', result)
        return result
        
    except Exception as e:
        print(f"Erro ao buscar preço {crypto_id}: {e}")
        return None

def generate_simulated_historical_data(crypto_id: str, current_price: float):
    """Gerar dados históricos simulados quando a API falhar"""
    print(f"Gerando dados simulados para {crypto_id}")
    
    historical = []
    base_price = current_price
    
    # Gerar 168 pontos (7 dias * 24 horas)
    for i in range(168):
        # Simulação de variação de preço (±3%)
        variation = random.uniform(-0.03, 0.03)
        price = base_price * (1 + variation)
        
        # Volume baseado no preço (simulação)
        volume = random.uniform(1000000, 10000000) * (current_price / 50000)
        
        timestamp = int((datetime.now() - timedelta(hours=168-i)).timestamp() * 1000)
        
        historical.append({
            'timestamp': timestamp,
            'price': price,
            'volume': volume,
            'date': datetime.fromtimestamp(timestamp/1000).isoformat()
        })
        
        base_price = price  # Próximo preço baseado no anterior
    
    return {
        'crypto': crypto_id,
        'symbol': SUPPORTED_CRYPTOS[crypto_id]['symbol'],
        'data': historical,
        'count': len(historical),
        'period': "7 days (simulated)"
    }

def fetch_historical_data(crypto_id: str, days: int = 7):
    """Buscar dados históricos de uma criptomoeda com fallback"""
    cached = get_cached_data(crypto_id, 'historical_data')
    if cached:
        return cached
    
    try:
        rate_limit_delay()
        
        url = f"{COINGECKO_API}/coins/{SUPPORTED_CRYPTOS[crypto_id]['id']}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'hourly' if days <= 7 else 'daily'
        }
        
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        
        data = response.json()
        
        # Processar dados históricos
        prices = data['prices']
        volumes = data['total_volumes']
        
        historical = []
        for i, (timestamp, price) in enumerate(prices):
            volume = volumes[i][1] if i < len(volumes) else 0
            historical.append({
                'timestamp': timestamp,
                'price': price,
                'volume': volume,
                'date': datetime.fromtimestamp(timestamp/1000).isoformat()
            })
        
        result = {
            'crypto': crypto_id,
            'symbol': SUPPORTED_CRYPTOS[crypto_id]['symbol'],
            'data': historical,
            'count': len(historical),
            'period': f"{days} days"
        }
        
        set_cached_data(crypto_id, 'historical_data', result)
        return result
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in [429, 401]:  # Rate limiting ou unauthorized
            print(f"Rate limiting detectado para {crypto_id}, usando dados simulados")
            
            # Tentar obter preço atual para simular dados
            price_data = fetch_crypto_price(crypto_id)
            if price_data:
                current_price = price_data['price_usd']
                simulated_data = generate_simulated_historical_data(crypto_id, current_price)
                set_cached_data(crypto_id, 'historical_data', simulated_data)
                return simulated_data
        
        print(f"Erro HTTP ao buscar histórico {crypto_id}: {e}")
        return None
        
    except Exception as e:
        print(f"Erro ao buscar histórico {crypto_id}: {e}")
        return None

def calculate_rsi(prices, period=14):
    """Calcular RSI melhorado"""
    if len(prices) < period + 1:
        return 50
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    if len(gains) < period:
        return 50
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)

def analyze_trend(prices, volumes):
    """Análise de tendência melhorada"""
    if len(prices) < 10:
        return {'trend': 'NEUTRAL', 'strength': 0, 'volume_analysis': 'NORMAL_VOLUME', 'short_ma': 0, 'medium_ma': 0}
    
    # Análise multi-timeframe
    short_prices = prices[-6:]  # 6 períodos recentes
    medium_prices = prices[-12:]  # 12 períodos médios
    
    # Calcular médias móveis
    short_ma = sum(short_prices) / len(short_prices)
    medium_ma = sum(medium_prices) / len(medium_prices)
    
    # Tendência baseada em médias móveis
    trend_strength = abs(short_ma - medium_ma) / medium_ma * 100
    
    if short_ma > medium_ma * 1.02:
        trend = 'STRONG_UPTREND' if trend_strength > 5 else 'UPTREND'
    elif short_ma < medium_ma * 0.98:
        trend = 'STRONG_DOWNTREND' if trend_strength > 5 else 'DOWNTREND'
    else:
        trend = 'NEUTRAL'
    
    # Análise de volume
    if len(volumes) >= 20:
        recent_volumes = volumes[-6:]
        avg_volume = sum(volumes[-20:]) / min(20, len(volumes))
        current_volume = recent_volumes[-1] if recent_volumes else avg_volume
        volume_strength = 'HIGH_VOLUME' if current_volume > avg_volume * 1.5 else 'NORMAL_VOLUME'
    else:
        volume_strength = 'NORMAL_VOLUME'
    
    return {
        'trend': trend,
        'strength': round(trend_strength, 2),
        'volume_analysis': volume_strength,
        'short_ma': round(short_ma, 2),
        'medium_ma': round(medium_ma, 2)
    }

def calculate_confidence_factors(rsi, trend_data, price_change_24h):
    """Calcular fatores de confiança melhorados"""
    factors = []
    
    # RSI factors
    if rsi <= TRADING_CONFIG['rsi_strong_oversold']:
        factors.append('RSI_STRONG_OVERSOLD')
    elif rsi <= TRADING_CONFIG['rsi_oversold']:
        factors.append('RSI_OVERSOLD')
    elif rsi >= TRADING_CONFIG['rsi_strong_overbought']:
        factors.append('RSI_STRONG_OVERBOUGHT')
    elif rsi >= TRADING_CONFIG['rsi_overbought']:
        factors.append('RSI_OVERBOUGHT')
    
    # Trend factors
    if trend_data['trend'] in ['STRONG_UPTREND', 'UPTREND']:
        factors.append(trend_data['trend'])
    elif trend_data['trend'] in ['STRONG_DOWNTREND', 'DOWNTREND']:
        factors.append(trend_data['trend'])
    
    # Volume factors
    if trend_data['volume_analysis'] == 'HIGH_VOLUME':
        factors.append('HIGH_VOLUME_CONFIRMATION')
    
    # Price momentum factors
    if abs(price_change_24h) > 5:
        factors.append('HIGH_MOMENTUM')
    
    return factors

def generate_trading_signal(crypto_id: str):
    """Gerar sinal de trading melhorado para uma criptomoeda"""
    try:
        # Buscar dados com cache otimizado
        price_data = fetch_crypto_price(crypto_id)
        historical_data = fetch_historical_data(crypto_id)
        
        if not price_data:
            print(f"Falha ao obter preço para {crypto_id}")
            return None
            
        if not historical_data:
            print(f"Falha ao obter histórico para {crypto_id}")
            return None
        
        # Extrair preços e volumes
        prices = [item['price'] for item in historical_data['data']]
        volumes = [item['volume'] for item in historical_data['data']]
        
        if len(prices) < 10:
            print(f"Dados insuficientes para {crypto_id}: {len(prices)} pontos")
            return None
        
        # Cálculos técnicos
        rsi = calculate_rsi(prices)
        trend_data = analyze_trend(prices, volumes)
        
        # Calcular score base
        score = 50  # Score neutro
        
        # Ajustes baseados em RSI
        if rsi <= 25:
            score += 25  # Forte sobrevendido
        elif rsi <= 35:
            score += 15  # Sobrevendido
        elif rsi >= 75:
            score -= 25  # Forte sobrecomprado
        elif rsi >= 65:
            score -= 15  # Sobrecomprado
        
        # Ajustes baseados em tendência
        if trend_data['trend'] == 'STRONG_UPTREND':
            score += 20
        elif trend_data['trend'] == 'UPTREND':
            score += 10
        elif trend_data['trend'] == 'STRONG_DOWNTREND':
            score -= 20
        elif trend_data['trend'] == 'DOWNTREND':
            score -= 10
        
        # Ajustes baseados em volume
        if trend_data['volume_analysis'] == 'HIGH_VOLUME':
            score += 10
        
        # Garantir score entre 0-100
        score = max(0, min(100, score))
        
        # Determinar sinal
        if score >= 65:
            signal = 'BUY'
        elif score <= 35:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        # Calcular confiança
        confidence_factors = calculate_confidence_factors(rsi, trend_data, price_data['change_24h'])
        
        if len(confidence_factors) >= 3 and score >= 70:
            confidence = 'HIGH'
        elif len(confidence_factors) >= 2 and score >= 55:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        # Calcular stop loss e take profit dinâmicos
        volatility = abs(price_data['change_24h']) / 100
        current_price = price_data['price_usd']
        
        if signal == 'BUY':
            stop_loss = current_price * (1 - max(0.03, volatility * 2))
            take_profit = current_price * (1 + max(0.06, volatility * 3))
        elif signal == 'SELL':
            stop_loss = current_price * (1 + max(0.03, volatility * 2))
            take_profit = current_price * (1 - max(0.06, volatility * 3))
        else:
            stop_loss = current_price
            take_profit = current_price
        
        # Risk/Reward ratio
        if signal != 'HOLD':
            risk = abs(current_price - stop_loss)
            reward = abs(take_profit - current_price)
            risk_reward_ratio = reward / risk if risk > 0 else 2.0
        else:
            risk_reward_ratio = 1.0
        
        return {
            'crypto': crypto_id,
            'symbol': SUPPORTED_CRYPTOS[crypto_id]['symbol'],
            'name': SUPPORTED_CRYPTOS[crypto_id]['name'],
            'emoji': SUPPORTED_CRYPTOS[crypto_id]['emoji'],
            'signal': signal,
            'score': round(score, 1),
            'confidence': confidence,
            'confidence_factors': confidence_factors,
            'current_price': {
                'usd': round(current_price, 2),
                'eur': round(price_data['price_eur'], 2)
            },
            'rsi': rsi,
            'trend': trend_data,
            'change_24h': round(price_data['change_24h'], 2),
            'volume_24h': price_data['volume_24h'],
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            'volatility_estimate': round(volatility * 100, 2),
            'market_cap': price_data['market_cap'],
            'timestamp': datetime.now().isoformat(),
            'version': 'multi_crypto_v2.0_optimized',
            'data_source': historical_data.get('period', '7 days')
        }
        
    except Exception as e:
        print(f"Erro crítico ao gerar sinal {crypto_id}: {e}")
        return None

# Keep-alive service
keep_alive_data = {
    'active': True,
    'last_ping': datetime.now().isoformat(),
    'ping_count': 0,
    'uptime_start': datetime.now().isoformat()
}

def keep_alive_service():
    """Serviço para manter API ativa no Render.com"""
    while True:
        try:
            time.sleep(600)  # 10 minutos
            keep_alive_data['last_ping'] = datetime.now().isoformat()
            keep_alive_data['ping_count'] += 1
            
            # Auto-ping para evitar spin down
            try:
                requests.get('https://bitdash-9dnk.onrender.com/api/health', timeout=5)
            except:
                pass  # Ignorar erros de auto-ping
                
        except Exception as e:
            print(f"Erro no keep-alive: {e}")
            time.sleep(60)

# Inicializar cache e keep-alive
init_cache()
keep_alive_thread = threading.Thread(target=keep_alive_service, daemon=True)
keep_alive_thread.start()

# === ROTAS DA API ===

@app.route('/')
def home():
    return jsonify({
        'service': 'Multi-Crypto Trading Signals API (Rate Limit Optimized)',
        'version': 'multi_crypto_v2.0_optimized',
        'supported_cryptos': list(SUPPORTED_CRYPTOS.keys()),
        'endpoints': [
            '/api/health',
            '/api/cryptos',
            '/api/<crypto>/price',
            '/api/<crypto>/signal',
            '/api/<crypto>/technical-analysis',
            '/api/signals/all',
            '/api/keep-alive-status'
        ],
        'optimizations': [
            'Extended cache TTL',
            'Batch price requests',
            'Rate limiting delays',
            'Simulated fallback data',
            'Improved error handling'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Multi-Crypto Trading Signals API (Rate Limit Optimized)',
        'version': 'multi_crypto_v2.0_optimized',
        'supported_cryptos': len(SUPPORTED_CRYPTOS),
        'uptime_start': keep_alive_data['uptime_start'],
        'cache_stats': {
            'price_ttl': '2 minutes',
            'historical_ttl': '15 minutes',
            'analysis_ttl': '5 minutes'
        },
        'rate_limiting': {
            'enabled': True,
            'delay_between_requests': f'{REQUEST_DELAY}s',
            'batch_requests': True,
            'fallback_simulation': True
        },
        'timestamp': datetime.now().isoformat(),
        'improvements': [
            'Multi-cryptocurrency support (BTC, ETH, XRP)',
            'Rate limiting protection',
            'Extended cache system',
            'Batch API requests',
            'Simulated fallback data',
            'Enhanced error handling'
        ]
    })

@app.route('/api/cryptos')
def list_cryptos():
    """Listar todas as criptomoedas suportadas"""
    return jsonify({
        'supported_cryptos': SUPPORTED_CRYPTOS,
        'count': len(SUPPORTED_CRYPTOS),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/<crypto>/price')
def get_crypto_price(crypto):
    """Obter preço de uma criptomoeda específica"""
    if crypto not in SUPPORTED_CRYPTOS:
        return jsonify({'error': f'Criptomoeda não suportada: {crypto}'}), 400
    
    price_data = fetch_crypto_price(crypto)
    if not price_data:
        return jsonify({'error': f'Erro ao buscar preço de {crypto}'}), 500
    
    return jsonify(price_data)

@app.route('/api/<crypto>/signal')
def get_crypto_signal(crypto):
    """Obter sinal de trading de uma criptomoeda específica"""
    if crypto not in SUPPORTED_CRYPTOS:
        return jsonify({'error': f'Criptomoeda não suportada: {crypto}'}), 400
    
    signal = generate_trading_signal(crypto)
    if not signal:
        return jsonify({'error': f'Erro ao gerar sinal para {crypto}'}), 500
    
    return jsonify(signal)

@app.route('/api/<crypto>/technical-analysis')
def get_crypto_analysis(crypto):
    """Obter análise técnica detalhada de uma criptomoeda"""
    if crypto not in SUPPORTED_CRYPTOS:
        return jsonify({'error': f'Criptomoeda não suportada: {crypto}'}), 400
    
    try:
        price_data = fetch_crypto_price(crypto)
        historical_data = fetch_historical_data(crypto)
        
        if not price_data or not historical_data:
            return jsonify({'error': f'Erro ao buscar dados de {crypto}'}), 500
        
        prices = [item['price'] for item in historical_data['data']]
        volumes = [item['volume'] for item in historical_data['data']]
        
        rsi = calculate_rsi(prices)
        trend_data = analyze_trend(prices, volumes)
        
        return jsonify({
            'crypto': crypto,
            'symbol': SUPPORTED_CRYPTOS[crypto]['symbol'],
            'name': SUPPORTED_CRYPTOS[crypto]['name'],
            'price_analysis': price_data,
            'technical_indicators': {
                'rsi': rsi,
                'trend': trend_data
            },
            'historical_summary': {
                'periods': len(historical_data['data']),
                'data_source': historical_data.get('period', '7 days'),
                'price_range': {
                    'min': min(prices),
                    'max': max(prices),
                    'avg': sum(prices) / len(prices)
                }
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro na análise técnica de {crypto}: {str(e)}'}), 500

@app.route('/api/signals/all')
def get_all_signals():
    """Obter sinais de todas as criptomoedas com throttling"""
    signals = {}
    errors = []
    
    # Buscar preços em batch primeiro
    print("Buscando preços em batch...")
    fetch_all_prices_batch()
    
    for crypto in SUPPORTED_CRYPTOS:
        try:
            print(f"Gerando sinal para {crypto}...")
            signal = generate_trading_signal(crypto)
            if signal:
                signals[crypto] = signal
            else:
                errors.append(f"Falha ao gerar sinal para {crypto}")
                
        except Exception as e:
            errors.append(f"Erro em {crypto}: {str(e)}")
        
        # Pequeno delay entre sinais para evitar sobrecarga
        if len(signals) < len(SUPPORTED_CRYPTOS) - 1:
            time.sleep(0.5)
    
    result = {
        'signals': signals,
        'count': len(signals),
        'timestamp': datetime.now().isoformat(),
        'version': 'multi_crypto_v2.0_optimized'
    }
    
    if errors:
        result['errors'] = errors
    
    return jsonify(result)

@app.route('/api/keep-alive-status')
def keep_alive_status():
    return jsonify({
        'service': 'Multi-Crypto Trading Signals API (Rate Limit Optimized)',
        'status': 'active',
        'keep_alive': keep_alive_data,
        'version': 'multi_crypto_v2.0_optimized',
        'timestamp': datetime.now().isoformat()
    })

# Manter compatibilidade com rotas antigas (Bitcoin)
@app.route('/api/bitcoin-price')
def bitcoin_price():
    """Compatibilidade: redirecionar para nova rota"""
    return get_crypto_price('bitcoin')

@app.route('/api/detailed-signal')
def detailed_signal():
    """Compatibilidade: redirecionar para nova rota Bitcoin"""
    return get_crypto_signal('bitcoin')

@app.route('/api/technical-analysis')
def technical_analysis():
    """Compatibilidade: redirecionar para nova rota Bitcoin"""
    return get_crypto_analysis('bitcoin')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
