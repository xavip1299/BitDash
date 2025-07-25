#!/usr/bin/env python3
"""
Bitcoin Dashboard - Sistema Principal
Ponto de entrada unificado para todos os componentes
"""

import sys
import os
from pathlib import Path

# Adicionar todas as pastas ao Python path
current_dir = Path(__file__).parent
sys.path.extend([
    str(current_dir / 'api'),
    str(current_dir / 'bots'),
    str(current_dir / 'scripts'),
    str(current_dir / 'config')
])

def show_menu():
    """Mostrar menu principal"""
    print("\n🚀 BITCOIN DASHBOARD - SISTEMA PRINCIPAL")
    print("=" * 50)
    print("1. 🌐 Iniciar Dashboard Web")
    print("2. 🤖 Executar Bot Telegram")
    print("3. 📊 API de Trading Signals")
    print("4. ⚡ Análise Rápida")
    print("5. 📋 Configurar Telegram")
    print("6. 🚀 Deploy para Cloud")
    print("0. ❌ Sair")
    print("=" * 50)

def start_dashboard():
    """Iniciar dashboard web"""
    print("🌐 Iniciando Dashboard Web...")
    print("📁 Abrir: dashboard/index.html no navegador")
    
    # Tentar abrir automaticamente
    import webbrowser
    dashboard_path = current_dir / 'dashboard' / 'index.html'
    if dashboard_path.exists():
        webbrowser.open(f'file://{dashboard_path.absolute()}')
        print(f"✅ Dashboard aberto: {dashboard_path}")
    else:
        print("❌ Ficheiro dashboard/index.html não encontrado")

def start_telegram_bot():
    """Iniciar bot do Telegram"""
    print("🤖 Iniciando Bot Telegram...")
    try:
        from telegram_signals_bot import main as bot_main
        bot_main()
    except ImportError:
        print("❌ Bot não encontrado em bots/telegram_signals_bot.py")
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")

def start_api():
    """Iniciar API de trading"""
    print("📊 Iniciando API de Trading Signals...")
    try:
        from improved_xtb_api import app
        print("🚀 API iniciada em http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except ImportError:
        print("❌ API não encontrada em api/improved_xtb_api.py")
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")

def quick_analysis():
    """Executar análise rápida"""
    print("⚡ Executando Análise Rápida...")
    try:
        from quick_analysis import main as analysis_main
        analysis_main()
    except ImportError:
        print("❌ Script não encontrado em scripts/quick_analysis.py")
    except Exception as e:
        print(f"❌ Erro na análise: {e}")

def configure_telegram():
    """Configurar Telegram"""
    print("📋 Configurando Telegram...")
    try:
        from telegram_config import main as config_main
        config_main()
    except ImportError:
        print("❌ Configuração não encontrada em config/telegram_config.py")
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")

def deploy_cloud():
    """Instruções de deploy"""
    print("🚀 Deploy para Cloud:")
    print("1. Usar pasta 'deploy/' para deploy em Render/Heroku")
    print("2. Consultar deploy/docs/README.md para instruções completas")
    print("3. Configurar variáveis de ambiente no painel do serviço")

def main():
    """Função principal"""
    while True:
        try:
            show_menu()
            choice = input("\n🔢 Escolha uma opção: ").strip()
            
            if choice == '1':
                start_dashboard()
            elif choice == '2':
                start_telegram_bot()
            elif choice == '3':
                start_api()
            elif choice == '4':
                quick_analysis()
            elif choice == '5':
                configure_telegram()
            elif choice == '6':
                deploy_cloud()
            elif choice == '0':
                print("👋 Até logo!")
                break
            else:
                print("❌ Opção inválida!")
                
            input("\n⏸️  Pressione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n👋 Sistema interrompido pelo utilizador!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
