#!/usr/bin/env python3
"""
Bitcoin Trading Signals Bot para Cloud
Envia sinais automáticos com score, SL/TP e alertas green/red
"""

import requests
import json
import time
import os
from datetime import datetime
import pytz

class BitcoinSignalsBot:
    def __init__(self):
        # Configurações do bot
        self.bot_token = os.getenv('BOT_TOKEN')
        self.chat_id = os.getenv('CHAT_ID')
        self.api_url = os.getenv('API_URL', 'https://bitcoin-trading-api.onrender.com')
        
        # Validar configurações
        if not self.bot_token or not self.chat_id:
            raise ValueError("BOT_TOKEN e CHAT_ID devem estar definidos nas variáveis de ambiente")
        
        self.telegram_api = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_signal_score = None
        self.last_signal_type = None
        
        print(f"🤖 Bot iniciado!")
        print(f"📊 API: {self.api_url}")
        print(f"💬 Chat ID: {self.chat_id}")
        
    def send_telegram_message(self, message, parse_mode='HTML'):
        """Enviar mensagem para o Telegram"""
        try:
            url = f"{self.telegram_api}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Erro ao enviar mensagem: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no envio: {e}")
            return False
    
    def get_trading_signal(self):
        """Obter sinal de trading da API"""
        try:
            response = requests.get(f"{self.api_url}/api/detailed-signal", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data')
            
            print(f"❌ Erro na API: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao obter sinal: {e}")
            return None
    
    def format_signal_message(self, signal_data):
        """Formatar mensagem do sinal"""
        if not signal_data:
            return None
        
        # Extrair dados
        signal_type = signal_data.get('signal', 'NEUTRAL')
        score = signal_data.get('score', 50)
        color = signal_data.get('color', '🟡')
        current_price = signal_data.get('current_price', 0)
        stop_loss = signal_data.get('stop_loss')
        take_profit = signal_data.get('take_profit')
        price_change_24h = signal_data.get('price_change_24h', 0)
        
        # Emoji baseado no tipo de sinal
        if 'BUY' in signal_type.upper():
            trend_emoji = '📈'
            action = 'COMPRAR'
        elif 'SELL' in signal_type.upper():
            trend_emoji = '📉'
            action = 'VENDER'
        else:
            trend_emoji = '➡️'
            action = 'AGUARDAR'
        
        # Formatação do preço change
        change_emoji = '🟢' if price_change_24h > 0 else '🔴' if price_change_24h < 0 else '⚪'
        change_text = f"+{price_change_24h:.1f}%" if price_change_24h > 0 else f"{price_change_24h:.1f}%"
        
        # Construir mensagem
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

<i>🤖 Sinal automático • Sempre faça sua própria análise</i>
        """.strip()
        
        return message
    
    def should_send_alert(self, signal_data):
        """Verificar se deve enviar alerta"""
        if not signal_data:
            return False
        
        current_score = signal_data.get('score', 50)
        current_signal = signal_data.get('signal', 'NEUTRAL')
        
        # Enviar se:
        # 1. Primeiro sinal
        # 2. Mudança significativa no score (>10 pontos)
        # 3. Mudança no tipo de sinal
        # 4. Score muito alto (>80) ou muito baixo (<20)
        
        if self.last_signal_score is None:
            return True
        
        score_change = abs(current_score - self.last_signal_score)
        signal_changed = current_signal != self.last_signal_type
        extreme_score = current_score > 80 or current_score < 20
        
        if score_change > 10 or signal_changed or extreme_score:
            return True
        
        return False
    
    def run_continuous(self, interval_minutes=15):
        """Executar bot continuamente"""
        print(f"🔄 Bot rodando com intervalo de {interval_minutes} minutos")
        
        # Enviar mensagem de início
        self.send_telegram_message("🤖 <b>Bitcoin Signals Bot ONLINE</b>\n\n📊 Monitoramento automático iniciado!\n🕐 Sinais a cada 15 minutos")
        
        while True:
            try:
                print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Verificando sinais...")
                
                # Obter sinal atual
                signal_data = self.get_trading_signal()
                
                if signal_data:
                    # Verificar se deve enviar alerta
                    if self.should_send_alert(signal_data):
                        message = self.format_signal_message(signal_data)
                        
                        if message and self.send_telegram_message(message):
                            print(f"✅ Signal enviado: {signal_data.get('signal')} (Score: {signal_data.get('score')})")
                            
                            # Atualizar últimos valores
                            self.last_signal_score = signal_data.get('score')
                            self.last_signal_type = signal_data.get('signal')
                        else:
                            print("❌ Falha ao enviar sinal")
                    else:
                        print(f"ℹ️  Sem mudanças significativas (Score: {signal_data.get('score')})")
                else:
                    print("❌ Erro ao obter dados da API")
                
                # Aguardar próximo ciclo
                print(f"💤 Aguardando {interval_minutes} minutos...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n⏹️  Bot interrompido pelo usuário")
                self.send_telegram_message("🛑 <b>Bitcoin Signals Bot OFFLINE</b>\n\nMonitoramento interrompido.")
                break
            except Exception as e:
                print(f"❌ Erro no loop principal: {e}")
                time.sleep(60)  # Aguardar 1 minuto antes de tentar novamente

def main():
    """Função principal"""
    try:
        # Inicializar bot
        bot = BitcoinSignalsBot()
        
        # Testar conectividade
        print("🧪 Testando conectividade...")
        test_signal = bot.get_trading_signal()
        
        if test_signal:
            print("✅ API funcionando")
            print(f"📊 Score atual: {test_signal.get('score')}")
        else:
            print("⚠️  API não respondeu, mas bot continuará tentando...")
        
        # Iniciar monitoramento
        bot.run_continuous(interval_minutes=15)
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()
