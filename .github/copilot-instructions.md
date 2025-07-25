<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Instruções do Copilot para Dashboard Bitcoin

Este é um projeto de dashboard web para monitoramento de preços de Bitcoin com sistema de alertas.

## Contexto do Projeto

- **Tipo**: Aplicação web estática (HTML, CSS, JavaScript)
- **Propósito**: Monitorar preços de Bitcoin e configurar alertas personalizados
- **API**: CoinGecko API (gratuita) para dados de criptomoedas
- **Armazenamento**: LocalStorage para persistir alertas
- **UI**: Design moderno com Chart.js para gráficos

## Estrutura dos Arquivos

- `index.html`: Interface principal com layout responsivo
- `styles.css`: Estilos modernos com gradientes e animações
- `script.js`: Lógica da aplicação, classe BitcoinDashboard principal
- `package.json`: Configurações do projeto e scripts
- `README.md`: Documentação completa

## Funcionalidades Principais

1. **Monitoramento de Preços**: Atualização automática a cada 30 segundos
2. **Sistema de Alertas**: Configuração de alertas acima/abaixo de valores
3. **Integração com Telegram**: Envio de alertas via bot do Telegram
4. **Gráfico em Tempo Real**: Histórico de preços com Chart.js
5. **Notificações**: Browser notifications + Telegram quando alertas são disparados
6. **Responsividade**: Interface adaptada para mobile e desktop

## Padrões de Código

- Use ES6+ (classes, arrow functions, async/await)
- Mantenha o código modular na classe BitcoinDashboard
- Use localStorage para persistência local
- Implemente error handling para chamadas de API
- Mantenha consistência visual com a paleta de cores Bitcoin (#f7931a)

## APIs e Bibliotecas

- **CoinGecko API**: `https://api.coingecko.com/api/v3/simple/price`
- **Telegram Bot API**: `https://api.telegram.org/bot{token}/` para envio de mensagens
- **Chart.js**: Para gráficos interativos
- **Font Awesome**: Para ícones
- **Notifications API**: Para alertas do navegador

## Convenções

- Nomes de funções em camelCase
- Classes com PascalCase
- IDs de elementos descritivos
- Comentários em português
- Console.log para debugging

## Melhorias Futuras

- Suporte a múltiplas criptomoedas
- Tema escuro/claro
- Exportar/importar configurações
- Integração com Discord
- Alertas sonoros
- Alertas recorrentes
