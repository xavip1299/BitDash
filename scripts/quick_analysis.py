#!/usr/bin/env python3
"""
Análise Rápida de Bitcoin
Script standalone para análise instantânea
"""

import sys
import os
from pathlib import Path

# Adicionar API path
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir / 'api'))

import requests
import json
from datetime import datetime
import pytz

# Configuração
API_URL = "http://localhost:5000"
COINGECKO_API = "https://api.coingecko.com/api/v3"

def get_bitcoin_price_direct():
    """Obter preço diretamente da CoinGecko"""
    try:
        url = f"{COINGECKO_API}/simple/price"
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'eur',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            btc_data = data.get('bitcoin', {})
            
            return {
                'price': btc_data.get('eur', 0),
                'change_24h': btc_data.get('eur_24h_change', 0)
            }
    except Exception as e:
        print(f"❌ Erro ao obter preço: {e}")
    
    return None

def get_signal_from_api():
    """Tentar obter sinal da API local"""
    try:
        response = requests.get(f"{API_URL}/api/detailed-signal", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data')
    except:
        pass  # API pode não estar rodando
    
    return None

def analyze_price_trend(current_price, change_24h):
    """Análise simples baseada em mudança de preço"""
    if change_24h > 5:
        return {
            'signal': 'STRONG_BUY',
            'score': 75,
            'color': '🟢',
            'reasoning': f'Alta de {change_24h:.1f}% em 24h'
        }
    elif change_24h > 2:
        return {
            'signal': 'BUY', 
            'score': 65,
            'color': '🟢',
            'reasoning': f'Alta de {change_24h:.1f}% em 24h'
        }
    elif change_24h > -2:
        return {
            'signal': 'NEUTRAL',
            'score': 50,
            'color': '🟡',
            'reasoning': f'Variação baixa: {change_24h:.1f}%'
        }
    elif change_24h > -5:
        return {
            'signal': 'SELL',
            'score': 35,
            'color': '🔴',
            'reasoning': f'Queda de {change_24h:.1f}% em 24h'
        }
    else:
        return {
            'signal': 'STRONG_SELL',
            'score': 25,
            'color': '🔴',
            'reasoning': f'Queda acentuada: {change_24h:.1f}%'
        }

def display_analysis(price_data, signal_data):
    """Exibir análise formatada"""
    print("\n" + "="*50)
    print("🚀 ANÁLISE RÁPIDA BITCOIN")
    print("="*50)
    
    # Preço atual
    price = price_data['price']
    change_24h = price_data['change_24h']
    change_emoji = '🟢' if change_24h > 0 else '🔴' if change_24h < 0 else '⚪'
    change_text = f"+{change_24h:.1f}%" if change_24h > 0 else f"{change_24h:.1f}%"
    
    print(f"💰 PREÇO ATUAL: €{price:,.2f}")
    print(f"{change_emoji} VARIAÇÃO 24H: {change_text}")
    
    # Sinal
    if signal_data:
        color = signal_data.get('color', '🟡')
        signal = signal_data.get('signal', 'NEUTRAL')
        score = signal_data.get('score', 50)
        
        print(f"\n{color} SINAL: {signal}")
        print(f"📊 SCORE: {score}/100")
        
        # Stop Loss e Take Profit se disponível
        if signal_data.get('stop_loss'):
            print(f"🛡️  STOP LOSS: €{signal_data['stop_loss']:,.2f}")
        if signal_data.get('take_profit'):
            print(f"🎯 TAKE PROFIT: €{signal_data['take_profit']:,.2f}")
        
        # Reasoning
        reasoning = signal_data.get('reasoning')
        if reasoning:
            if isinstance(reasoning, list):
                print(f"\n📋 ANÁLISE:")
                for reason in reasoning[:3]:  # Mostrar apenas 3 primeiros
                    print(f"  • {reason}")
            else:
                print(f"\n📋 ANÁLISE: {reasoning}")
    
    # Timestamp
    timestamp = datetime.now(pytz.timezone('Europe/Lisbon')).strftime('%d/%m/%Y %H:%M:%S')
    print(f"\n⏰ ATUALIZADO: {timestamp}")
    print("="*50)

def main():
    """Função principal"""
    print("⚡ Iniciando análise rápida...")
    
    # Obter dados de preço
    price_data = get_bitcoin_price_direct()
    
    if not price_data:
        print("❌ Erro ao obter dados de preço")
        return
    
    # Tentar obter sinal da API
    signal_data = get_signal_from_api()
    
    if not signal_data:
        print("ℹ️  API local não disponível, usando análise simples...")
        signal_data = analyze_price_trend(price_data['price'], price_data['change_24h'])
    else:
        print("✅ Usando análise técnica avançada da API")
    
    # Exibir resultados
    display_analysis(price_data, signal_data)
    
    # Recomendação final
    score = signal_data.get('score', 50)
    if score >= 70:
        print("\n🎯 RECOMENDAÇÃO: Considerar compra")
        print("⚠️  Sempre defina stop loss!")
    elif score <= 30:
        print("\n🎯 RECOMENDAÇÃO: Considerar venda")
        print("⚠️  Mercado pode estar em correção")
    else:
        print("\n🎯 RECOMENDAÇÃO: Aguardar sinal mais claro")
        print("ℹ️  Mercado neutro, observar desenvolvimento")

if __name__ == "__main__":
    main()
