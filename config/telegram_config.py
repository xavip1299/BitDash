#!/usr/bin/env python3
"""
Configuração do Telegram Bot
Configure suas credenciais aqui
"""

import os
import json
from pathlib import Path

# ⚠️  CONFIGURAR ESTAS VARIÁVEIS:
TELEGRAM_BOT_TOKEN = "8343884144:AAETIlOVnA69fI-N4E-vzNJcQHTh0gDBz0I"
TELEGRAM_CHAT_ID = "1064066035"

# Configurações adicionais
API_BASE_URL = "http://localhost:5000"
UPDATE_INTERVAL_MINUTES = 15

def load_config_from_json():
    """Carregar configuração do arquivo JSON se existir"""
    config_file = Path(__file__).parent / 'telegram_config_exemplo.json'
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            return {
                'bot_token': config.get('telegram', {}).get('bot_token'),
                'chat_id': config.get('telegram', {}).get('chat_id'),
                'api_url': config.get('api', {}).get('base_url', API_BASE_URL)
            }
        except Exception as e:
            print(f"⚠️  Erro ao carregar config JSON: {e}")
    
    return None

def validate_config():
    """Validar configuração"""
    issues = []
    
    if not TELEGRAM_BOT_TOKEN or len(TELEGRAM_BOT_TOKEN) < 10:
        issues.append("❌ TELEGRAM_BOT_TOKEN inválido")
    
    if not TELEGRAM_CHAT_ID:
        issues.append("❌ TELEGRAM_CHAT_ID não configurado")
    
    return issues

def setup_interactive():
    """Setup interativo das configurações"""
    print("🔧 CONFIGURAÇÃO DO TELEGRAM BOT")
    print("=" * 40)
    
    print("\n📋 Passos para configurar:")
    print("1. Criar bot com @BotFather no Telegram")
    print("2. Obter token do bot")
    print("3. Obter seu chat ID")
    print("4. Configurar neste ficheiro")
    
    print(f"\n📁 Ficheiro de configuração: {__file__}")
    
    current_token = TELEGRAM_BOT_TOKEN
    current_chat_id = TELEGRAM_CHAT_ID
    
    print(f"\n🤖 Token atual: {current_token[:10]}..." if current_token else "❌ Token não configurado")
    print(f"💬 Chat ID atual: {current_chat_id}" if current_chat_id else "❌ Chat ID não configurado")
    
    # Verificar se configuração está válida
    issues = validate_config()
    
    if issues:
        print("\n⚠️  PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n🔧 Para corrigir:")
        print(f"  1. Editar: {__file__}")
        print("  2. Configurar TELEGRAM_BOT_TOKEN")
        print("  3. Configurar TELEGRAM_CHAT_ID")
    else:
        print("\n✅ Configuração válida!")
        
        # Testar conectividade
        import requests
        try:
            bot_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
            response = requests.get(bot_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_name = data.get('result', {}).get('first_name', 'Unknown')
                    print(f"🤖 Bot ativo: {bot_name}")
                else:
                    print("❌ Bot token inválido")
            else:
                print("❌ Erro ao verificar bot")
        except:
            print("❌ Erro de conexão")

def main():
    """Função principal de configuração"""
    setup_interactive()

if __name__ == "__main__":
    main()
