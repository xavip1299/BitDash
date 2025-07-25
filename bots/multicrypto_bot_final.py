#!/usr/bin/env python3
"""
Bot Telegram Multi-Crypto Trading Signals - Versão Final
Adaptado para funcionar tanto local quanto na nuvem
"""

import os
import time
import requests
import schedule
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multicrypto_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MultiCryptoTelegramBot:
    def __init__(self):
        """Inicializar bot com configurações automáticas"""
        
        # Configurações do Telegram
        self.bot_token = os.getenv('BOT_TOKEN', '8343884144:AAETIlOVnA69fI-N4E-vzNJcQHTh0gDBz0I')
        self.chat_id = os.getenv('CHAT_ID', '1064066035')
        
        # URLs da API (com fallback local)
        self.api_urls = [
            'https://bitdash-9dnk.onrender.com',  # Produção
            'http://localhost:5000'                # Local fallback
        ]
        self.current_api_url = None
        
        # Configurações
        self.cryptos = ['bitcoin', 'ethereum', 'xrp']
        self.crypto_emojis = {
            'bitcoin': '₿',
            'ethereum': '⟠', 
            'xrp': '◆'
        }
        
        # Estado
        self.last_signals = {}
        self.api_errors = 0
        self.max_api_errors = 3
        
        logger.info("🤖 MultiCryptoTelegramBot inicializado")
    
    def find_working_api(self):
        """Encontrar API funcionando (local ou nuvem)"""
        for api_url in self.api_urls:
            try:
                logger.info(f"🔍 Testando API: {api_url}")
                response = requests.get(f"{api_url}/api/health", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ API funcionando: {api_url}")
                    logger.info(f"📊 Status: {data.get('status')}")
                    logger.info(f"🔢 Versão: {data.get('version')}")
                    
                    self.current_api_url = api_url
                    self.api_errors = 0
                    return True
                    
            except Exception as e:
                logger.warning(f"❌ API {api_url} não disponível: {e}")
                continue
        
        logger.error("❌ Nenhuma API disponível!")
        self.api_errors += 1
        return False
    
    def send_telegram_message(self, message, parse_mode='HTML'):
        """Enviar mensagem para o Telegram com retry"""
        telegram_api = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }
        
        for attempt in range(3):
            try:
                response = requests.post(telegram_api, json=payload, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        message_id = result['result']['message_id']
                        logger.info(f"✅ Mensagem enviada (ID: {message_id})")
                        return message_id
                    else:
                        logger.error(f"❌ Erro Telegram: {result}")
                else:
                    logger.error(f"❌ HTTP {response.status_code}: {response.text}")
                
            except Exception as e:
                logger.error(f"❌ Erro envio (tentativa {attempt+1}): {e}")
                if attempt < 2:
                    time.sleep(2)
        
        return None
    
    def get_crypto_signal(self, crypto_id):
        """Obter sinal de uma criptomoeda"""
        if not self.current_api_url:
            if not self.find_working_api():
                return None
        
        try:
            url = f"{self.current_api_url}/api/{crypto_id}/signal"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Erro sinal {crypto_id}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Erro obter sinal {crypto_id}: {e}")
            # Tentar próxima API
            if self.current_api_url == self.api_urls[0]:
                self.current_api_url = None
        
        return None
    
    def get_all_signals(self):
        """Obter todos os sinais"""
        if not self.current_api_url:
            if not self.find_working_api():
                return None
        
        try:
            url = f"{self.current_api_url}/api/signals/all"
            response = requests.get(url, timeout=20)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Erro todos sinais: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Erro obter todos sinais: {e}")
            self.current_api_url = None
        
        return None
    
    def format_signal_message(self, signal_data):
        """Formatar mensagem de sinal"""
        crypto = signal_data.get('crypto', 'unknown')
        symbol = signal_data.get('symbol', crypto.upper())
        emoji = self.crypto_emojis.get(crypto, '🪙')
        
        signal = signal_data.get('signal', 'HOLD')
        score = signal_data.get('score', 50)
        confidence = signal_data.get('confidence', 'LOW')
        price = signal_data.get('current_price', 0)
        rsi = signal_data.get('rsi', 50)
        trend = signal_data.get('trend', 'NEUTRAL')
        
        # Cor do sinal
        if signal == 'BUY':
            signal_color = '🟢'
        elif signal == 'SELL':
            signal_color = '🔴'
        else:
            signal_color = '🟡'
        
        # Confiança
        if confidence == 'HIGH':
            conf_emoji = '🔥'
        elif confidence == 'MEDIUM':
            conf_emoji = '⚡'
        else:
            conf_emoji = '⚠️'
        
        message = f"""
{signal_color} <b>{symbol} {emoji} - {signal}</b> {conf_emoji}

💰 <b>Preço:</b> ${price:,.2f}
📊 <b>Score:</b> {score}/100
🎯 <b>Confiança:</b> {confidence}
📈 <b>RSI:</b> {rsi:.1f}
📊 <b>Tendência:</b> {trend}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""
        
        return message.strip()
    
    def send_signals_summary(self):
        """Enviar resumo de todos os sinais"""
        logger.info("📊 Enviando resumo de sinais...")
        
        signals_data = self.get_all_signals()
        
        if not signals_data or not signals_data.get('signals'):
            self.send_telegram_message("❌ <b>Erro ao obter sinais</b>\n\nTentando reconectar à API...")
            return
        
        signals = signals_data['signals']
        
        # Contar sinais por tipo
        buy_count = sum(1 for s in signals if s.get('signal') == 'BUY')
        sell_count = sum(1 for s in signals if s.get('signal') == 'SELL')
        hold_count = sum(1 for s in signals if s.get('signal') == 'HOLD')
        high_conf_count = sum(1 for s in signals if s.get('confidence') == 'HIGH')
        
        # Header
        header = f"""
🚀 <b>RESUMO MULTI-CRYPTO</b>
⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}

