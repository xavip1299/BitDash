#!/usr/bin/env python3
"""
Sistema de Alertas por Webhook - Solução para Render.com Free Tier
Em vez de bot contínuo, API envia alertas quando há mudanças significativas
"""

import requests
import json
from datetime import datetime, timedelta
import time

class WebhookAlertSystem:
    def __init__(self):
        self.bot_token = "8343884144:AAETIlOVnA69fI-N4E-vzNJcQHTh0gDBz0I"
        self.chat_id = "1064066035"
        self.api_base = "https://bitdash-9dnk.onrender.com"
        self.last_prices = {}
        self.alert_threshold = 3.0  # 3% mudança para alertar
        
    def get_current_signals(self):
        """Buscar sinais atuais da API"""
        try:
            response = requests.get(f"{self.api_base}/api/signals/all", timeout=15)
            if response.status_code == 200:
                return response.json().get('signals', [])
            return None
        except Exception as e:
            print(f"Erro ao buscar sinais: {e}")
            return None
    
    def check_significant_changes(self, current_signals):
        """Verificar se há mudanças significativas nos preços"""
        alerts = []
        
        for signal in current_signals:
            crypto = signal['crypto']
            current_price = signal['current_price']['usd']
            change_24h = signal['change_24h']
            signal_action = signal['signal']
            
            # Verificar mudança significativa
            if abs(change_24h) >= self.alert_threshold:
                alerts.append({
                    'crypto': crypto,
                    'price': current_price,
                    'change': change_24h,
                    'signal': signal_action,
                    'type': 'price_change'
                })
            
            # Verificar mudança de sinal
            if crypto in self.last_prices:
                last_signal = self.last_prices[crypto].get('signal')
                if last_signal and last_signal != signal_action:
                    alerts.append({
                        'crypto': crypto,
                        'price': current_price,
                        'old_signal': last_signal,
                        'new_signal': signal_action,
                        'type': 'signal_change'
                    })
            
            # Guardar estado atual
            self.last_prices[crypto] = {
                'price': current_price,
                'change': change_24h,
                'signal': signal_action,
                'timestamp': datetime.now()
            }
        
        return alerts
    
    def send_alert(self, alerts):
        """Enviar alerta para Telegram"""
        if not alerts:
            return False
        
        message = f"🚨 <b>ALERTA BITCOIN DASHBOARD</b>\n\n⏰ <b>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</b>\n\n"
        
        for alert in alerts:
            crypto = alert['crypto'].upper()
            
            if alert['type'] == 'price_change':
                change = alert['change']
                emoji = "📈" if change > 0 else "📉"
                signal_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(alert['signal'], "❓")
                
                message += f"{emoji} <b>{crypto}:</b> ${alert['price']:,.2f}\n"
                message += f"   Mudança: {change:+.2f}%\n"
                message += f"   {signal_emoji} Sinal: {alert['signal']}\n\n"
                
            elif alert['type'] == 'signal_change':
                old_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(alert['old_signal'], "❓")
                new_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(alert['new_signal'], "❓")
                
                message += f"🔄 <b>{crypto} - MUDANÇA DE SINAL!</b>\n"
                message += f"   Preço: ${alert['price']:,.2f}\n"
                message += f"   {old_emoji} {alert['old_signal']} → {new_emoji} {alert['new_signal']}\n\n"
        
        message += "---\n<i>BitDash Alert System</i>"
        
        # Enviar mensagem
        telegram_api = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(telegram_api, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print(f"✅ Alerta enviado (ID: {result['result']['message_id']})")
                    return True
            return False
        except Exception as e:
            print(f"❌ Erro ao enviar alerta: {e}")
            return False
    
    def run_single_check(self):
        """Executar uma única verificação"""
        print("🔍 Verificando sinais para alertas...")
        
        current_signals = self.get_current_signals() 
        if not current_signals:
            print("❌ Não foi possível obter sinais")
            return False
        
        alerts = self.check_significant_changes(current_signals)
        
        if alerts:
            print(f"🚨 {len(alerts)} alertas encontrados!")
            return self.send_alert(alerts)
        else:
            print("✅ Nenhum alerta necessário")
            return True

if __name__ == "__main__":
    print("🔔 SISTEMA DE ALERTAS WEBHOOK")
    print("=" * 40)
    print("💡 Este sistema roda sob demanda, não 24/7")
    print("🎯 Ideal para Render.com free tier")
    print()
    
    alert_system = WebhookAlertSystem()
    success = alert_system.run_single_check()
    
    if success:
        print("\n✅ Verificação concluída com sucesso!")
    else:
        print("\n❌ Houve problemas na verificação")
    
    print("\n💡 COMO USAR:")
    print("1. Execute este script sempre que quiseres verificar")
    print("2. Ou configure no Windows Task Scheduler para executar periodicamente")
    print("3. Ou use cron job no Linux/Mac")
