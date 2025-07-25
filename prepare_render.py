#!/usr/bin/env python3
"""
Script para preparar deploy no Render.com
Automatiza verificações e preparação
"""

import os
import json
import subprocess
from pathlib import Path

def check_git_installed():
    """Verificar se Git está instalado"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_project_ready():
    """Verificar se projeto está pronto"""
    required_files = [
        'start.py',
        'requirements.txt', 
        'Procfile',
        '.env',
        'api/main.py',
        'bots/cloud_bot.py'
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    return len(missing) == 0, missing

def get_env_variables():
    """Obter variáveis de ambiente do .env"""
    env_vars = {}
    
    if Path('.env').exists():
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    return env_vars

def create_git_commands(repo_url):
    """Criar comandos Git para copy-paste"""
    commands = f"""
# COMANDOS PARA EXECUTAR NO TERMINAL:

cd "C:/Users/Pc/Desktop/dashbit/deploy"

git init
git add .
git commit -m "Bitcoin Trading Signals - Deploy Ready"
git remote add origin {repo_url}
git branch -M main
git push -u origin main
"""
    return commands

def main():
    """Função principal"""
    print("🚀 PREPARAÇÃO PARA RENDER.COM DEPLOY")
    print("=" * 50)
    
    # Verificar se estamos na pasta certa  
    if not Path('start.py').exists():
        print("❌ Execute este script na pasta deploy/")
        return
    
    # Verificar Git
    if not check_git_installed():
        print("❌ Git não está instalado!")
        print("📥 Baixar em: https://git-scm.com/download/windows")
        return
    else:
        print("✅ Git instalado")
    
    # Verificar projeto
    ready, missing = check_project_ready()
    if not ready:
        print(f"❌ Ficheiros em falta: {', '.join(missing)}")
        return
    else:
        print("✅ Todos os ficheiros essenciais presentes")
    
    # Verificar variáveis de ambiente
    env_vars = get_env_variables()
    required_env = ['BOT_TOKEN', 'CHAT_ID', 'API_URL']
    
    print("\n🔐 VARIÁVEIS DE AMBIENTE:")
    for var in required_env:
        if var in env_vars:
            value = env_vars[var]
            if var == 'BOT_TOKEN':
                display_value = f"{value[:10]}..."
            else:
                display_value = value
            print(f"  ✅ {var} = {display_value}")
        else:
            print(f"  ❌ {var} não configurado")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. 🌐 Criar repositório no GitHub")
    print("   - Ir para https://github.com")
    print("   - New repository → bitcoin-trading-signals")
    print("   - NÃO adicionar README/gitignore/license")
    
    print("\n2. 📤 Obter URL do repositório")
    repo_url = input("   Cole aqui a URL do repositório GitHub: ").strip()
    
    if repo_url:
        print("\n3. 💻 COMANDOS PARA EXECUTAR:")
        commands = create_git_commands(repo_url)
        print(commands)
        
        # Salvar comandos em arquivo
        with open('git_commands.txt', 'w') as f:
            f.write(commands)
        print("📁 Comandos salvos em: git_commands.txt")
        
        print("\n4. 🌐 RENDER.COM SETUP:")
        print("   - Ir para https://render.com")
        print("   - Sign up with GitHub")
        print("   - New → Web Service")
        print("   - Connect repository: bitcoin-trading-signals")
        print("   - Build Command: pip install -r requirements.txt")
        print("   - Start Command: python start.py")
        print(f"   - Environment Variables:")
        for var, value in env_vars.items():
            print(f"     {var}={value}")
        
        print("\n🎯 IMPORTANTE:")
        print("   - Após deploy, atualizar API_URL para a URL do Render")
        print("   - Exemplo: https://your-app-name.onrender.com")
    
    print("\n📚 DOCUMENTAÇÃO COMPLETA:")
    print("   - Ver: RENDER_DEPLOY_GUIDE.md")

if __name__ == "__main__":
    main()
