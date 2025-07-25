#!/usr/bin/env python3
"""
Entry point para cloud deployment (Render, Heroku, etc.)
Inclui keep-alive service para evitar spin down
"""

import os
import sys
import threading
import time

def keep_alive_service():
    """Keep-alive service para manter a API ativa"""
    import requests
    from datetime import datetime
    
    # URL da API
    api_url = os.environ.get('API_URL', 'https://bitdash-9dnk.onrender.com')
    
    # Aguardar API estar online
    print("💓 Keep-alive: Aguardando API inicializar...")
    time.sleep(60)  # 1 minuto
    
    print(f"💓 Keep-alive iniciado: {api_url}")
    
    while True:
        try:
            time.sleep(600)  # 10 minutos
            response = requests.get(f"{api_url}/api/health", timeout=15)
            if response.status_code == 200:
                print(f"💓 Keep-alive OK - {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"⚠️ Keep-alive warning: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Keep-alive error: {str(e)[:50]}")
            time.sleep(300)  # 5 minutos em caso de erro

def main():
    """Iniciar a aplicação Flask com keep-alive"""
    
    # Adicionar diretório atual ao Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Iniciar keep-alive em thread separada
    keep_alive_thread = threading.Thread(target=keep_alive_service, daemon=True)
    keep_alive_thread.start()
    
    # Importar e iniciar a API
    try:
        from api.main import app
        
        # Configurar porta
        port = int(os.environ.get('PORT', 5000))
        
        print(f"🚀 Iniciando Bitcoin Trading API na porta {port}")
        print(f"💓 Keep-alive service ativo")
        print(f"🛡️ Proteção contra spin down ativada")
        
        # Executar aplicação
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
