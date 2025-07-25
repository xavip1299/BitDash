#!/usr/bin/env python3
"""
Setup interativo para configurar o projeto Bitcoin Trading Signals
"""

import os
import requests
from pathlib import Path

def main():
    print("🚀 BITCOIN TRADING SIGNALS - SETUP")
    print("=" * 50)
    
    # Verificar se .env existe
    env_file = Path('.env')
    
    if env_file.exists():
        print("📁 Arquivo .env encontrado!")
        
        # Ler configurações existentes
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        # Extrair valores
        bot_token = None
        chat_id = None
        api_url = None
        
        for line in env_content.split('\n'):
            if line.startswith('BOT_TOKEN='):
                bot_token = line.split('=', 1)[1].strip()
            elif line.startswith('CHAT_ID='):
                chat_id = line.split('=', 1)[1].strip()
            elif line.startswith('API_URL='):
                api_url = line.split('=', 1)[1].strip()
        
        print(f"BOT_TOKEN = {bot_token}")
        print(f"CHAT_ID = {chat_id}")
        print(f"API_URL = {api_url}")
        
    else:
        print("❌ Arquivo .env não encontrado!")
        print("Por favor, crie o arquivo .env com:")
        print("BOT_TOKEN=seu_bot_token_aqui")
        print("CHAT_ID=seu_chat_id_aqui")
        print("API_URL=https://bitcoin-trading-api.onrender.com")
        return
    
    # Perguntar se quer testar
    test = input("\n🧪 Testar configuração agora? (y/n): ").lower().strip()
    
    if test == 'y':
        print("\n🧪 TESTANDO CONFIGURAÇÃO...")
        
        # Testar API
        try:
            response = requests.get(f"{api_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ API online")
            else:
                print(f"⚠️ API status: {response.status_code}")
        except:
            print(f"⚠️ API status: 404")
        
        # Testar bot
        if bot_token:
            try:
                bot_url = f"https://api.telegram.org/bot{bot_token}/getMe"
                response = requests.get(bot_url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        bot_name = data.get('result', {}).get('first_name', 'Unknown')
                        print(f"✅ Bot ativo: {bot_name}")
                    else:
                        print("❌ Bot token inválido")
                else:
                    print("❌ Erro ao verificar bot")
            except:
                print("❌ Erro de conexão com Telegram")
    
    print("\n🎯 Configuração concluída!")

if __name__ == "__main__":
    main()
