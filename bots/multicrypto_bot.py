#!/usr/bin/env python3
"""
Multi-Crypto Telegram Bot - Bitcoin, Ethereum & XRP
Bot expandido para enviar sinais de múltiplas criptomoedas
"""

import requests
import os
from datetime import datetime
import time
import threading
import json

# Configurações
BOT_TOKEN = os.getenv('BOT_TOKEN', '8343884144:AAETIlOVnA69fI-N4E-vzNJcQHTh0gDBz0I')
CHAT_ID = os.getenv('CHAT_ID', '1064066035')
API_BASE_URL = os.getenv('API_URL', 'https://bitdash-9dnk.onrender.com')

# Configurações das criptomoedas
CRYPTOS_CONFIG = {
    'bitcoin': {
        'emoji': '₿',
        'color_emoji': '🟠',
        'name': 'Bitcoin',
        'enabled': True
    },
    'ethereum': {
        'emoji': '⟠',
        'color_emoji': '🔵',
        'name': 'Ethereum',
        'enabled': True
    },
    'xrp': {
        'emoji': '◆',
        'color_emoji': '⚫',
        'name': 'XRP',
        'enabled': True
    }
}

def send_telegram_message(message, parse_mode='HTML'):
    """Enviar mensagem para o Telegram"""
    try:
        telegram_api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }
        
        response = requests.post(telegram_api, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                return True, result['result']['message_id']
            else:
                print(f"❌ Erro Telegram: {result}")
                return False, None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False, None

def get_crypto_signal(crypto):
    """Obter sinal de uma criptomoeda específica"""
    try:
        url = f"{API_BASE_URL}/api/{crypto}/signal"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro ao obter sinal {crypto}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro de conexão {crypto}: {e}")
        return None

def get_all_signals():
    """Obter sinais de todas as criptomoedas"""
    try:
        url = f"{API_BASE_URL}/api/signals/all"
        response = requests.get(url, timeout=20)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro ao obter todos os sinais: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None

def format_signal_message(signal_data):
    """Formatar mensagem de sinal individual"""
    crypto = signal_data['crypto']
    config = CRYPTOS_CONFIG.get(crypto, {})
    
    # Emoji baseado no sinal
    if signal_data['signal'] == 'BUY':
        signal_emoji = '🟢'
        action_emoji = '📈'
    elif signal_data['signal'] == 'SELL':
        signal_emoji = '🔴'
        action_emoji = '📉'
    else:
        signal_emoji = '🟡'
        action_emoji = '➡️'
    
    # Emoji de confiança
    confidence_emoji = {
        'HIGH': '🔥',
        'MEDIUM': '⚡',
        'LOW': '⚠️'
    }.get(signal_data['confidence'], '❓')
    
    # Formatação da mensagem
    message = f"""
{config.get('color_emoji', '⚪')} <b>{signal_data['name'].upper()} {config.get('emoji', '')}</b>

{signal_emoji} <b>SINAL:</b> {signal_data['signal']} {action_emoji}
🎯 <b>Score:</b> {signal_data['score']}/100
{confidence_emoji} <b>Confiança:</b> {signal_data['confidence']}

💰 <b>Preço Atual:</b>
   💵 ${signal_data['current_price']['usd']:,.2f}
   💶 €{signal_data['current_price']['eur']:,.2f}

📊 <b>Análise Técnica:</b>
   📈 RSI: {signal_data['rsi']}
   🎢 Tendência: {signal_data['trend']['trend']}
   📊 Força: {signal_data['trend']['strength']}%
   📈 24h: {signal_data['change_24h']:+.2f}%

🎯 <b>Trading:</b>
   🛑 Stop Loss: ${signal_data['stop_loss']:,.2f}
   🎯 Take Profit: ${signal_data['take_profit']:,.2f}
   ⚖️ Risk/Reward: {signal_data['risk_reward_ratio']:.1f}:1
   📊 Volatilidade: {signal_data['volatility_estimate']:.1f}%

🔍 <b>Fatores de Confiança:</b>"""
    
    # Adicionar fatores de confiança
    for factor in signal_data['confidence_factors']:
        factor_emoji = {
            'RSI_STRONG_OVERSOLD': '📉🔥',
            'RSI_OVERSOLD': '📉',
            'RSI_STRONG_OVERBOUGHT': '📈🔥',
            'RSI_OVERBOUGHT': '📈',
            'STRONG_UPTREND': '🚀',
            'UPTREND': '📈',
            'STRONG_DOWNTREND': '📉🔥',
            'DOWNTREND': '📉',
            'HIGH_VOLUME_CONFIRMATION': '🔊',
            'HIGH_MOMENTUM': '⚡'
        }.get(factor, '✅')
        
        message += f"\n   {factor_emoji} {factor.replace('_', ' ')}"
    
    message += f"""

🕐 <i>Atualizado: {datetime.now().strftime('%H:%M:%S')}</i>
🤖 <i>Multi-Crypto Bot v1.0</i>"""
    
    return message

def format_summary_message(signals_data):
    """Formatar mensagem de resumo de todos os sinais"""
    signals = signals_data['signals']
    
    message = f"""
🚀 <b>RESUMO MULTI-CRYPTO</b>
📊 <b>Sinais de {len(signals)} Criptomoedas</b>

"""
    
    # Resumo por criptomoeda
    for crypto, signal in signals.items():
        config = CRYPTOS_CONFIG.get(crypto, {})
        
        if signal['signal'] == 'BUY':
            signal_emoji = '🟢'
        elif signal['signal'] == 'SELL':
            signal_emoji = '🔴'
        else:
            signal_emoji = '🟡'
        
        confidence_emoji = {
            'HIGH': '🔥',
            'MEDIUM': '⚡',
            'LOW': '⚠️'
        }.get(signal['confidence'], '❓')
        
        message += f"""{config.get('color_emoji', '⚪')} <b>{signal['symbol']}</b> {signal_emoji} {signal['signal']} ({signal['score']}/100) {confidence_emoji}
   💰 ${signal['current_price']['usd']:,.2f} | 📈 {signal['change_24h']:+.2f}%

"""
    
    # Estatísticas gerais
    buy_count = sum(1 for s in signals.values() if s['signal'] == 'BUY')
    sell_count = sum(1 for s in signals.values() if s['signal'] == 'SELL')
    hold_count = sum(1 for s in signals.values() if s['signal'] == 'HOLD')
    high_conf_count = sum(1 for s in signals.values() if s['confidence'] == 'HIGH')
    
    message += f"""📊 <b>Estatísticas:</b>
🟢 Buy: {buy_count} | 🔴 Sell: {sell_count} | 🟡 Hold: {hold_count}
🔥 Alta Confiança: {high_conf_count}/{len(signals)}

🕐 <i>Atualizado: {datetime.now().strftime('%H:%M:%S')}</i>
🤖 <i>Multi-Crypto Bot v1.0</i>"""
    
    return message

def send_individual_signals():
    """Enviar sinais individuais de cada criptomoeda"""
    print("🚀 Enviando sinais individuais...")
    
    for crypto, config in CRYPTOS_CONFIG.items():
        if not config.get('enabled', True):
            continue
            
        print(f"📊 Obtendo sinal {config['name']}...")
        signal = get_crypto_signal(crypto)
        
        if signal:
            message = format_signal_message(signal)
            success, msg_id = send_telegram_message(message)
            
            if success:
                print(f"✅ {config['name']}: Enviado (ID: {msg_id})")
            else:
                print(f"❌ {config['name']}: Falha no envio")
        else:
            print(f"❌ {config['name']}: Falha ao obter sinal")
        
        # Pausa entre envios para evitar rate limit
        time.sleep(2)

def send_summary_signal():
    """Enviar resumo de todos os sinais"""
    print("📊 Enviando resumo multi-crypto...")
    
    signals_data = get_all_signals()
    
    if signals_data and signals_data.get('signals'):
        message = format_summary_message(signals_data)
        success, msg_id = send_telegram_message(message)
        
        if success:
            print(f"✅ Resumo enviado (ID: {msg_id})")
            return True
        else:
            print("❌ Falha ao enviar resumo")
            return False
    else:
        print("❌ Falha ao obter sinais para resumo")
        return False

def send_startup_message():
    """Enviar mensagem de inicialização do bot"""
    message = f"""
🤖 <b>MULTI-CRYPTO BOT INICIADO</b>

🚀 <b>Criptomoedas Monitoradas:</b>
{chr(10).join([f"   {config['color_emoji']} {config['name']} {config['emoji']}" for config in CRYPTOS_CONFIG.values() if config.get('enabled')])}

📡 <b>API:</b> {API_BASE_URL}
🔄 <b>Frequência:</b> Sinais automáticos
⚡ <b>Versão:</b> Multi-Crypto v1.0

🎯 <b>Funcionalidades:</b>
   📊 Análise técnica individual
   🔍 Resumo consolidado
   🎯 Sinais BUY/SELL/HOLD
   🛡️ Gerenciamento de risco

✅ <b>Bot online e monitorando!</b>

🕐 <i>Iniciado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>"""
    
    success, msg_id = send_telegram_message(message)
    
    if success:
        print(f"✅ Mensagem de startup enviada (ID: {msg_id})")
    else:
        print("❌ Falha ao enviar mensagem de startup")

def test_api_connection():
    """Testar conexão com a API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API conectada: {data.get('service', 'Unknown')} v{data.get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ API erro: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro conexão API: {e}")
        return False

def main():
    """Função principal do bot"""
    print("🚀 INICIANDO MULTI-CRYPTO TELEGRAM BOT")
    print("=" * 50)
    print(f"🤖 Bot Token: {BOT_TOKEN[:20]}...")
    print(f"💬 Chat ID: {CHAT_ID}")
    print(f"📡 API URL: {API_BASE_URL}")
    print(f"🎯 Criptomoedas: {', '.join(CRYPTOS_CONFIG.keys())}")
    print()
    
    # Testar conexões
    print("🧪 Testando conexões...")
    api_ok = test_api_connection()
    
    if not api_ok:
        print("❌ API não disponível. Tentando novamente em 30s...")
        time.sleep(30)
        api_ok = test_api_connection()
    
    if api_ok:
        print("✅ Todas as conexões OK!")
        
        # Enviar mensagem de startup
        send_startup_message()
        
        # Enviar primeiro resumo
        time.sleep(5)
        send_summary_signal()
        
        print("\n🎉 BOT MULTI-CRYPTO ATIVO!")
        print("📱 Verifica o teu Telegram para ver os sinais!")
        
        return True
    else:
        print("❌ Falha na inicialização - API não disponível")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Bot inicializado com sucesso!")
    else:
        print("\n❌ Falha na inicialização do bot")
        exit(1)
