# -*- coding: utf-8 -*-
"""
Multi-Crypto Trading Signals API - VERSÃO CORRIGIDA
Simplificada e robusta com inicialização garantida
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

# Suporte a múltiplas criptomoedas
SUPPORTED_CRYPTOS = {
    'bitcoin': {
        'id': 'bitcoin',
        'symbol': 'BTC',
        'name': 'Bitcoin',
        'emoji': '₿'
    },
    'ethereum': {
        'id': 'ethereum',
        'symbol': 'ETH',
        'name': 'Ethereum',
        'emoji': '⟠'
    },
    'xrp': {
        'id': 'ripple',
        'symbol': 'XRP',
        'name': 'XRP',
        'emoji': '◆'
    }
}

# Cache global simplificado
cache = {}
last_request_time = 0
REQUEST_DELAY = 3  # 3 segundos entre requests

def init_cache():
    """Inicializar cache vazio para todas as criptomoedas"""
    global cache
    print("🔄 Inicializando cache...")
    cache = {
        'prices': {},
        'last_update': 0,
        'ttl': 300  # 5 minutos
    }
    print("✅ Cache inicializado")

def is_cache_valid():
    """Verificar se o cache ainda é válido"""
    if not cache or 'last_update' not in cache:
        return False
    return (time.time() - cache['last_update']) < cache['ttl']

def get_real_prices():
    """Buscar preços reais da CoinGecko"""
    global last_request_time
    
    try:
        # Rate limiting
        current_time = time.time()
        if current_time - last_request_time < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - (current_time - last_request_time))
        
        print("📡 Buscando preços da CoinGecko...")
        
        # Buscar todos os preços em uma request
        all_ids = ','.join([info['id'] for info in SUPPORTED_CRYPTOS.values()])
        url = f"{COINGECKO_API}/simple/price"
        params = {
            'ids': all_ids,
            'vs_currencies': 'usd,eur',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=15)
        last_request_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dados recebidos da CoinGecko: {len(data)} cryptos")
            return data
        elif response.status_code == 429:
            print("⚠️ Rate limiting da CoinGecko")
            return None
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao buscar CoinGecko: {e}")
        return None

def get_simulated_prices():
    """Gerar preços simulados como fallback"""
    print("🤖 Gerando preços simulados...")
    
    base_prices = {
        'bitcoin': 115000,
        'ethereum': 3600,
        'ripple': 3.0
    }
    
    simulated = {}
    for crypto_key, crypto_info in SUPPORTED_CRYPTOS.items():
        crypto_id = crypto_info['id']
        base_price = base_prices.get(crypto_id, 1000)
        
        # Variação aleatória ±3%
        variation = random.uniform(-0.03, 0.03)
        price_usd = base_price * (1 + variation)
        price_eur = price_usd * 0.85
        change_24h = random.uniform(-5.0, 5.0)
        
        simulated[crypto_id] = {
            'usd': round(price_usd, 2),
            'eur': round(price_eur, 2),
            'usd_24h_change': round(change_24h, 2)
        }
    
    print(f"✅ Preços simulados gerados: {len(simulated)} cryptos")
    return simulated

def update_cache():
    """Atualizar cache com dados frescos"""
    global cache
    
    print("🔄 Atualizando cache...")
    
    # Tentar dados reais primeiro
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

def get_crypto_data(crypto_key):
    """Obter dados de uma criptomoeda específica"""
    # Garantir que cache existe
    if not cache:
        init_cache()
    
    # Atualizar cache se necessário
    if not is_cache_valid():
        update_cache()
    
    # Obter dados do cache
    crypto_info = SUPPORTED_CRYPTOS.get(crypto_key)
    if not crypto_info:
        return None
    
    crypto_id = crypto_info['id']
    price_data = cache.get('prices', {}).get(crypto_id)
    
    if not price_data:
        print(f"❌ Dados não encontrados para {crypto_key}")
        return None
    
    # Formatar resposta
    result = {
        'crypto': crypto_key,
        'symbol': crypto_info['symbol'],
        'name': crypto_info['name'],
        'price_usd': price_data.get('usd', 0),
        'price_eur': price_data.get('eur', 0),
        'change_24h': price_data.get('usd_24h_change', 0),
        'timestamp': datetime.now().isoformat(),
        'data_source': cache.get('data_source', 'unknown')
    }
    
    return result

# === ENDPOINTS ===

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'service': 'Multi-Crypto Trading Signals API (Fixed)',
        'status': 'healthy',
        'cache_status': 'valid' if is_cache_valid() else 'expired',
        'supported_cryptos': len(SUPPORTED_CRYPTOS),
        'timestamp': datetime.now().isoformat(),
        'version': 'v2.1_fixed'
    })

@app.route('/api/cryptos')
def list_cryptos():
    """Listar criptomoedas suportadas"""
    return jsonify({
        'supported_cryptos': SUPPORTED_CRYPTOS,
        'count': len(SUPPORTED_CRYPTOS),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/<crypto>/price')
def get_crypto_price(crypto):
    """Obter preço de uma criptomoeda"""
    if crypto not in SUPPORTED_CRYPTOS:
        return jsonify({'error': f'Criptomoeda não suportada: {crypto}'}), 400
    
    try:
        data = get_crypto_data(crypto)
        if data:
            return jsonify(data)
        else:
            return jsonify({'error': f'Dados não disponíveis para {crypto}'}), 500
    except Exception as e:
        print(f"❌ Erro no endpoint {crypto}: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/signals/all')
def get_all_signals():
    """Obter sinais de todas as criptomoedas"""
    try:
        signals = []
        
        for crypto_key in SUPPORTED_CRYPTOS.keys():
            data = get_crypto_data(crypto_key)
            if data:
                # Gerar sinal simples baseado na mudança 24h
                change = data.get('change_24h', 0)
                if change > 2:
                    signal = 'BUY'
                    confidence = 'MEDIUM'
                elif change < -2:
                    signal = 'SELL'
                    confidence = 'MEDIUM'
                else:
                    signal = 'HOLD'
                    confidence = 'LOW'
                
                signal_data = {
                    'crypto': crypto_key,
                    'symbol': data['symbol'],
                    'signal': signal,
                    'confidence': confidence,
                    'current_price': {
                        'usd': data['price_usd'],
                        'eur': data['price_eur']
                    },
                    'change_24h': data['change_24h'],
                    'data_source': data['data_source'],
                    'timestamp': data['timestamp']
                }
                
                signals.append(signal_data)
        
        return jsonify({
            'signals': signals,
            'count': len(signals),
            'timestamp': datetime.now().isoformat(),
            'cache_status': cache.get('data_source', 'unknown')
        })
        
    except Exception as e:
        print(f"❌ Erro nos sinais: {e}")
        return jsonify({'error': f'Erro ao gerar sinais: {str(e)}'}), 500

# === KEEP ALIVE ===
@app.route('/keep-alive')
def keep_alive():
    """Keep alive endpoint para Render"""
    return jsonify({
        'service': 'Multi-Crypto Trading Signals API (Fixed)',
        'status': 'active',
        'timestamp': datetime.now().isoformat()
    })

# === STARTUP ===
if __name__ == '__main__':
    print("🚀 INICIANDO API MULTI-CRYPTO CORRIGIDA")
    print("=" * 50)
    
    # Inicializar cache
    init_cache()
    
    # Fazer primeira atualização
    print("🔄 Fazendo primeira atualização de dados...")
    update_cache()
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Servidor iniciando na porta {port}")
    print("✅ API pronta para uso!")
    
    app.run(host='0.0.0.0', port=port, debug=False)
