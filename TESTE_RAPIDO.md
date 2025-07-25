# 🎯 GUIA RÁPIDO: TESTAR ENDPOINTS

## 🚀 PASSO A PASSO

### 1. Primeiro, fazer deploy no Render.com
- Seguir `RENDER_FINAL_STEPS.md`
- Aguardar deploy completar (5-10 min)
- Obter URL real: `https://SEU-APP.onrender.com`

### 2. Testar automaticamente
```powershell
# Se o teu app se chama "bitdash-api"
.\test_api.ps1

# Se tem nome diferente, exemplo "meu-bitcoin-api"
.\test_api.ps1 -BaseUrl "https://meu-bitcoin-api.onrender.com"
```

### 3. Testar manualmente no navegador
```
https://SEU-APP.onrender.com/api/health
https://SEU-APP.onrender.com/api/bitcoin-price
https://SEU-APP.onrender.com/api/detailed-signal
https://SEU-APP.onrender.com/api/technical-analysis
```

## ✅ RESULTADO QUANDO FUNCIONAR

### Health Check
```json
{"status": "healthy", "timestamp": "2025-01-25T..."}
```

### Bitcoin Price  
```json
{"price_eur": 85432.50, "change_24h": 2.45, "timestamp": "..."}
```

### Detailed Signal
```json
{
  "signal": "BUY",
  "score": 78,
  "current_price": 85432.50,
  "stop_loss": 83500.00,
  "take_profit": 88000.00,
  "confidence": "HIGH"
}
```

## 🔧 SE DER ERRO 404

1. **Aguardar mais tempo** (cold start demora)
2. **Verificar URL** está correto
3. **Verificar logs** no Render Dashboard
4. **Verificar se deploy** foi bem-sucedido

## 📱 TELEGAM BOT

Quando API funcionar, bot enviará automaticamente:
```
🤖 BitDash Bot Iniciado!
✅ Conectado com sucesso
⏰ Próximo sinal em breve...
```

---

**🎯 IMPORTANTE**: API só funciona depois do deploy no Render.com estar completo!
