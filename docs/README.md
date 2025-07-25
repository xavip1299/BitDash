# 🤖 Bitcoin Trading Signals - Sistema Completo

Sistema automatizado de sinais de trading de Bitcoin com análise técnica avançada e alertas via Telegram.

## 📊 Características

- **Análise Técnica Completa**: RSI, MACD, Bollinger Bands, Stochastic, Moving Averages
- **Score de Confiança**: 0-100 baseado em múltiplos indicadores
- **Stop Loss & Take Profit**: Calculados automaticamente com base na volatilidade
- **Alertas Telegram**: Sinais automáticos com cores (🟢/🔴/🟡)
- **Dados em EUR**: Preços e análises em euros
- **Cloud Ready**: Pronto para deploy em Render, Heroku, etc.

## 🏗️ Arquitetura

```
deploy/
├── api/main.py           # Flask API com análise técnica
├── bots/cloud_bot.py     # Bot Telegram para cloud
├── start.py              # Entry point para deploy
├── requirements.txt      # Dependências Python
├── Procfile             # Configuração Render/Heroku
└── .env                 # Variáveis de ambiente
```

## 📈 API Endpoints

### Health Check
```
GET /api/health
```

### Preço Atual
```
GET /api/bitcoin-price
```
Retorna preço atual em EUR com variação 24h.

### Análise Técnica
```
GET /api/technical-analysis
```
Indicadores técnicos completos.

### Sinal Detalhado (Principal)
```
GET /api/detailed-signal
```
Sinal completo com score, SL/TP e recomendação.

## 🤖 Bot Telegram

### Funcionalidades
- ✅ Sinais automáticos a cada 15 minutos
- ✅ Score de 0-100 para cada sinal
- ✅ Stop Loss e Take Profit calculados
- ✅ Alertas Green/Red baseados no score
- ✅ Gestão inteligente de spam (só envia mudanças significativas)

### Exemplo de Mensagem
```
🟢 BITCOIN TRADING SIGNAL 🟢

📈 AÇÃO: COMPRAR
📊 SCORE: 78/100
💰 PREÇO: €45,250.00
🟢 24h: +2.5%

🛡️ GESTÃO DE RISCO:
• Stop Loss: €44,100.00
• Take Profit: €46,800.00

🔍 TIPO: STRONG BUY
⏰ HORA: 14:30:25
```

## 🚀 Deploy

### 1. Render.com (Recomendado)
1. Fork/upload este código para GitHub
2. Conectar ao Render.com
3. Configurar:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start.py`
4. Adicionar variáveis de ambiente:
   ```
   BOT_TOKEN=seu_bot_token
   CHAT_ID=seu_chat_id
   API_URL=https://your-app.onrender.com
   ```

### 2. Heroku
```bash
git add .
git commit -m "Deploy"
heroku create your-app-name
heroku config:set BOT_TOKEN=your_token
heroku config:set CHAT_ID=your_chat_id
heroku config:set API_URL=https://your-app.herokuapp.com
git push heroku main
```

### 3. Railway
Similar ao Render, mas com interface diferente.

## 🔧 Configuração Local

### Pré-requisitos
- Python 3.8+
- Conta Telegram + Bot Token
- Chat ID do Telegram

### Instalação
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar API
python api/main.py

# Executar Bot (em outro terminal)
python bots/cloud_bot.py
```

## 📊 Algoritmo de Score

O score é calculado com base em:

| Indicador | Pontos Máximos | Condições |
|-----------|----------------|-----------|
| RSI | 30 | Oversold/Overbought extremos |
| MACD | 20 | Cruzamentos e posição relativa |
| Bollinger Bands | 15 | Preço nos extremos |
| Moving Averages | 15 | SMA20 vs SMA50 |
| Price vs EMA | 10 | Preço acima/abaixo EMA12 |
| Stochastic | 10 | Condições de oversold/overbought |

### Interpretação do Score
- **80-100**: 🟢 STRONG BUY
- **60-79**: 🟢 BUY  
- **40-59**: 🟡 NEUTRAL
- **20-39**: 🔴 SELL
- **0-19**: 🔴 STRONG SELL

## 🛡️ Gestão de Risco

### Stop Loss
Calculado com base na volatilidade histórica:
- **Long**: Preço atual × (1 - volatilidade × 0.02)
- **Short**: Preço atual × (1 + volatilidade × 0.02)

### Take Profit
- **Long**: Preço atual × (1 + volatilidade × 0.04)
- **Short**: Preço atual × (1 - volatilidade × 0.04)

## 📱 Configuração do Telegram

### 1. Criar Bot
1. Falar com @BotFather no Telegram
2. `/newbot`
3. Seguir instruções
4. Guardar o token

### 2. Obter Chat ID
1. Enviar mensagem para o bot
2. Aceder: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Procurar por `"chat":{"id":`

## 🔍 Monitoramento

### Logs da API
A API gera logs detalhados para debug:
```
⏰ 2024-01-15 14:30:00 - Verificando sinais...
✅ Signal enviado: STRONG_BUY (Score: 78)
💤 Aguardando 15 minutos...
```

### Health Check
Verificar se a API está online:
```bash
curl https://your-app.onrender.com/api/health
```

## ⚠️ Avisos Importantes

1. **Não é Aconselhamento Financeiro**: Use apenas para análise pessoal
2. **Teste Primeiro**: Sempre teste com valores pequenos
3. **Diversifique**: Não coloque todos os fundos numa única estratégia
4. **Monitorize**: Acompanhe os resultados e ajuste conforme necessário

## 🤝 Contribuição

1. Fork o projeto
2. Criar branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja `LICENSE` para mais detalhes.

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verificar logs da aplicação
2. Testar endpoints manualmente
3. Verificar configuração do Telegram
4. Abrir issue no GitHub

---

**🚀 Sistema sempre online, sinais automáticos, gestão de risco integrada!**
