#!/usr/bin/env python3
"""
API de Sinais de Trading com Reliability Score
Calcula confiabilidade de 0-100 baseada em múltiplos indicadores
"""

import os
import time
import math
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Configurações
SUPPORTED_CRYPTOS = {
    'bitcoin': {'id': 'bitcoin', 'symbol': 'BTC', 'name': 'Bitcoin'},
    'ethereum': {'id': 'ethereum', 'symbol': 'ETH', 'name': 'Ethereum'},
    'xrp': {'id': 'ripple', 'symbol': 'XRP', 'name': 'XRP'}
}

REQUEST_DELAY = 1.2  # Delay entre requests para evitar rate limiting
last_request_time = 0
cache = {}

def init_cache():
    """Inicializar cache com histórico para cálculos técnicos"""
    global cache
    print("🔄 Inicializando cache avançado...")
    cache = {
        'prices': {},
        'historical': {},  # Para RSI, MA, etc
        'last_update': 0,
        'ttl': 300  # 5 minutos
    }
    print("✅ Cache avançado inicializado")

def calculate_rsi(prices, period=14):
    """Calcular RSI (Relative Strength Index)"""
    if len(prices) < period + 1:
        return 50  # Valor neutro se não há dados suficientes
    
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

def calculate_moving_averages(prices):
    """Calcular médias móveis simples"""
    if len(prices) < 20:
        return {'ma7': prices[-1] if prices else 0, 'ma20': prices[-1] if prices else 0}
    
    ma7 = sum(prices[-7:]) / 7 if len(prices) >= 7 else prices[-1]
    ma20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else prices[-1]
    
    return {'ma7': ma7, 'ma20': ma20}

def calculate_volatility(prices, period=7):
    """Calcular volatilidade (desvio padrão)"""
    if len(prices) < period:
        return 0
    
    recent_prices = prices[-period:]
    avg = sum(recent_prices) / len(recent_prices)
    variance = sum((p - avg) ** 2 for p in recent_prices) / len(recent_prices)
    volatility = math.sqrt(variance) / avg * 100
    
    return round(volatility, 2)

