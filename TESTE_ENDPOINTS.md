# 🧪 COMO TESTAR OS ENDPOINTS DA API

## 📋 ENDPOINTS DISPONÍVEIS

Após o deploy no Render.com, terás estes endpoints:

```
https://YOUR-APP-NAME.onrender.com/api/health
https://YOUR-APP-NAME.onrender.com/api/bitcoin-price  
https://YOUR-APP-NAME.onrender.com/api/detailed-signal
https://YOUR-APP-NAME.onrender.com/api/technical-analysis
```

⚠️ **Substitui `YOUR-APP-NAME` pelo nome real do teu serviço no Render**

## 🔧 MÉTODO 1: POWERSHELL (Windows)

### Health Check
```powershell
Invoke-WebRequest -Uri "https://YOUR-APP-NAME.onrender.com/api/health" -Method GET
```

### Preço Bitcoin
```powershell
Invoke-WebRequest -Uri "https://YOUR-APP-NAME.onrender.com/api/bitcoin-price" -Method GET
```

### Sinal Detalhado
```powershell
Invoke-WebRequest -Uri "https://YOUR-APP-NAME.onrender.com/api/detailed-signal" -Method GET
```

### Análise Técnica
```powershell
Invoke-WebRequest -Uri "https://YOUR-APP-NAME.onrender.com/api/technical-analysis" -Method GET
```

## 🌐 MÉTODO 2: NAVEGADOR WEB

Simplesmente abre estes URLs no navegador:

1. **Health Check**: https://YOUR-APP-NAME.onrender.com/api/health
2. **Preço Bitcoin**: https://YOUR-APP-NAME.onrender.com/api/bitcoin-price
3. **Sinal Detalhado**: https://YOUR-APP-NAME.onrender.com/api/detailed-signal
4. **Análise Técnica**: https://YOUR-APP-NAME.onrender.com/api/technical-analysis

## 📱 MÉTODO 3: POSTMAN/INSOMNIA

1. **Criar nova Collection**
2. **Adicionar requests GET**:
   - Nome: "Health Check", URL: https://YOUR-APP-NAME.onrender.com/api/health
   - Nome: "Bitcoin Price", URL: https://YOUR-APP-NAME.onrender.com/api/bitcoin-price
   - Nome: "Detailed Signal", URL: https://YOUR-APP-NAME.onrender.com/api/detailed-signal
   - Nome: "Technical Analysis", URL: https://YOUR-APP-NAME.onrender.com/api/technical-analysis

## 💻 MÉTODO 4: CURL (Git Bash/Terminal)

Se tiveres Git Bash instalado:

```bash
# Health Check
curl -X GET "https://YOUR-APP-NAME.onrender.com/api/health"

# Bitcoin Price
curl -X GET "https://YOUR-APP-NAME.onrender.com/api/bitcoin-price"

# Detailed Signal
curl -X GET "https://YOUR-APP-NAME.onrender.com/api/detailed-signal"

# Technical Analysis
curl -X GET "https://YOUR-APP-NAME.onrender.com/api/technical-analysis"
```

## 📊 RESPOSTA ESPERADA

### /api/health
```json
{
  "status": "healthy",
  "timestamp": "2025-01-25T12:00:00Z",
  "version": "1.0.0"
}
```

### /api/bitcoin-price
```json
{
  "price_eur": 85432.50,
  "price_usd": 89750.00,
  "change_24h": 2.45,
  "timestamp": "2025-01-25T12:00:00Z"
}
```

### /api/detailed-signal
```json
{
  "signal": "BUY",
  "score": 78,
  "current_price": 85432.50,
  "stop_loss": 83500.00,
  "take_profit": 88000.00,
  "confidence": "HIGH",
  "timestamp": "2025-01-25T12:00:00Z",
  "indicators": {
    "rsi": 65.2,
    "macd": "BULLISH",
    "bollinger": "NEUTRAL"
  }
}
```

### /api/technical-analysis
```json
{
  "price": 85432.50,
  "trend": "UPTREND",
  "indicators": {
    "rsi": 65.2,
    "rsi_signal": "NEUTRAL",
    "macd": 125.6,
    "macd_signal": "BUY",
    "sma_20": 84500.0,
    "sma_50": 83200.0,
    "bollinger_upper": 87000.0,
    "bollinger_lower": 82000.0
  },
  "support_resistance": {
    "support": 83500.0,
    "resistance": 88000.0
  },
  "timestamp": "2025-01-25T12:00:00Z"
}
```

## ❗ PROBLEMAS COMUNS

### Erro 404 (Not Found)
- ✅ Verificar se o URL está correto
- ✅ Aguardar alguns minutos (cold start)
- ✅ Verificar se o deploy foi bem-sucedido no Render

### Erro 500 (Server Error)
- ✅ Verificar logs no Render Dashboard
- ✅ Verificar Environment Variables
- ✅ Verificar se todas as dependências foram instaladas

### Timeout
- ✅ Primeira chamada pode demorar (cold start)
- ✅ Aguardar até 30 segundos
- ✅ Tentar novamente

## 🚀 SCRIPT DE TESTE AUTOMÁTICO

Cria este ficheiro `test_api.ps1` para testar todos os endpoints:

```powershell
$BASE_URL = "https://YOUR-APP-NAME.onrender.com"
$endpoints = @("/api/health", "/api/bitcoin-price", "/api/detailed-signal", "/api/technical-analysis")

foreach ($endpoint in $endpoints) {
    Write-Host "Testing $endpoint..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "$BASE_URL$endpoint" -Method GET
        Write-Host "✅ $endpoint - Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "Response: $($response.Content.Substring(0, 100))..." -ForegroundColor Cyan
    }
    catch {
        Write-Host "❌ $endpoint - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host "---" -ForegroundColor Gray
}
```

## 🎯 PRÓXIMOS PASSOS

1. **Fazer deploy no Render.com**
2. **Obter URL real da aplicação**
3. **Substituir YOUR-APP-NAME nos comandos**
4. **Testar todos os endpoints**
5. **Verificar se bot Telegram funciona**

---

**🔥 Quando a API estiver online, todos estes testes devem funcionar perfeitamente!**