📊 <b>Sinais ({len(signals)}):</b>
🟢 BUY: {buy_count} | 🔴 SELL: {sell_count} | 🟡 HOLD: {hold_count}
🔥 Alta Confiança: {high_conf_count}

---
"""
        
        # Sinais individuais
        signals_text = ""
        for signal in signals:
            crypto = signal.get('crypto', 'unknown')
            symbol = signal.get('symbol', crypto.upper())
            emoji = self.crypto_emojis.get(crypto, '🪙')
            signal_type = signal.get('signal', 'HOLD')
            score = signal.get('score', 50)
            confidence = signal.get('confidence', 'LOW')
            price = signal.get('current_price', 0)
            
            if signal_type == 'BUY':
                signal_color = '🟢'
            elif signal_type == 'SELL':
                signal_color = '🔴'
            else:
                signal_color = '🟡'
            
            conf_emoji = '🔥' if confidence == 'HIGH' else '⚡' if confidence == 'MEDIUM' else '⚠️'
            
            signals_text += f"{signal_color} <b>{symbol}</b> {emoji}: {signal_type} ({score}/100) {conf_emoji}\n"
        
        # Footer
        api_source = "🌐 Local" if "localhost" in (self.current_api_url or "") else "☁️ Cloud"
        footer = f"""