def calculate_reliability_score(crypto_data, historical_prices):
    """
    Calcular Reliability Score de 0-100 baseado em múltiplos fatores:
    - RSI (30 pontos): Sobrecompra/sobrevenda
    - Tendências MA (25 pontos): Médias móveis
    - Volatilidade (20 pontos): Estabilidade do preço
    - Momentum (15 pontos): Força da mudança 24h
    - Consistência (10 pontos): Estabilidade do sinal
    """
    
    current_price = crypto_data['price_usd']
    change_24h = crypto_data['change_24h']
    
    # Preparar dados históricos (simulados se necessário)
    if len(historical_prices) < 20:
        # Simular dados históricos baseados no preço atual
        base_price = current_price
        historical_prices = []
        for i in range(20):
            # Simular pequenas variações
            variation = (i % 3 - 1) * (current_price * 0.02)
            historical_prices.append(base_price + variation)
        historical_prices.append(current_price)
    
    # 1. RSI Score (30 pontos)
    rsi = calculate_rsi(historical_prices)
    if 30 <= rsi <= 70:
        rsi_score = 30  # RSI neutro = máxima confiabilidade
    elif rsi < 30:
        rsi_score = 20 + (rsi / 30) * 10  # Sobrevenda forte
    else:  # rsi > 70
        rsi_score = 20 + ((100 - rsi) / 30) * 10  # Sobrecompra forte
    
    # 2. Tendência das Médias Móveis (25 pontos)
    mas = calculate_moving_averages(historical_prices)
    ma7, ma20 = mas['ma7'], mas['ma20']
    
    if ma7 > ma20 * 1.02:  # Tendência de alta forte
        if change_24h > 0:
            ma_score = 25  # Confirmação da tendência
        else:
            ma_score = 15  # Contradição
    elif ma7 < ma20 * 0.98:  # Tendência de baixa forte
        if change_24h < 0:
            ma_score = 25  # Confirmação da tendência
        else:
            ma_score = 15  # Contradição
    else:  # Tendência lateral
        ma_score = 20  # Neutro
    
    # 3. Volatilidade (20 pontos) - Menor volatilidade = maior confiabilidade
    volatility = calculate_volatility(historical_prices)
    if volatility < 2:
        vol_score = 20  # Baixa volatilidade
    elif volatility < 5:
        vol_score = 15
    elif volatility < 10:
        vol_score = 10
    else:
        vol_score = 5  # Alta volatilidade
    
    # 4. Momentum 24h (15 pontos)
    abs_change = abs(change_24h)
    if 2 <= abs_change <= 5:
        momentum_score = 15  # Movimento significativo mas controlado
    elif 1 <= abs_change < 2:
        momentum_score = 12  # Movimento moderado
    elif abs_change > 5:
        momentum_score = 8   # Movimento muito forte (pode ser instável)
    else:
        momentum_score = 5   # Movimento muito fraco
    
    # 5. Consistência (10 pontos) - Baseado na estabilidade recente
    recent_changes = []
    for i in range(1, min(5, len(historical_prices))):
        change = ((historical_prices[i] - historical_prices[i-1]) / historical_prices[i-1]) * 100
        recent_changes.append(change)
    
    if recent_changes:
        avg_change = sum(recent_changes) / len(recent_changes)
        change_std = math.sqrt(sum((c - avg_change) ** 2 for c in recent_changes) / len(recent_changes))
        if change_std < 1:
            consistency_score = 10
        elif change_std < 3:
            consistency_score = 7
        else:
            consistency_score = 3
    else:
        consistency_score = 5
    
    # Calcular score total
    total_score = round(rsi_score + ma_score + vol_score + momentum_score + consistency_score)
    
    # Garantir que está entre 0-100
    total_score = max(0, min(100, total_score))
    
    # Detalhes para debugging
    score_details = {
        'rsi': {'value': rsi, 'score': round(rsi_score, 1)},
        'moving_averages': {'ma7': round(ma7, 2), 'ma20': round(ma20, 2), 'score': round(ma_score, 1)},
        'volatility': {'value': volatility, 'score': round(vol_score, 1)},
        'momentum': {'change_24h': change_24h, 'score': round(momentum_score, 1)},
        'consistency': {'score': round(consistency_score, 1)},
        'total': total_score
    }
    
    return total_score, score_details

def generate_enhanced_signal(crypto_data, historical_prices):
    """Gerar sinal com reliability score"""
    
    reliability_score, score_details = calculate_reliability_score(crypto_data, historical_prices)
    change_24h = crypto_data['change_24h']
    rsi = score_details['rsi']['value']
    
    # Determinar sinal baseado em múltiplos fatores
    if change_24h > 3 and rsi < 70 and reliability_score >= 70:
        signal = 'BUY'
        confidence = 'HIGH'
    elif change_24h > 1.5 and rsi < 75 and reliability_score >= 60:
        signal = 'BUY'
        confidence = 'MEDIUM'
    elif change_24h < -3 and rsi > 30 and reliability_score >= 70:
        signal = 'SELL'
        confidence = 'HIGH'
    elif change_24h < -1.5 and rsi > 25 and reliability_score >= 60:
        signal = 'SELL'
        confidence = 'MEDIUM'
    else:
        signal = 'HOLD'
        confidence = 'LOW' if reliability_score < 50 else 'MEDIUM'
    
    return {
        'signal': signal,
        'confidence': confidence,
        'reliability_score': reliability_score,
        'score_breakdown': score_details
    }

