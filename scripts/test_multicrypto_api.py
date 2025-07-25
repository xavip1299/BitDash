#!/usr/bin/env python3
"""
Teste da API Multi-Crypto - Bitcoin, Ethereum & XRP
Testa todas as funcionalidades da nova API expandida
"""

import requests
import json
import time
from datetime import datetime

# Configurações
API_BASE_URL = "https://bitdash-9dnk.onrender.com"
LOCAL_API_URL = "http://localhost:5000"  # Para testes locais

# Usar API local para testes
API_URL = LOCAL_API_URL

def test_api_health():
    """Testar endpoint de saúde da API"""
    print("🏥 TESTE DE SAÚDE DA API")
    print("-" * 40)
    
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"🔢 Versão: {data['version']}")
            print(f"📊 Criptomoedas: {data['supported_cryptos']}")
            print(f"⏰ Uptime: {data['uptime_start']}")
            print(f"🎯 Melhorias: {len(data['improvements'])}")
            return True
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_list_cryptos():
    """Testar listagem de criptomoedas"""
    print("\n📋 TESTE DE LISTAGEM DE CRIPTOMOEDAS")
    print("-" * 40)
    
    try:
        response = requests.get(f"{API_URL}/api/cryptos", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total de criptomoedas: {data['count']}")
            
            for crypto_key, crypto_info in data['supported_cryptos'].items():
                print(f"   {crypto_info['emoji']} {crypto_info['name']} ({crypto_info['symbol']})")
            
            return True
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_individual_prices():
    """Testar preços individuais"""
    print("\n💰 TESTE DE PREÇOS INDIVIDUAIS")
    print("-" * 40)
    
    cryptos = ['bitcoin', 'ethereum', 'xrp']
    results = {}
    
    for crypto in cryptos:
        try:
            response = requests.get(f"{API_URL}/api/{crypto}/price", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results[crypto] = data
                print(f"✅ {crypto.upper()}:")
                print(f"   💵 ${data['price_usd']:,.2f}")
                print(f"   💶 €{data['price_eur']:,.2f}")
                print(f"   📈 24h: {data['change_24h']:+.2f}%")
                print(f"   📊 Volume: ${data['volume_24h']:,.0f}")
            else:
                print(f"❌ {crypto.upper()}: Erro HTTP {response.status_code}")
                results[crypto] = None
                
        except Exception as e:
            print(f"❌ {crypto.upper()}: Erro {e}")
            results[crypto] = None
        
        time.sleep(1)  # Pausa entre requests
    
    return results

def test_individual_signals():
    """Testar sinais individuais"""
    print("\n🎯 TESTE DE SINAIS INDIVIDUAIS")
    print("-" * 40)
    
    cryptos = ['bitcoin', 'ethereum', 'xrp']
    results = {}
    
    for crypto in cryptos:
        try:
            response = requests.get(f"{API_URL}/api/{crypto}/signal", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results[crypto] = data
                print(f"✅ {data['name'].upper()} {data['emoji']}:")
                print(f"   🎯 Sinal: {data['signal']} (Score: {data['score']}/100)")
                print(f"   🔥 Confiança: {data['confidence']}")
                print(f"   💰 Preço: ${data['current_price']['usd']:,.2f}")
                print(f"   📊 RSI: {data['rsi']}")
                print(f"   📈 Tendência: {data['trend']['trend']}")
                print(f"   🛑 Stop Loss: ${data['stop_loss']:,.2f}")
                print(f"   🎯 Take Profit: ${data['take_profit']:,.2f}")
                print(f"   ⚖️ R/R: {data['risk_reward_ratio']:.1f}:1")
                print(f"   🔍 Fatores: {len(data['confidence_factors'])}")
            else:
                print(f"❌ {crypto.upper()}: Erro HTTP {response.status_code}")
                results[crypto] = None
                
        except Exception as e:
            print(f"❌ {crypto.upper()}: Erro {e}")
            results[crypto] = None
        
        time.sleep(2)  # Pausa entre requests
    
    return results

def test_all_signals():
    """Testar endpoint de todos os sinais"""
    print("\n🚀 TESTE DE TODOS OS SINAIS")
    print("-" * 40)
    
    try:
        response = requests.get(f"{API_URL}/api/signals/all", timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            signals = data['signals']
            
            print(f"✅ Obtidos {data['count']} sinais:")
            
            # Estatísticas
            buy_signals = [s for s in signals.values() if s['signal'] == 'BUY']
            sell_signals = [s for s in signals.values() if s['signal'] == 'SELL']
            hold_signals = [s for s in signals.values() if s['signal'] == 'HOLD']
            high_conf = [s for s in signals.values() if s['confidence'] == 'HIGH']
            
            print(f"   🟢 BUY: {len(buy_signals)}")
            print(f"   🔴 SELL: {len(sell_signals)}")
            print(f"   🟡 HOLD: {len(hold_signals)}")
            print(f"   🔥 Alta Confiança: {len(high_conf)}")
            
            # Detalhes de cada sinal
            for crypto, signal in signals.items():
                emoji = '🟢' if signal['signal'] == 'BUY' else '🔴' if signal['signal'] == 'SELL' else '🟡'
                conf_emoji = '🔥' if signal['confidence'] == 'HIGH' else '⚡' if signal['confidence'] == 'MEDIUM' else '⚠️'
                
                print(f"   {emoji} {signal['symbol']}: {signal['signal']} ({signal['score']}/100) {conf_emoji}")
            
            return data
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def test_technical_analysis():
    """Testar análise técnica individual"""
    print("\n📊 TESTE DE ANÁLISE TÉCNICA")
    print("-" * 40)
    
    cryptos = ['bitcoin', 'ethereum', 'xrp']
    
    for crypto in cryptos:
        try:
            response = requests.get(f"{API_URL}/api/{crypto}/technical-analysis", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data['name'].upper()}:")
                print(f"   📊 RSI: {data['technical_indicators']['rsi']}")
                print(f"   📈 Tendência: {data['technical_indicators']['trend']['trend']}")
                print(f"   💪 Força: {data['technical_indicators']['trend']['strength']}%")
                print(f"   📊 Períodos: {data['historical_summary']['periods']}")
                
                price_range = data['historical_summary']['price_range']
                print(f"   💰 Min: ${price_range['min']:,.2f}")
                print(f"   💰 Max: ${price_range['max']:,.2f}")
                print(f"   💰 Média: ${price_range['avg']:,.2f}")
            else:
                print(f"❌ {crypto.upper()}: Erro HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {crypto.upper()}: Erro {e}")
        
        time.sleep(1)

def test_compatibility_routes():
    """Testar rotas de compatibilidade (Bitcoin)"""
    print("\n🔄 TESTE DE COMPATIBILIDADE (Rotas Antigas)")
    print("-" * 40)
    
    old_routes = [
        '/api/bitcoin-price',
        '/api/detailed-signal',
        '/api/technical-analysis'
    ]
    
    for route in old_routes:
        try:
            response = requests.get(f"{API_URL}{route}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {route}: OK")
            else:
                print(f"❌ {route}: Erro {response.status_code}")
                
        except Exception as e:
            print(f"❌ {route}: Erro {e}")

def generate_test_report(health_ok, cryptos_ok, prices, signals, all_signals):
    """Gerar relatório de testes"""
    print("\n" + "=" * 60)
    print("📋 RELATÓRIO FINAL DOS TESTES")
    print("=" * 60)
    
    # Status geral
    print(f"🏥 API Health: {'✅ OK' if health_ok else '❌ FALHA'}")
    print(f"📋 Lista Cryptos: {'✅ OK' if cryptos_ok else '❌ FALHA'}")
    
    # Preços
    if prices:
        price_success = sum(1 for p in prices.values() if p is not None)
        print(f"💰 Preços: {price_success}/3 ✅")
    else:
        print("💰 Preços: ❌ FALHA")
    
    # Sinais individuais
    if signals:
        signal_success = sum(1 for s in signals.values() if s is not None)
        print(f"🎯 Sinais Individuais: {signal_success}/3 ✅")
    else:
        print("🎯 Sinais Individuais: ❌ FALHA")
    
    # Todos os sinais
    if all_signals:
        print(f"🚀 Todos os Sinais: ✅ OK ({all_signals['count']} sinais)")
    else:
        print("🚀 Todos os Sinais: ❌ FALHA")
    
    # Resumo de performance
    total_tests = 5
    passed_tests = sum([
        health_ok,
        cryptos_ok,
        bool(prices and any(prices.values())),
        bool(signals and any(signals.values())),
        bool(all_signals)
    ])
    
    print(f"\n🏆 RESULTADO FINAL: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM! API Multi-Crypto funcionando perfeitamente!")
    elif passed_tests >= 3:
        print("⚡ Maioria dos testes passaram. API funcional com pequenos problemas.")
    else:
        print("⚠️ Muitos testes falharam. Verificar configuração da API.")
    
    print(f"\n🕐 Testes concluídos: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

def main():
    """Função principal dos testes"""
    print("🚀 INICIANDO TESTES DA API MULTI-CRYPTO")
    print("=" * 60)
    print(f"🌐 URL da API: {API_URL}")
    print(f"🎯 Criptomoedas: Bitcoin, Ethereum, XRP")
    print(f"⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Executar testes
    health_ok = test_api_health()
    cryptos_ok = test_list_cryptos()
    prices = test_individual_prices()
    signals = test_individual_signals()
    all_signals = test_all_signals()
    
    # Testes adicionais
    test_technical_analysis()
    test_compatibility_routes()
    
    # Relatório final
    generate_test_report(health_ok, cryptos_ok, prices, signals, all_signals)

if __name__ == "__main__":
    main()
