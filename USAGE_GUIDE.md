# 📋 Guia de Configuração e Uso

## 🚀 Início Rápido

### 1. Execução do Sistema Principal
```bash
cd bitcoin-dashboard
python main.py
```

### 2. Menu Principal
- **🌐 Dashboard Web**: Interface gráfica (dashboard/index.html)
- **🤖 Bot Telegram**: Sinais automáticos via Telegram
- **📊 API Trading**: Servidor Flask local (porta 5000)
- **⚡ Análise Rápida**: Verificação instantânea do Bitcoin
- **📋 Configurar Telegram**: Setup do bot
- **🚀 Deploy Cloud**: Instruções para deploy

## 🔧 Configuração Inicial

### Telegram Bot (Obrigatório para bot)
1. **Criar Bot**:
   - Falar com @BotFather no Telegram
   - `/newbot` → seguir instruções
   - Guardar o token

2. **Obter Chat ID**:
   - Enviar mensagem para o bot
   - Aceder: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Procurar `"chat":{"id":NUMERO}`

3. **Configurar**:
   ```bash
   python main.py
   # Escolher opção 5 - Configurar Telegram
   # OU editar diretamente: config/telegram_config.py
   ```

### Dependências Python
```bash
pip install -r config/requirements.txt
```

## 📁 Estrutura Detalhada

```
bitcoin-dashboard/
├── main.py                    # 🎯 Sistema principal
├── README.md                  # 📖 Documentação
│
├── 🌐 dashboard/              # Interface Web
│   ├── index.html            # Página principal
│   ├── styles.css            # Estilos
│   ├── script.js             # Lógica principal
│   ├── notifications.js      # Notificações
│   ├── ultimate_bitcoin_trading_system.js
│   └── xtb_trading_analyzer.js
│
├── 📊 api/                    # Backend APIs
│   └── improved_xtb_api.py   # API Flask principal
│
├── 🤖 bots/                   # Telegram Bots
│   ├── telegram_signals_bot.py  # Bot principal
│   ├── cloud_bot.py             # Bot para cloud
│   ├── scheduler_bot.py         # Bot com agendamento
│   └── [outros bots...]
│
├── 🔧 config/                 # Configurações
│   ├── telegram_config.py    # Config Telegram
│   ├── requirements.txt      # Dependências
│   └── [outros configs...]
│
├── ⚡ scripts/                # Utilitários
│   ├── quick_analysis.py     # Análise rápida
│   └── [outros scripts...]
│
├── 📚 docs/                   # Documentação
│   └── [guias de deploy...]
│
└── 🚀 deploy/                 # Para Cloud Deploy
    ├── api/main.py           # API otimizada
    ├── bots/cloud_bot.py     # Bot cloud
    └── [estrutura deploy...]
```

## 🌐 Dashboard Web

### Funcionalidades
- ✅ Preço Bitcoin em tempo real (EUR)
- ✅ Gráficos Chart.js interativos
- ✅ Alertas personalizados
- ✅ Análise técnica visual
- ✅ Integração Telegram
- ✅ Responsivo mobile

### Uso
1. `python main.py` → opção 1
2. Dashboard abre automaticamente no browser
3. Ou abrir manualmente: `dashboard/index.html`

## 🤖 Bot Telegram

### Funcionalidades
- ✅ Sinais automáticos (15 min)
- ✅ Score 0-100
- ✅ Stop Loss / Take Profit
- ✅ Alertas Green/Red
- ✅ Análise técnica integrada

### Uso
1. Configurar primeiro (opção 5)
2. `python main.py` → opção 2
3. Escolher modo:
   - Contínuo (15 min)
   - Verificação única
   - Teste conectividade

## 📊 API de Trading

### Endpoints
- `GET /api/bitcoin-price` - Preço atual
- `GET /api/technical-analysis` - Indicadores
- `GET /api/detailed-signal` - Sinal completo
- `GET /api/health` - Status

### Uso
1. `python main.py` → opção 3
2. API disponível em `http://localhost:5000`
3. Testar: `http://localhost:5000/api/health`

## ⚡ Análise Rápida

### Uso
1. `python main.py` → opção 4
2. Resultado instantâneo:
   - Preço atual
   - Variação 24h
   - Score e sinal
   - Recomendação

### Funciona Independente
- Não precisa de API local
- Conecta diretamente à CoinGecko
- Análise simples baseada em preço

## 🚀 Deploy para Cloud

### Opções
1. **Render.com** (Recomendado)
2. **Heroku**
3. **Railway**
4. **PythonAnywhere**

### Passos
1. `python main.py` → opção 6
2. Usar pasta `deploy/`
3. Seguir `deploy/docs/README.md`

## 🔍 Troubleshooting

### Bot não envia mensagens
- Verificar token e chat ID
- Testar conectividade (opção 3 no bot)
- Verificar se API está rodando

### Dashboard não carrega
- Verificar se `dashboard/index.html` existe
- Abrir manualmente no browser
- Verificar console do browser para erros

### API não responde
- Verificar se Flask está instalado
- Porta 5000 pode estar ocupada
- Verificar firewall/antivírus

### Análise rápida falha
- Verificar conexão internet
- CoinGecko pode ter rate limit
- Tentar novamente após alguns minutos

## 📞 Suporte

- 📖 Documentação: `docs/`
- 🔧 Configuração: `config/`
- 🚀 Deploy: `deploy/docs/`
- 🐛 Issues: Verificar logs no terminal

---

**✅ Sistema modular, organizado e pronto para uso!**
