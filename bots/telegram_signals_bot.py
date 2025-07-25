#!/usr/bin/env python3
"""
Bitcoin Trading Signals Bot - Versão Principal
Bot integrado com configuração local
"""

import sys
import os
from pathlib import Path

# Adicionar paths para imports
current_dir = Path(__file__).parent.parent
sys.path.extend([
    str(current_dir / 'config'),
    str(current_dir / 'api')
])

import requests
import json
import time
from datetime import datetime
import pytz

# Tentar importar configuração local
try:
    from telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    bot_token = TELEGRAM_BOT_TOKEN
    chat_id = TELEGRAM_CHAT_ID
    api_url = "http://localhost:5000"  # API local
except ImportError:
    # Fallback para variáveis de ambiente
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    api_url = os.getenv('API_URL', 'http://localhost:5000')

class BitcoinTradingBot:
    def __init__(self):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = api_url
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("❌ Bot token e chat ID devem estar configurados!")
        
        self.telegram_api = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_signal_score = None
        self.last_signal_type = None
        
        print(f"🤖 Bitcoin Trading Bot iniciado!")
        print(f"📊 API: {self.api_url}")
        print(f"💬 Chat ID: {self.chat_id}")
    
    def send_telegram_message(self, message, parse_mode='HTML'):
        """Enviar mensagem para Telegram"""
        try:
            url = f"{self.telegram_api}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            return False
    
    def get_trading_signal(self):
        """Obter sinal da API local"""
        try:
            response = requests.get(f"{self.api_url}/api/detailed-signal", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data')
            
            print(f"❌ API erro: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao obter sinal: {e}")
            return None
    
    def format_signal_message(self, signal_data):
        """Formatar mensagem do sinal"""
        if not signal_data:
            return None
        
        signal_type = signal_data.get('signal', 'NEUTRAL')
        score = signal_data.get('score', 50)
        color = signal_data.get('color', '🟡')
        current_price = signal_data.get('current_price', 0)
        stop_loss = signal_data.get('stop_loss')
        take_profit = signal_data.get('take_profit')
        price_change_24h = signal_data.get('price_change_24h', 0)
        
        # Emoji baseado no sinal
        if 'BUY' in signal_type.upper():
            trend_emoji = '📈'
            action = 'COMPRAR'
        elif 'SELL' in signal_type.upper():
            trend_emoji = '📉'
            action = 'VENDER'
        else:
            trend_emoji = '➡️'
            action = 'AGUARDAR'
        
        change_emoji = '🟢' if price_change_24h > 0 else '🔴' if price_change_24h < 0 else '⚪'
        change_text = f"+{price_change_24h:.1f}%" if price_change_24h > 0 else f"{price_change_24h:.1f}%"
        
        message = f"""
{color} <b>BITCOIN TRADING SIGNAL</b> {color}

{trend_emoji} <b>AÇÃO:</b> {action}
📊 <b>SCORE:</b> {score}/100
💰 <b>PREÇO:</b> €{current_price:,.2f}
{change_emoji} <b>24h:</b> {change_text}

🛡️ <b>GESTÃO DE RISCO:</b>
• Stop Loss: €{stop_loss:,.2f}
• Take Profit: €{take_profit:,.2f}

🔍 <b>TIPO:</b> {signal_type.replace('_', ' ')}
⏰ <b>HORA:</b> {datetime.now(pytz.timezone('Europe/Lisbon')).strftime('%H:%M:%S')}

<i>🏠 Sinal local • Dashboard Bitcoin</i>
        """.strip()
        
        return message
    
    def should_send_alert(self, signal_data):
        """Verificar se deve enviar alerta"""
        if not signal_data:
            return False
        
        current_score = signal_data.get('score', 50)
        current_signal = signal_data.get('signal', 'NEUTRAL')
        
        # Primeiro sinal
        if self.last_signal_score is None:
            return True
        
        # Mudança significativa no score ou tipo
        score_change = abs(current_score - self.last_signal_score)
        signal_changed = current_signal != self.last_signal_type
        extreme_score = current_score > 80 or current_score < 20
        
        return score_change > 10 or signal_changed or extreme_score
    
    def run_once(self):
        """Executar uma verificação"""
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Verificando sinal...")
        
        signal_data = self.get_trading_signal()
        
        if signal_data:
            if self.should_send_alert(signal_data):
                message = self.format_signal_message(signal_data)
                
                if message and self.send_telegram_message(message):
                    print(f"✅ Sinal enviado: {signal_data.get('signal')} (Score: {signal_data.get('score')})")
                    
                    self.last_signal_score = signal_data.get('score')  
                    self.last_signal_type = signal_data.get('signal')
                else:
                    print("❌ Falha ao enviar sinal")
            else:
                print(f"ℹ️  Sem mudanças significativas (Score: {signal_data.get('score')})")
        else:
            print("❌ Erro ao obter sinal da API")
    
    def run_continuous(self, interval_minutes=15):
        """Executar continuamente"""
        print(f"🔄 Bot executando a cada {interval_minutes} minutos")
        print("🛑 Pressione Ctrl+C para parar")
        
        # Message inicial
        self.send_telegram_message("🤖 <b>Bitcoin Bot ONLINE</b>\n\n📊 Monitoramento iniciado (Local)")
        
        try:
            while True:
                self.run_once()
                print(f"💤 Aguardando {interval_minutes} minutos...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n⏹️  Bot interrompido")
            self.send_telegram_message("🛑 <b>Bitcoin Bot OFFLINE</b>\n\nMonitoramento interrompido.")

def main():
    """Função principal"""
    try:
        bot = BitcoinTradingBot()
        
        print("\n🚀 BITCOIN TRADING BOT")
        print("=" * 40)
        print("1. 🔄 Executar continuamente (15 min)")
        print("2. ⚡ Verificação única")
        print("3. 🧪 Testar conectividade")
        print("0. ❌ Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            bot.run_continuous()
        elif choice == '2':
            bot.run_once()
        elif choice == '3':
            print("🧪 Testando...")
            signal = bot.get_trading_signal()
            if signal:
                print(f"✅ API OK - Score: {signal.get('score')}")
            else:
                print("❌ API não responde")
        elif choice == '0':
            print("👋 Até logo!")
        else:
            print("❌ Opção inválida")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
