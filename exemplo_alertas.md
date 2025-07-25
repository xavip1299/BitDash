# 📱 EXEMPLOS DE ALERTAS QUE RECEBERÁS

## 🚨 **ALERTA DE MUDANÇA DE PREÇO** (webhook_alerts.py)
*Disparado quando mudança ≥ 3% em qualquer crypto*

```
🚨 ALERTA BITCOIN DASHBOARD

⏰ 25/07/2025 16:01:15

📈 BITCOIN: $116,352.61
   Mudança: +4.2%
   🟢 Sinal: BUY

📉 ETHEREUM: $3,643.89
   Mudança: -3.7%
   🔴 Sinal: SELL

---
BitDash Alert System
```

## 🔄 **ALERTA DE MUDANÇA DE SINAL**
*Quando recomendação muda (BUY→SELL, HOLD→BUY, etc)*

```
🚨 ALERTA BITCOIN DASHBOARD

⏰ 25/07/2025 16:01:15

🔄 BITCOIN - MUDANÇA DE SINAL!
   Preço: $116,352.61
   🟡 HOLD → 🟢 BUY

🔄 XRP - MUDANÇA DE SINAL!
   Preço: $3.03
   🟢 BUY → 🔴 SELL

---
BitDash Alert System
```

## 📊 **RESUMO COMPLETO** (multicrypto_bot_final.py)
*Enviado pelo bot completo a cada 15 minutos*

```
🚀 RESUMO MULTI-CRYPTO

📊 Sinais de Trading - 25/07/2025 16:01:15

🪙 BITCOIN (BTC)
💰 Preço: $116,352.61
📈 24h: +4.2%
🎯 RSI: 68.5
🟢 SINAL: BUY

⚡ ETHEREUM (ETH)  
💰 Preço: $3,643.89
📉 24h: -3.7%
🎯 RSI: 32.1
🔴 SINAL: SELL

💎 XRP
💰 Preço: $3.03
📊 24h: +1.8%
🎯 RSI: 45.2
🟡 SINAL: HOLD

---
🌐 API: Cloud | ⏰ Próximo: 16:16
BitDash Multi-Crypto Bot
```

## 🚀 **MENSAGEM DE STARTUP**
*Quando bot inicia*

```
🚀 BOT MULTI-CRYPTO ATIVO!

🤖 BitDash Trading Bot
⏰ Iniciado: 25/07/2025 16:01:15
📡 API: ☁️ Cloud
🎯 Cryptos: Bitcoin, Ethereum, XRP

✅ Sistema funcionando!
📊 Sinais serão enviados automaticamente

---
🔄 Próximo resumo em 15 minutos
```

## 🔧 **ALERTA DE SISTEMA**
*Quando há problemas técnicos*

```
⚠️ ALERTA DO SISTEMA

❌ Erro no sistema:
API timeout - tentando reconectar...

🔧 Status: Recuperando
⏰ 25/07/2025 16:01:15

---
BitDash Alert System
```

---

# 📈 **FREQUÊNCIA DOS ALERTAS**

## 🔄 **ALERTAS AUTOMÁTICOS** (Task Scheduler - A cada 15 min)
- Verificação de mudanças ≥ 3%
- **~96 verificações/dia**
- **~5-15 alertas/dia** (conforme volatilidade)

## 📊 **RESUMOS COMPLETOS** (Bot completo - Se activado)
- Resumos detalhados a cada 15 min
- Verificação de mudanças a cada 5 min
- **~96 resumos/dia + alertas extras**

## 🎯 **TOTAL ESPERADO**
- **Modo webhook:** ~100-115 mensagens/dia
- **Bot completo:** ~150-200 mensagens/dia
- **Alta volatilidade:** Até 300+ mensagens/dia

---

# ⚙️ **CONFIGURAÇÕES ATUAIS**

| Parâmetro | Valor | Descrição |
|-----------|--------|-----------|
| Threshold | 3% | Mudança mínima para alertar |
| Intervalo | 15 min | Frequência de verificação |
| Cryptos | 3 | Bitcoin, Ethereum, XRP |
| API | Cloud | Render.com (24/7) |
| Bot | Telegram | Mensagens HTML |
| Cache | 5 min | TTL para reduzir spam |

---

*🎯 Todos estes alertas chegam diretamente ao teu Telegram!*
