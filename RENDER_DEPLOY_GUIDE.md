# 🚀 DEPLOY RENDER.COM - GUIA COMPLETO

## 📋 Pré-requisitos

✅ **Projeto preparado na pasta `deploy/`**
✅ **Conta GitHub** (gratuita)
✅ **Conta Render.com** (gratuita)
✅ **Bot Telegram configurado**

## 🔥 PASSO 1: Preparar Repositório GitHub

### 1.1 Criar Repositório
1. Ir para [github.com](https://github.com)
2. Clicar em "New repository"
3. Nome: `bitcoin-trading-signals`
4. Descrição: `Bitcoin Trading Signals API with Telegram Bot`
5. Público ou Privado (ambos funcionam)
6. ✅ **NÃO** adicionar README, .gitignore, licença
7. Criar repositório

### 1.2 Upload do Código
```bash
# Na pasta deploy/ (IMPORTANTE!)
cd "C:/Users/Pc/Desktop/dashbit/deploy"

# Inicializar Git
git init

# Adicionar ficheiros
git add .

# Primeiro commit
git commit -m "Bitcoin Trading Signals - Deploy Ready"

# Conectar ao GitHub (substituir YOUR_USERNAME e YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/bitcoin-trading-signals.git

# Fazer push
git branch -M main
git push -u origin main
```

## 🌐 PASSO 2: Deploy no Render.com

### 2.1 Criar Conta
1. Ir para [render.com](https://render.com)
2. "Sign Up" com GitHub (recomendado)
3. Autorizar acesso aos repositórios

### 2.2 Criar Web Service
1. **Dashboard Render** → "New" → "Web Service"
2. **Connect Repository**: Selecionar `bitcoin-trading-signals`
3. **Configurações**:
   - **Name**: `bitcoin-trading-api`
   - **Region**: `Frankfurt` (Europa)
   - **Branch**: `main`
   - **Root Directory**: `.` (deixar vazio)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start.py`

### 2.3 Configurar Variáveis de Ambiente
Na secção "Environment Variables":

```env
BOT_TOKEN=8343884144:AAETIlOVnA69fI-N4E-vzNJcQHTh0gDBz0I
CHAT_ID=1064066035
API_URL=https://bitcoin-trading-api.onrender.com
FLASK_ENV=production
PORT=10000
```

⚠️ **IMPORTANTE**: Substituir `bitcoin-trading-api` pelo nome real do teu serviço

### 2.4 Deploy Automático
1. Clicar em "Create Web Service"
2. **Aguardar deploy** (5-10 minutos)
3. Verificar logs em tempo real
4. URL final: `https://your-service-name.onrender.com`

## ✅ PASSO 3: Verificar Deploy

### 3.1 Testar API
```bash
# Health check
curl https://your-service-name.onrender.com/api/health

# Bitcoin price
curl https://your-service-name.onrender.com/api/bitcoin-price

# Trading signal
curl https://your-service-name.onrender.com/api/detailed-signal
```

### 3.2 Logs do Render
- **Dashboard** → **Seu serviço** → **Logs**
- Verificar se não há erros
- API deve mostrar "Running on port 10000"

## 🤖 PASSO 4: Bot Telegram Always-On

### 4.1 Criar Background Worker (Opcional)
Para o bot ficar sempre online:

1. **Render Dashboard** → "New" → "Background Worker"
2. **Configurações**:
   - **Name**: `bitcoin-telegram-bot`
   - **Repository**: Mesmo repositório
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bots/cloud_bot.py`
3. **Mesmo Environment Variables**

### 4.2 Alternativa: Processo Único
O bot já está integrado na API principal e executará automaticamente.

## 🔧 PASSO 5: Configurações Avançadas

### 5.1 Custom Domain (Opcional)
- **Settings** → **Custom Domains**
- Adicionar domínio próprio
- Configurar DNS

### 5.2 Auto-Deploy
✅ **Já configurado**: Qualquer push para `main` faz deploy automático

### 5.3 Scaling (Pago)
- **Settings** → **Scaling**
- Aumentar recursos se necessário

## 📊 PASSO 6: Monitoramento

### 6.1 Uptime Monitoring
- **Dashboard** → **Metrics**
- Verificar uptime e performance
- Alertas automáticos por email

### 6.2 Logs em Tempo Real
```bash
# Via Render CLI (opcional)
render logs -s your-service-id --tail
```

## 🚨 Troubleshooting

### Deploy Failed
1. Verificar `requirements.txt`
2. Verificar `start.py`
3. Verificar logs do build
4. Verificar Python version compatibility

### API não responde
1. Verificar porta (deve ser PORT do ambiente)
2. Verificar if `__name__ == '__main__'`
3. Verificar firewall/cors

### Bot não envia mensagens
1. Verificar BOT_TOKEN e CHAT_ID
2. Verificar API_URL aponta para Render
3. Verificar logs do bot

## 💰 Custos

### Free Tier (Suficiente para teste)
- ✅ 750 horas/mês grátis
- ✅ Suspende após 15min inatividade
- ✅ Desperta automaticamente

### Paid Plans (Para produção)
- **Starter**: $7/mês - Sempre online
- **Standard**: $25/mês - Mais recursos

## 🔄 Updates Futuros

### Git Workflow
```bash
# Fazer alterações
git add .
git commit -m "Update: nova funcionalidade"
git push origin main

# Deploy automático no Render!
```

## 📱 URL Final

Depois do deploy:
- **API**: `https://your-service-name.onrender.com`
- **Health**: `https://your-service-name.onrender.com/api/health`
- **Signals**: `https://your-service-name.onrender.com/api/detailed-signal`

---

## 🎯 CHECKLIST FINAL

- [ ] Repositório GitHub criado
- [ ] Código na pasta `deploy/` enviado
- [ ] Web Service criado no Render
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy concluído com sucesso
- [ ] API responde em `/api/health`
- [ ] Bot Telegram funcionando
- [ ] URL atualizada no BOT_TOKEN

**🚀 Seu Bitcoin Trading System estará SEMPRE ONLINE!**