def get_real_prices():
    """Buscar preços reais da CoinGecko com dados históricos simulados"""
    global last_request_time
    
    try:
        current_time = time.time()
        if current_time - last_request_time < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - (current_time - last_request_time))
        
        print("📡 Buscando preços da CoinGecko...")
        
        all_ids = ','.join([info['id'] for info in SUPPORTED_CRYPTOS.values()])
        
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': all_ids,
            'vs_currencies': 'usd,eur',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        last_request_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Preços atualizados: {len(data)} cryptos")
            
            # Simular dados históricos para cada crypto
            for crypto_id in data.keys():
                if crypto_id not in cache.get('historical', {}):
                    cache.setdefault('historical', {})[crypto_id] = []
                
                # Adicionar preço atual ao histórico
                current_price = data[crypto_id]['usd']
                historical = cache['historical'][crypto_id]
                historical.append(current_price)
                
                # Manter apenas últimos 30 pontos
                if len(historical) > 30:
                    historical.pop(0)
            
            cache['data_source'] = 'coingecko'
            return data
        else:
            print(f"❌ CoinGecko erro {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro CoinGecko: {e}")
        return None

def get_simulated_prices():
    """Dados simulados quando CoinGecko não responde"""
    print("🔄 Usando dados simulados...")
    
    base_prices = {
        'bitcoin': 67000,
        'ethereum': 3500,
        'ripple': 0.6
    }
    
    simulated_data = {}
    
    for crypto_id, base_price in base_prices.items():
        # Simular mudança aleatória
        import random
        change_24h = random.uniform(-8, 8)
        current_price = base_price * (1 + change_24h / 100)
        
        simulated_data[crypto_id] = {
            'usd': current_price,
            'eur': current_price * 0.85,
            'usd_24h_change': change_24h,
            'usd_market_cap': current_price * 19000000,
            'usd_24h_vol': current_price * 500000
        }
        
        # Adicionar ao histórico simulado
        if crypto_id not in cache.get('historical', {}):
            cache.setdefault('historical', {})[crypto_id] = []
        
        historical = cache['historical'][crypto_id]
        historical.append(current_price)
        
        if len(historical) > 30:
            historical.pop(0)
    
    return simulated_data

def update_cache():
    """Atualizar cache com dados reais ou simulados"""
    global cache
    
    if not cache:
        init_cache()
    
    # Tentar obter dados reais
    real_data = get_real_prices()
    
    if real_data:
        cache['prices'] = real_data
        cache['data_source'] = 'coingecko'
        print("✅ Cache atualizado com dados reais")
    else:
        # Fallback para dados simulados
        simulated_data = get_simulated_prices()
        cache['prices'] = simulated_data
        cache['data_source'] = 'simulated'
        print("✅ Cache atualizado com dados simulados")
    
    cache['last_update'] = time.time()
    return True

def is_cache_valid():
    """Verificar se o cache ainda é válido"""
    if not cache or 'last_update' not in cache:
        return False
    return (time.time() - cache['last_update']) < cache['ttl']

def get_crypto_data_enhanced(crypto_key):
    """Obter dados avançados de uma criptomoeda"""
    if not cache:
        init_cache()
    
    if not is_cache_valid():
        update_cache()
    
    crypto_info = SUPPORTED_CRYPTOS.get(crypto_key)
    if not crypto_info:
        return None
    
    crypto_id = crypto_info['id']
    price_data = cache.get('prices', {}).get(crypto_id)
    historical_prices = cache.get('historical', {}).get(crypto_id, [])
    
    if not price_data:
        print(f"❌ Dados não encontrados para {crypto_key}")
        return None
    
    # Dados básicos
    basic_data = {
        'crypto': crypto_key,
        'symbol': crypto_info['symbol'],
        'name': crypto_info['name'],
        'price_usd': price_data.get('usd', 0),
        'price_eur': price_data.get('eur', 0),
        'change_24h': price_data.get('usd_24h_change', 0),
        'market_cap': price_data.get('usd_market_cap', 0),
        'volume_24h': price_data.get('usd_24h_vol', 0),
        'timestamp': datetime.now().isoformat(),
        'data_source': cache.get('data_source', 'unknown')
    }
    
    # Gerar sinal avançado com reliability score
    signal_data = generate_enhanced_signal(basic_data, historical_prices)
    
    # Combinar tudo
    result = {**basic_data, **signal_data}
    
    return result

