#!/usr/bin/env python3
"""
Entry point para cloud deployment (Render, Heroku, etc.)
"""

import os
import sys

def main():
    """Iniciar a aplicação Flask"""
    
    # Adicionar diretório atual ao Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Importar e iniciar a API
    try:
        from api.main import app
        
        # Configurar porta
        port = int(os.environ.get('PORT', 5000))
        
        print(f"🚀 Iniciando Bitcoin Trading API na porta {port}")
        
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
