// Configurações e Estado da Aplicação
class BitcoinDashboard {
    constructor() {
        this.apiKey = null; // Para APIs que requerem chave (opcional)
        this.currentPrice = 0;
        this.alerts = JSON.parse(localStorage.getItem('bitcoinAlerts')) || [];
        this.priceHistory = [];
        this.chart = null;
        this.updateInterval = null;
        this.isOnline = navigator.onLine;
        
        // Configurações do Telegram
        this.telegram = {
            botToken: localStorage.getItem('telegramBotToken') || '',
            chatId: localStorage.getItem('telegramChatId') || '',
            connected: false
        };
        
        this.init();
    }

    async init() {
        console.log('Inicializando Dashboard Bitcoin...');
        
        this.setupEventListeners();
        this.renderAlerts();
        this.updateAlertCount();
        this.initTelegram();
        
        // Aguardar um pouco para garantir que o DOM está completamente carregado
        setTimeout(() => {
            this.setupChart();
        }, 100);
        
        await this.fetchBitcoinPrice();
        this.startPriceUpdates();
        this.checkNetworkStatus();
        
        console.log('Dashboard inicializado com sucesso');
    }

    setupEventListeners() {
        // Form de alertas
        document.getElementById('alertForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createAlert();
        });

        // Form do Telegram
        document.getElementById('telegramForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.configureTelegram();
        });

        // Status da rede
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showNotification('Conexão restaurada', 'Voltando a monitorar preços', 'success');
            this.startPriceUpdates();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showNotification('Conexão perdida', 'Monitoramento pausado', 'warning');
            this.stopPriceUpdates();
        });

        // Fechar modals ao clicar fora
        document.getElementById('alertModal').addEventListener('click', (e) => {
            if (e.target.id === 'alertModal') {
                this.hideAlertModal();
            }
        });

        document.getElementById('telegramModal').addEventListener('click', (e) => {
            if (e.target.id === 'telegramModal') {
                this.hideTelegramModal();
            }
        });
    }

    async fetchBitcoinPrice() {
        if (!this.isOnline) {
            console.log('Sem conexão com a internet');
            return;
        }

        try {
            // Array de APIs com proxy EUR como prioridade
            const apis = [
                {
                    name: 'Proxy EUR',
                    url: 'http://localhost:8002/api/bitcoin-price',
                    parser: (data) => {
                        // Dados já convertidos para EUR pelo proxy
                        return {
                            eur: data.usd, // O proxy já converte USD para EUR
                            eur_24h_change: data.usd_24h_change || 0,
                            eur_24h_vol: data.usd_24h_vol || 21250000000,
                            eur_market_cap: data.usd_market_cap || 1955000000000,
                            source: data.source || 'Proxy EUR',
                            exchange_rate: data.exchange_rate,
                            original_usd_price: data.original_usd_price
                        };
                    }
                },
                {
                    name: 'Simulação (Fallback)',
                    url: null,
                    parser: () => {
                        // Manter preço próximo ao último conhecido ou usar base realista em EUR
                        const basePrice = this.currentPrice > 0 ? this.currentPrice : 100300; // ~118000 * 0.85
                        const variation = (Math.random() - 0.5) * 850; // ±425 EUR
                        return {
                            eur: basePrice + variation,
                            eur_24h_change: (Math.random() - 0.5) * 5, // ±2.5%
                            eur_24h_vol: 21250000000, // 25B * 0.85
                            eur_market_cap: 1955000000000, // 2.3T * 0.85
                            source: 'Simulação'
                        };
                    }
                }
            ];

            let bitcoinData = null;
            let usedApi = null;
            let lastError = null;

            // Tentar cada API até uma funcionar
            for (const api of apis) {
                try {
                    console.log(`Tentando API: ${api.name}`);
                    
                    if (api.url === null) {
                        // Simulação como último recurso
                        bitcoinData = api.parser();
                        usedApi = api.name;
                        console.log(`Usando dados simulados: ${api.name}`);
                        break;
                    }
                    
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 segundos timeout
                    
                    const response = await fetch(api.url, {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'Cache-Control': 'no-cache'
                        },
                        cache: 'no-cache',
                        signal: controller.signal
                    });
                    
                    clearTimeout(timeoutId);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const data = await response.json();
                    
                    // Verificar se houve erro no proxy
                    if (data && data.error) {
                        throw new Error(data.message || data.error);
                    }
                    
                    bitcoinData = api.parser(data);
                    usedApi = bitcoinData.source || api.name;
                    console.log(`✅ Sucesso com API: ${usedApi} - €${bitcoinData.eur}`);
                    break;

                } catch (apiError) {
                    lastError = apiError;
                    console.warn(`❌ Erro na API ${api.name}:`, apiError.message);
                    
                    // Se for o primeiro (proxy local) e falhar, dar feedback mas não mostrar erro ainda
                    if (api.name === 'Proxy Local') {
                        console.log('Proxy local indisponível, tentando APIs diretas...');
                    }
                    
                    // Pequena pausa entre tentativas para evitar spam
                    await new Promise(resolve => setTimeout(resolve, 500));
                    continue;
                }
            }

            if (!bitcoinData) {
                throw new Error(`Todas as APIs falharam. Último erro: ${lastError?.message}`);
            }

            // Garantir que temos um valor numérico válido
            if (!bitcoinData.eur || isNaN(bitcoinData.eur) || bitcoinData.eur <= 0) {
                throw new Error('Dados de preço inválidos recebidos');
            }

            // Atualizar preço atual
            this.currentPrice = bitcoinData.eur;
            
            // Adicionar ao histórico de preços
            this.priceHistory.push({
                price: this.currentPrice,
                timestamp: new Date(),
                source: usedApi
            });

            // Manter apenas últimas 100 entradas
            if (this.priceHistory.length > 100) {
                this.priceHistory.shift();
            }

            this.updateUI(bitcoinData);
            this.checkAlerts();
            this.updatePriceChart();
            this.updateLastUpdateTime(usedApi);

            // Limpar mensagens de erro anteriores se houver sucesso
            this.clearErrorState();

            // Mostrar notificação especial apenas se estiver realmente simulando
            if (usedApi && usedApi.includes('Simulação')) {
                this.showNotification('Modo Simulação', 'APIs indisponíveis, usando dados simulados', 'warning');
            } else if (usedApi && usedApi.includes('CoinLore')) {
                // Se estiver usando CoinLore via proxy, mostrar como dados reais
                console.log(`✅ Dados reais obtidos via ${usedApi}`);
            } else if (usedApi && usedApi.includes('CoinGecko')) {
                // Se estiver usando CoinGecko via proxy, mostrar como dados reais
                console.log(`✅ Dados reais obtidos via ${usedApi}`);
            }

        } catch (error) {
            console.error('❌ Erro crítico ao buscar preço do Bitcoin:', error);
            this.handleConnectionError(error);
        }
    }

    updateUI(data) {
        // Preço atual
        document.getElementById('currentPrice').textContent = `€${data.eur.toLocaleString('pt-PT', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}`;

        // Mudança de preço 24h
        const priceChangeElement = document.getElementById('priceChange');
        const change24h = data.eur_24h_change || 0;
        priceChangeElement.textContent = `${change24h > 0 ? '+' : ''}${change24h.toFixed(2)}%`;
        priceChangeElement.className = `price-change ${change24h >= 0 ? 'positive' : 'negative'}`;

        // Estatísticas (convertidas para EUR)
        document.getElementById('volume24h').textContent = `€${(data.eur_24h_vol || 21250000000).toLocaleString()}`;
        document.getElementById('marketCap').textContent = `€${(data.eur_market_cap || 680000000000).toLocaleString()}`;
        
        // High/Low 24h (simulados baseados no preço atual em EUR)
        const high24h = data.eur * 1.05; // Simulação
        const low24h = data.eur * 0.95;  // Simulação
        document.getElementById('high24h').textContent = `€${high24h.toLocaleString('pt-PT', {minimumFractionDigits: 2})}`;
        document.getElementById('low24h').textContent = `€${low24h.toLocaleString('pt-PT', {minimumFractionDigits: 2})}`;
    }

    updateLastUpdateTime(apiSource = '') {
        const now = new Date();
        const timeString = now.toLocaleTimeString('pt-BR');
        
        // Determinar status baseado na fonte real dos dados
        let statusClass = 'online';
        let statusText = 'Conectado';
        
        if (apiSource.includes('Simulação')) {
            statusClass = 'offline';
            statusText = 'Simulação';
        } else if (apiSource.includes('CoinGecko') || apiSource.includes('CoinLore')) {
            statusClass = 'online';
            statusText = 'Dados Reais';
        }
        
        const sourceText = apiSource ? ` (${apiSource})` : '';
        document.getElementById('lastUpdate').innerHTML = `
            <span class="status-indicator ${statusClass}"></span>
            Última atualização: ${timeString}${sourceText}
        `;
        
        // Atualizar status no card de conexão também
        const connectionStatus = document.getElementById('connectionStatus');
        if (connectionStatus) {
            connectionStatus.innerHTML = `
                <span class="status-indicator ${statusClass}"></span>
                <span>${statusText}</span>
            `;
            connectionStatus.classList.remove('error');
        }
    }

    handleConnectionError(error) {
        console.error('Erro de conexão:', error);
        
        // Não mostrar erro se estivermos conseguindo dados (mesmo que simulados)
        if (this.currentPrice > 0) {
            console.log('Mantendo dados anteriores, erro temporário');
            return;
        }
        
        // Mostrar erro na interface apenas se não conseguirmos nenhum dado
        this.showNotification('Conectividade Limitada', 'Tentando reconectar...', 'warning');
        
        // Atualizar status visual
        document.getElementById('lastUpdate').innerHTML = `
            <span class="status-indicator offline"></span>
            Reconectando... - ${new Date().toLocaleTimeString('pt-BR')}
        `;

        // Atualizar status de conexão no card
        const connectionStatus = document.getElementById('connectionStatus');
        if (connectionStatus) {
            connectionStatus.innerHTML = `
                <span class="status-indicator offline"></span>
                <span>Reconectando...</span>
            `;
            connectionStatus.classList.add('error');
        }
        
        // Mostrar preço como indisponível apenas se não tiver dados
        if (this.currentPrice === 0) {
            document.getElementById('currentPrice').textContent = 'Carregando...';
            document.getElementById('priceChange').textContent = '--';
            document.getElementById('priceChange').className = 'price-change';
        }
        
        // Tentar novamente em 15 segundos (intervalo maior para evitar spam)
        setTimeout(() => {
            if (this.isOnline) {
                console.log('Tentativa de reconexão...');
                this.fetchBitcoinPrice();
            }
        }, 15000);
    }

    clearErrorState() {
        // Remover qualquer indicação de erro se a conexão foi restaurada
        const notifications = document.querySelectorAll('.notification.error');
        notifications.forEach(notification => {
            if (notification.textContent.includes('Erro de Conexão')) {
                notification.remove();
            }
        });

        // Restaurar status de conexão
        const connectionStatus = document.getElementById('connectionStatus');
        if (connectionStatus) {
            connectionStatus.innerHTML = `
                <span class="status-indicator online"></span>
                <span>Conectado</span>
            `;
            connectionStatus.classList.remove('error');
        }
    }

    setupChart() {
        const chartElement = document.getElementById('priceChart');
        if (!chartElement) {
            console.error('Elemento priceChart não encontrado!');
            return;
        }

        // Destruir gráfico existente se houver
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }

        try {
            console.log('Configurando gráfico Chart.js...');
            
            const ctx = chartElement.getContext('2d');
            if (!ctx) {
                console.error('Não foi possível obter contexto 2D do canvas');
                return;
            }

            // Verificar se Chart.js está disponível
            if (typeof Chart === 'undefined') {
                console.error('Chart.js não está carregado!');
                return;
            }

            this.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Preço Bitcoin (EUR)',
                        data: [],
                        borderColor: '#f7931a',
                        backgroundColor: 'rgba(247, 147, 26, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#f7931a',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 1000,
                        easing: 'easeInOutQuart'
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    return 'Preço: €' + context.parsed.y.toLocaleString('pt-PT', {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2
                                    });
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)',
                                drawBorder: false
                            },
                            ticks: {
                                maxTicksLimit: 10
                            }
                        },
                        y: {
                            display: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)',
                                drawBorder: false
                            },
                            ticks: {
                                callback: function(value) {
                                    return '€' + value.toLocaleString('pt-PT', {
                                        minimumFractionDigits: 0,
                                        maximumFractionDigits: 0
                                    });
                                }
                            }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            });

            console.log('✅ Gráfico configurado com sucesso:', this.chart);
            
            // Se já temos dados de histórico, atualizar o gráfico
            if (this.priceHistory.length > 0) {
                this.updatePriceChart();
            }

        } catch (error) {
            console.error('❌ Erro ao configurar gráfico:', error);
            this.chart = null;
        }
    }

    updatePriceChart() {
        if (!this.chart) {
            console.warn('Gráfico não inicializado, tentando configurar...');
            this.setupChart();
            return;
        }
        
        if (this.priceHistory.length === 0) {
            console.log('Sem dados de histórico para o gráfico');
            return;
        }

        try {
            const labels = this.priceHistory.map(item => 
                item.timestamp.toLocaleTimeString('pt-BR', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                })
            );

            const prices = this.priceHistory.map(item => item.price);

            this.chart.data.labels = labels;
            this.chart.data.datasets[0].data = prices;
            this.chart.update('none');
            
            console.log(`Gráfico atualizado com ${prices.length} pontos de dados`);
        } catch (error) {
            console.error('Erro ao atualizar gráfico:', error);
            // Tentar recriar o gráfico se houver erro
            this.setupChart();
        }
    }

    createAlert() {
        const type = document.getElementById('alertType').value;
        const price = parseFloat(document.getElementById('alertPrice').value);
        const name = document.getElementById('alertName').value || `Alerta ${type === 'above' ? 'acima' : 'abaixo'} de €${price}`;
        const telegramAlert = document.getElementById('telegramAlert').checked;

        if (!price || price <= 0) {
            this.showNotification('Erro', 'Por favor, insira um preço válido', 'error');
            return;
        }

        const alert = {
            id: Date.now(),
            type: type,
            price: price,
            name: name,
            created: new Date(),
            active: true,
            telegram: telegramAlert && this.telegram.connected
        };

        this.alerts.push(alert);
        this.saveAlerts();
        this.renderAlerts();
        this.updateAlertCount();
        this.hideAlertModal();
        
        const telegramStatus = alert.telegram ? ' (com Telegram)' : '';
        this.showNotification('Alerta Criado', `Alerta "${name}" foi configurado com sucesso${telegramStatus}`, 'success');
        
        // Limpar formulário
        document.getElementById('alertForm').reset();
        document.getElementById('telegramAlert').checked = true; // Reset para checked
    }

    deleteAlert(alertId) {
        if (confirm('Tem certeza que deseja excluir este alerta?')) {
            this.alerts = this.alerts.filter(alert => alert.id !== alertId);
            this.saveAlerts();
            this.renderAlerts();
            this.updateAlertCount();
            this.showNotification('Alerta Removido', 'Alerta foi removido com sucesso', 'success');
        }
    }

    checkAlerts() {
        this.alerts.forEach(alert => {
            if (!alert.active) return;

            const triggered = (alert.type === 'above' && this.currentPrice >= alert.price) ||
                            (alert.type === 'below' && this.currentPrice <= alert.price);

            if (triggered) {
                alert.active = false;
                this.saveAlerts();
                this.renderAlerts();
                this.updateAlertCount();

                const message = alert.type === 'above' 
                    ? `Bitcoin atingiu €${this.currentPrice.toLocaleString()} (acima de €${alert.price.toLocaleString()})`
                    : `Bitcoin caiu para €${this.currentPrice.toLocaleString()} (abaixo de €${alert.price.toLocaleString()})`;

                this.showNotification('🚨 Alerta Disparado!', message, 'warning');
                
                // Notificação do navegador (se permitida)
                this.showBrowserNotification(alert.name, message);

                // Enviar para o Telegram se configurado
                if (alert.telegram && this.telegram.connected) {
                    this.sendTelegramAlert(alert, message);
                }
            }
        });
    }

    showBrowserNotification(title, body) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: body,
                icon: 'https://cryptologos.cc/logos/bitcoin-btc-logo.png',
                badge: 'https://cryptologos.cc/logos/bitcoin-btc-logo.png'
            });
        } else if ('Notification' in window && Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification(title, {
                        body: body,
                        icon: 'https://cryptologos.cc/logos/bitcoin-btc-logo.png'
                    });
                }
            });
        }
    }

    renderAlerts() {
        const alertsList = document.getElementById('alertsList');
        
        if (this.alerts.length === 0) {
            alertsList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-bell-slash"></i>
                    <p>Nenhum alerta configurado</p>
                    <small>Clique em "Novo Alerta" para começar</small>
                </div>
            `;
            return;
        }

        alertsList.innerHTML = this.alerts.map(alert => `
            <div class="alert-item ${!alert.active ? 'triggered' : ''} ${alert.telegram ? 'telegram' : ''}">
                <div class="alert-info">
                    <h4>
                        ${alert.name}
                        ${alert.telegram ? '<span class="telegram-badge"><i class="fab fa-telegram-plane"></i> Telegram</span>' : ''}
                    </h4>
                    <p>
                        ${alert.type === 'above' ? 'Acima de' : 'Abaixo de'} 
                        €${alert.price.toLocaleString('pt-PT', {minimumFractionDigits: 2})}
                        ${!alert.active ? ' - <strong>DISPARADO</strong>' : ''}
                    </p>
                    <small>Criado em: ${alert.created.toLocaleString ? alert.created.toLocaleString('pt-BR') : new Date(alert.created).toLocaleString('pt-BR')}</small>
                </div>
                <div class="alert-actions">
                    <button class="btn btn-delete" onclick="dashboard.deleteAlert(${alert.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    updateAlertCount() {
        const activeCount = this.alerts.filter(alert => alert.active).length;
        document.getElementById('activeAlerts').textContent = activeCount;
    }

    saveAlerts() {
        localStorage.setItem('bitcoinAlerts', JSON.stringify(this.alerts));
    }

    showAlertModal() {
        document.getElementById('alertModal').style.display = 'block';
        document.getElementById('alertPrice').focus();
    }

    hideAlertModal() {
        document.getElementById('alertModal').style.display = 'none';
    }

    showNotification(title, message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <h4>${title}</h4>
            <p>${message}</p>
        `;

        const notifications = document.getElementById('notifications');
        notifications.appendChild(notification);

        // Remover notificação após 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    startPriceUpdates() {
        this.stopPriceUpdates();
        // Atualizar a cada 60 segundos (reduzido para evitar spam no proxy)
        this.updateInterval = setInterval(() => {
            this.fetchBitcoinPrice();
        }, 60000);
        
        console.log('✅ Atualizações automáticas iniciadas (60s)');
    }

    stopPriceUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    async manualRefresh() {
        const refreshBtn = document.getElementById('refreshBtn');
        refreshBtn.classList.add('loading');
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Atualizando...';
        
        try {
            await this.fetchBitcoinPrice();
            this.showNotification('Atualizado!', 'Preços atualizados manualmente', 'success');
        } catch (error) {
            this.showNotification('Erro', 'Falha na atualização manual', 'error');
        } finally {
            refreshBtn.classList.remove('loading');
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Atualizar';
        }
    }

    async testConnectivity() {
        try {
            // Teste simples de conectividade
            const response = await fetch('https://httpbin.org/get', {
                method: 'GET',
                cache: 'no-cache',
                signal: AbortSignal.timeout(5000) // Timeout de 5 segundos
            });
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    checkNetworkStatus() {
        // Verificar status da rede periodicamente
        setInterval(() => {
            const wasOnline = this.isOnline;
            this.isOnline = navigator.onLine;
            
            if (wasOnline !== this.isOnline) {
                this.updateLastUpdateTime();
            }
        }, 5000);
    }

    // Método para atualizar período do gráfico (para futura implementação)
    updateChartPeriod(period) {
        // Remover classe active de todos os botões
        document.querySelectorAll('.chart-controls .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Adicionar classe active ao botão clicado
        if (event && event.target) {
            event.target.classList.add('active');
        }
        
        // Aqui você pode implementar lógica para diferentes períodos
        // Por enquanto, apenas feedback visual
        this.showNotification('Período Alterado', `Visualizando dados de ${period}`, 'info');
        
        // Forçar atualização do gráfico
        if (this.chart && this.priceHistory.length > 0) {
            this.updatePriceChart();
        }
    }

    // ===== MÉTODOS DO TELEGRAM =====

    initTelegram() {
        if (this.telegram.botToken) {
            this.checkTelegramConnection();
        }
        this.updateTelegramStatus();
    }

    async configureTelegram() {
        const botToken = document.getElementById('botToken').value.trim();
        const chatId = document.getElementById('chatId').value.trim();

        if (!botToken) {
            this.showNotification('Erro', 'Token do bot é obrigatório', 'error');
            return;
        }

        // Validar formato do token
        if (!botToken.match(/^\d+:[A-Za-z0-9_-]+$/)) {
            this.showNotification('Erro', 'Formato do token inválido', 'error');
            return;
        }

        this.telegram.botToken = botToken;
        this.telegram.chatId = chatId;

        // Salvar no localStorage
        localStorage.setItem('telegramBotToken', botToken);
        if (chatId) {
            localStorage.setItem('telegramChatId', chatId);
        }

        // Testar conexão
        const connected = await this.checkTelegramConnection();
        
        if (connected) {
            this.hideTelegramModal();
            this.showNotification('Telegram Conectado!', 'Alertas serão enviados para o Telegram', 'success');
        }
    }

    async checkTelegramConnection() {
        if (!this.telegram.botToken) {
            this.telegram.connected = false;
            this.updateTelegramStatus();
            return false;
        }

        try {
            const response = await fetch(`https://api.telegram.org/bot${this.telegram.botToken}/getMe`);
            const data = await response.json();

            if (data.ok) {
                this.telegram.connected = true;
                
                // Se não tiver chatId, tentar detectar automaticamente
                if (!this.telegram.chatId) {
                    await this.detectChatId();
                }
                
                this.updateTelegramStatus();
                return true;
            } else {
                throw new Error(data.description || 'Token inválido');
            }
        } catch (error) {
            this.telegram.connected = false;
            this.updateTelegramStatus();
            this.showNotification('Erro no Telegram', `Não foi possível conectar: ${error.message}`, 'error');
            return false;
        }
    }

    async detectChatId() {
        try {
            const response = await fetch(`https://api.telegram.org/bot${this.telegram.botToken}/getUpdates`);
            const data = await response.json();

            if (data.ok && data.result.length > 0) {
                // Pegar o chat_id da mensagem mais recente
                const lastMessage = data.result[data.result.length - 1];
                this.telegram.chatId = lastMessage.message.chat.id.toString();
                localStorage.setItem('telegramChatId', this.telegram.chatId);
                
                this.showNotification('Chat ID Detectado', `Chat ID: ${this.telegram.chatId}`, 'success');
            } else {
                this.showNotification('Chat ID não encontrado', 'Envie /start para o bot primeiro', 'warning');
            }
        } catch (error) {
            console.error('Erro ao detectar Chat ID:', error);
        }
    }

    async sendTelegramAlert(alert, message) {
        if (!this.telegram.connected || !this.telegram.chatId) {
            console.log('Telegram não configurado ou Chat ID não encontrado');
            return;
        }

        const telegramMessage = `🚨 *ALERTA BITCOIN DISPARADO!*\n\n` +
                              `📊 *${alert.name}*\n` +
                              `💰 Preço atual: *€${this.currentPrice.toLocaleString()}*\n` +
                              `🎯 Condição: ${alert.type === 'above' ? 'Acima de' : 'Abaixo de'} €${alert.price.toLocaleString()}\n` +
                              `⏰ ${new Date().toLocaleString('pt-BR')}\n\n` +
                              `${message}`;

        try {
            const response = await fetch(`https://api.telegram.org/bot${this.telegram.botToken}/sendMessage`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    chat_id: this.telegram.chatId,
                    text: telegramMessage,
                    parse_mode: 'Markdown'
                })
            });

            const data = await response.json();
            
            if (data.ok) {
                console.log('Alerta enviado para o Telegram com sucesso');
            } else {
                console.error('Erro ao enviar para o Telegram:', data.description);
                this.showNotification('Erro no Telegram', 'Não foi possível enviar alerta', 'error');
            }
        } catch (error) {
            console.error('Erro ao enviar mensagem para o Telegram:', error);
            this.showNotification('Erro no Telegram', 'Falha na comunicação', 'error');
        }
    }

    async testTelegram() {
        if (!this.telegram.botToken) {
            this.showNotification('Erro', 'Configure o token primeiro', 'error');
            return;
        }

        const connected = await this.checkTelegramConnection();
        
        if (connected && this.telegram.chatId) {
            const testMessage = `🤖 *Teste de Conexão - Dashboard Bitcoin*\n\n` +
                              `✅ Bot conectado com sucesso!\n` +
                              `💰 Preço atual do Bitcoin: *€${this.currentPrice.toLocaleString()}*\n` +
                              `⏰ ${new Date().toLocaleString('pt-BR')}\n\n` +
                              `Agora você receberá alertas neste chat! 🚀`;

            try {
                const response = await fetch(`https://api.telegram.org/bot${this.telegram.botToken}/sendMessage`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        chat_id: this.telegram.chatId,
                        text: testMessage,
                        parse_mode: 'Markdown'
                    })
                });

                const data = await response.json();
                
                if (data.ok) {
                    this.showNotification('Teste Enviado!', 'Verifique seu Telegram', 'success');
                } else {
                    this.showNotification('Erro no Teste', data.description, 'error');
                }
            } catch (error) {
                this.showNotification('Erro no Teste', 'Falha na comunicação', 'error');
            }
        } else {
            this.showNotification('Erro no Teste', 'Conexão não estabelecida ou Chat ID não encontrado', 'error');
        }
    }

    updateTelegramStatus() {
        const statusElement = document.getElementById('telegramStatus');
        const connectionStatusElement = document.getElementById('telegramConnectionStatus');
        
        if (this.telegram.connected) {
            statusElement.innerHTML = `
                <i class="fab fa-telegram-plane"></i>
                <span>Telegram: Conectado</span>
            `;
            statusElement.classList.add('connected');
            
            if (connectionStatusElement) {
                connectionStatusElement.innerHTML = `
                    <span class="status-indicator online"></span>
                    <span>Conectado - Chat ID: ${this.telegram.chatId || 'Detectando...'}</span>
                `;
            }
        } else {
            statusElement.innerHTML = `
                <i class="fab fa-telegram-plane"></i>
                <span>Telegram: Desconectado</span>
            `;
            statusElement.classList.remove('connected');
            
            if (connectionStatusElement) {
                connectionStatusElement.innerHTML = `
                    <span class="status-indicator offline"></span>
                    <span>Não configurado</span>
                `;
            }
        }
    }

    showTelegramModal() {
        document.getElementById('telegramModal').style.display = 'block';
        
        // Preencher campos se já configurado
        if (this.telegram.botToken) {
            document.getElementById('botToken').value = this.telegram.botToken;
        }
        if (this.telegram.chatId) {
            document.getElementById('chatId').value = this.telegram.chatId;
        }
        
        document.getElementById('botToken').focus();
    }

    hideTelegramModal() {
        document.getElementById('telegramModal').style.display = 'none';
    }
}

// Funções globais para o HTML
function showAlertModal() {
    dashboard.showAlertModal();
}

function hideAlertModal() {
    dashboard.hideAlertModal();
}

function showTelegramModal() {
    dashboard.showTelegramModal();
}

function hideTelegramModal() {
    dashboard.hideTelegramModal();
}

function testTelegram() {
    dashboard.testTelegram();
}

function updateChart(period) {
    if (dashboard) {
        dashboard.updateChartPeriod(period);
    }
}

// Inicializar a aplicação
let dashboard;

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM carregado, aguardando Chart.js...');
    
    // Aguardar Chart.js estar disponível
    const initDashboard = () => {
        if (typeof Chart !== 'undefined') {
            console.log('Chart.js disponível, inicializando dashboard...');
            dashboard = new BitcoinDashboard();
            
            // Solicitar permissão para notificações
            if ('Notification' in window && Notification.permission === 'default') {
                Notification.requestPermission();
            }
        } else {
            console.log('Aguardando Chart.js...');
            setTimeout(initDashboard, 100);
        }
    };
    
    initDashboard();
});

// Service Worker para funcionalidade offline (opcional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registrado: ', registration);
            })
            .catch(registrationError => {
                console.log('SW falhou: ', registrationError);
            });
    });
}
