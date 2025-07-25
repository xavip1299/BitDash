# 🔧 TROUBLESHOOTING - RENDER.COM DEPLOY

## 🎯 PROBLEMAS RESOLVIDOS

### ✅ Python Version Compatibility
- **Problema**: Python 3.13.4 não é compatível com algumas dependências
- **Solução**: Adicionado `runtime.txt` especificando Python 3.11.9
- **Ficheiros criados**: 
  - `runtime.txt`
  - `pyproject.toml`
  - `build.sh`

### ✅ Dependencies Issues
- **Problema**: Versões fixas causavam conflitos
- **Solução**: Versões flexíveis no `requirements.txt`
- **Antes**: `flask==2.3.3`
- **Agora**: `flask>=2.3.0,<3.0.0`

## 🚀 INSTRUÇÕES ATUALIZADAS RENDER.COM

### 1. Build Configuration
```
Build Command: pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
Start Command: python start.py
Runtime: Python 3.11.9 (será detectado automaticamente)
```

### 2. Environment Variables (sem mudanças)
```
BOT_TOKEN=8343884144:AAETIlOVnA69fI-N4E-vzNJcQHTh0gDBz0I
CHAT_ID=1064066035
API_URL=https://bitdash-api.onrender.com
FLASK_ENV=production
PORT=10000
```

## 📊 LOGS ESPERADOS

### ✅ Build Success
```
==> Using Python version 3.11.9
==> Running build command 'pip install --upgrade pip setuptools wheel && pip install -r requirements.txt'...
Successfully installed flask-2.3.3 requests-2.31.0 pandas-2.0.3 numpy-1.24.4 ta-0.10.2 pytz-2023.3 flask-cors-4.0.0
==> Build succeeded 🎉
```

### ✅ Start Success
```
==> Starting service with 'python start.py'...
🚀 Iniciando Bitcoin Trading API na porta 10000
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:10000
 * Running on http://[::1]:10000
```

## 🧪 TESTES APÓS DEPLOY

### 1. Health Check
```bash
curl https://your-app.onrender.com/api/health
```
**Resposta esperada**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00",
  "service": "Bitcoin Trading API"
}
```

### 2. Bitcoin Price
```bash
curl https://your-app.onrender.com/api/bitcoin-price
```

### 3. Trading Signal
```bash
curl https://your-app.onrender.com/api/detailed-signal
```

## ⚠️ POSSÍVEIS PROBLEMAS

### Deploy ainda falha?
1. **Verificar logs** no Render Dashboard
2. **Aguardar** - build pode demorar 5-10 minutos
3. **Verificar** se todas as variáveis estão configuradas

### API não responde após deploy?
1. **Cold start**: Primeira requisição pode demorar 30-60 segundos
2. **Verificar URL**: Usar HTTPS sempre
3. **Verificar logs**: Dashboard → Service → Logs

### Bot não envia mensagens?
1. **Atualizar API_URL**: Deve ser a URL real do Render
2. **Verificar token**: BOT_TOKEN correto
3. **Testar manualmente**: Enviar mensagem para o bot primeiro

## 📱 FREE TIER LIMITATIONS

### Render.com Free
- ✅ **750 horas/mês grátis**
- ⚠️ **Suspende após 15min inatividade**
- ✅ **Desperta automaticamente na próxima requisição**
- ⚠️ **Deploy pode demorar até 10 minutos**

### Para Produção
- **Upgrade para Paid**: $7/mês - Sempre online
- **Custom Domain**: Disponível nos planos pagos
- **Mais recursos**: CPU e RAM adicional

## 🔄 RE-DEPLOY

Se precisares de fazer alterações:

```bash
# Na pasta deploy/
git add .
git commit -m "Update: descrição da mudança"
git push

# Deploy automático no Render!
```

## 📞 SUPORTE

### Render Support
- **Docs**: https://render.com/docs
- **Community**: Discord/Forum
- **Status**: https://status.render.com

### Projeto Support
- **Logs detalhados**: Disponíveis no dashboard
- **GitHub Issues**: No repositório
- **Documentação**: RENDER_DEPLOY_GUIDE.md

---

**🎯 Com estas correções, o deploy deve funcionar perfeitamente!**