---
{api_source} | 🤖 BitDash Bot
"""
        
        message = header + signals_text + footer
        self.send_telegram_message(message)
    
    def check_signal_changes(self):
        """Verificar mudanças nos sinais e enviar alertas"""
        logger.info("🔍 Verificando mudanças nos sinais...")
        
        current_signals = {}
        
        for crypto in self.cryptos:
            signal_data = self.get_crypto_signal(crypto)
            if signal_data:
                current_signals[crypto] = {
                    'signal': signal_data.get('signal'),
                    'score': signal_data.get('score'),
                    'confidence': signal_data.get('confidence')
                }
        
        # Verificar mudanças
        for crypto, current in current_signals.items():
            if crypto in self.last_signals:
                last = self.last_signals[crypto]
                
                # Sinal mudou
                if current['signal'] != last['signal']:
                    logger.info(f"🚨 Mudança de sinal {crypto}: {last['signal']} → {current['signal']}")
                    
                    signal_data = self.get_crypto_signal(crypto)
                    if signal_data:
                        message = f"🚨 <b>MUDANÇA DE SINAL!</b>\n" + self.format_signal_message(signal_data)
                        self.send_telegram_message(message)
                
                # Score mudou significativamente (>10 pontos)
                elif abs(current['score'] - last['score']) > 10:
                    logger.info(f"📊 Mudança significativa score {crypto}: {last['score']} → {current['score']}")
        
        # Atualizar últimos sinais
        self.last_signals = current_signals
    
    def send_startup_message(self):
        """Enviar mensagem de inicialização"""
        api_source = "🌐 Local" if "localhost" in (self.current_api_url or "") else "☁️ Cloud"
        
        message = f"""
🚀 <b>BOT MULTI-CRYPTO ATIVO!</b>

🤖 <b>BitDash Trading Bot</b>
⏰ <b>Iniciado:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
📡 <b>API:</b> {api_source}
🎯 <b>Cryptos:</b> Bitcoin, Ethereum, XRP

✅ <b>Sistema funcionando!</b>
📊 Sinais serão enviados automaticamente

---
🔄 Próximo resumo em 15 minutos
"""
        
        return self.send_telegram_message(message)
    
    def run_scheduled_tasks(self):
        """Executar tarefas agendadas"""
        logger.info("⏰ Executando tarefas agendadas...")
        
        try:
            # Resumo completo
            self.send_signals_summary()
            
            # Verificar mudanças
            time.sleep(2)  # Delay pequeno
            self.check_signal_changes()
            
        except Exception as e:
            logger.error(f"❌ Erro tarefas agendadas: {e}")
            self.send_telegram_message(f"❌ <b>Erro no sistema:</b>\n{str(e)}")
    
    def run(self):
        """Executar bot principal"""
        logger.info("🚀 Iniciando MultiCrypto Telegram Bot...")
        
        # Encontrar API funcionando
        if not self.find_working_api():
            logger.error("💀 Nenhuma API disponível - Bot não pode iniciar")
            return
        
        # Mensagem de startup
        if self.send_startup_message():
            logger.info("✅ Mensagem de startup enviada")
        
        # Enviar primeiro resumo
        time.sleep(3)
        self.send_signals_summary()
        
        # Configurar agendamentos
        schedule.every(15).minutes.do(self.run_scheduled_tasks)
        schedule.every(5).minutes.do(self.check_signal_changes)
        
        logger.info("⏰ Agendamentos configurados:")
        logger.info("   📊 Resumo completo: a cada 15 minutos")
        logger.info("   🔍 Verificar mudanças: a cada 5 minutos")
        
        # Loop principal
        logger.info("🔄 Iniciando loop principal...")
        
        while True:
            try:
                schedule.run_pending()
                
                # Verificar saúde da API a cada hora
                if self.api_errors >= self.max_api_errors:
                    logger.warning("🔧 Muitos erros de API, tentando reconectar...")
                    self.find_working_api()
                
                time.sleep(30)  # Check a cada 30 segundos
                
            except KeyboardInterrupt:
                logger.info("⏹️ Bot parado pelo usuário")
                self.send_telegram_message("⏹️ <b>Bot Parado</b>\n\nSistema desligado pelo administrador.")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop principal: {e}")
                time.sleep(60)  # Wait 1 minute on error

def main():
    """Função principal"""
    bot = MultiCryptoTelegramBot()
    bot.run()

if __name__ == "__main__":
    main()