# === ENDPOINTS ===

@app.route('/')
def home():
    """Página inicial da API"""
    return jsonify({
        'service': 'BitDash Enhanced Trading Signals API',
        'version': 'v3.0_reliability_score',
        'features': [
            'Reliability Score 0-100',
            'RSI Technical Analysis',
            'Moving Averages',
            'Volatility Analysis',
            'Multi-factor Signal Generation'
        ],
        'endpoints': {
            '/api/health': 'Health check',
            '/api/cryptos': 'Supported cryptocurrencies',
            '/api/{crypto}/price': 'Enhanced crypto data with reliability score',
            '/api/signals/all': 'All signals with reliability scores'
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/favicon.ico')
def favicon():
    """Favicon placeholder"""
    return '', 204

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'BitDash Enhanced Trading Signals API',
        'version': 'v3.0_reliability_score',
        'cache_status': cache.get('data_source', 'unknown'),
        'last_update': datetime.fromtimestamp(cache.get('last_update', 0)).isoformat() if cache.get('last_update') else None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/cryptos')
def get_cryptos():
    """Listar criptomoedas suportadas"""
    return jsonify({
        'supported_cryptos': SUPPORTED_CRYPTOS,
        'count': len(SUPPORTED_CRYPTOS),
        'features': [
            'Real-time prices',
            'Reliability Score 0-100',
            'Technical indicators (RSI, MA)',
            'Signal confidence levels'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/<crypto>/price')
def get_crypto_price(crypto):
    """Obter dados avançados de uma criptomoeda específica"""
    try:
        data = get_crypto_data_enhanced(crypto.lower())
        if data:
            return jsonify(data)
        else:
            return jsonify({'error': f'Dados não disponíveis para {crypto}'}), 500
    except Exception as e:
        print(f"❌ Erro no endpoint {crypto}: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/signals/all')
def get_all_enhanced_signals():
    """Obter sinais avançados de todas as criptomoedas"""
    try:
        signals = []
        
        for crypto_key in SUPPORTED_CRYPTOS.keys():
            data = get_crypto_data_enhanced(crypto_key)
            if data:
                signals.append(data)
        
        # Calcular estatísticas gerais
        if signals:
            avg_reliability = sum(s['reliability_score'] for s in signals) / len(signals)
            high_confidence = len([s for s in signals if s['reliability_score'] >= 75])
            medium_confidence = len([s for s in signals if 50 <= s['reliability_score'] < 75])
            low_confidence = len([s for s in signals if s['reliability_score'] < 50])
        else:
            avg_reliability = 0
            high_confidence = medium_confidence = low_confidence = 0
        
        return jsonify({
            'signals': signals,
            'count': len(signals),
            'statistics': {
                'average_reliability': round(avg_reliability, 1),
                'high_confidence_signals': high_confidence,
                'medium_confidence_signals': medium_confidence,
                'low_confidence_signals': low_confidence
            },
            'timestamp': datetime.now().isoformat(),
            'cache_status': cache.get('data_source', 'unknown')
        })
        
    except Exception as e:
        print(f"❌ Erro nos sinais: {e}")
        return jsonify({'error': f'Erro ao gerar sinais: {str(e)}'}), 500

@app.route('/keep-alive')
def keep_alive():
    """Keep alive endpoint para Render"""
    return jsonify({
        'service': 'BitDash Enhanced Trading Signals API',
        'status': 'active',
        'version': 'v3.0_reliability_score',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 INICIANDO API BITDASH COM RELIABILITY SCORE")
    print("=" * 60)
    
    init_cache()
    
    print("🔄 Fazendo primeira atualização de dados...")
    update_cache()
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Servidor iniciando na porta {port}")
    print("✅ API com Reliability Score pronta para uso!")
    
    app.run(host='0.0.0.0', port=port, debug=False)
