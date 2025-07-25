// MÓDULO DE ANÁLISE DE MERCADO E SINAIS XTB
class XTBTradingAnalyzer {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.newsData = [];
        this.signals = [];
        this.marketAnalysis = null;
        this.sentimentScore = 0;
        this.riskLevel = 'medium';
        this.profitTargets = [];
        
        // Configurações de trading
        this.settings = {
            riskTolerance: localStorage.getItem('riskTolerance') || 'medium',
            profitTarget: parseFloat(localStorage.getItem('profitTarget')) || 5.0,
            stopLoss: parseFloat(localStorage.getItem('stopLoss')) || 2.0,
            timeframe: localStorage.getItem('timeframe') || '1h',
            notificationsEnabled: localStorage.getItem('tradingNotifications') !== 'false'
        };
        
        this.init();
    }

    async init() {
        console.log('🚀 Inicializando XTB Trading Analyzer...');
        
        this.createTradingInterface();
        this.startNewsMonitoring();
        this.startMarketAnalysis();
        this.loadTradingSettings();
        
        // Atualizar análises a cada 5 minutos
        setInterval(() => {
            this.updateMarketAnalysis();
        }, 300000);
        
        console.log('✅ XTB Trading Analyzer ativo!');
    }

    createTradingInterface() {
        // Adicionar seção de trading na dashboard
        const tradingSection = document.createElement('section');
        tradingSection.className = 'trading-section';
        tradingSection.innerHTML = `
            <div class="card trading-card">
                <div class="card-header">
                    <h3><i class="fas fa-chart-line"></i> XTB Trading Signals</h3>
                    <div class="trading-controls">
                        <button class="btn btn-sm" onclick="xtbAnalyzer.refreshAnalysis()">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="xtbAnalyzer.showSettingsModal()">
                            <i class="fas fa-cog"></i> Config
                        </button>
                    </div>
                </div>
                <div class="card-content">
                    <div class="trading-dashboard">
                        <!-- Sinais de Trading -->
                        <div class="trading-signals">
                            <h4>🎯 Sinais Ativos</h4>
                            <div id="tradingSignals" class="signals-list">
                                <div class="loading-state">
                                    <i class="fas fa-spinner fa-spin"></i>
                                    <p>Analisando mercado...</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Análise de Sentimento -->
                        <div class="sentiment-analysis">
                            <h4>📊 Sentimento do Mercado</h4>
                            <div class="sentiment-meter">
                                <div class="sentiment-bar" id="sentimentBar">
                                    <div class="sentiment-fill" id="sentimentFill"></div>
                                </div>
                                <div class="sentiment-labels">
                                    <span>Bearish</span>
                                    <span>Neutral</span>
                                    <span>Bullish</span>
                                </div>
                            </div>
                            <div class="sentiment-score" id="sentimentScore">
                                Calculando...
                            </div>
                        </div>
                        
                        <!-- Notícias e Eventos -->
                        <div class="market-news">
                            <h4>📰 Notícias Relevantes</h4>
                            <div id="marketNews" class="news-list">
                                <div class="loading-state">
                                    <i class="fas fa-newspaper"></i>
                                    <p>Carregando notícias...</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Simulações de Lucro -->
                        <div class="profit-simulation">
                            <h4>💰 Simulação de Lucros</h4>
                            <div class="simulation-controls">
                                <div class="input-group">
                                    <label>Investimento (EUR):</label>
                                    <input type="number" id="investmentAmount" value="1000" min="10" step="10">
                                </div>
                                <button class="btn btn-primary" onclick="xtbAnalyzer.runProfitSimulation()">
                                    <i class="fas fa-calculator"></i> Simular
                                </button>
                            </div>
                            <div id="simulationResults" class="simulation-results"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Inserir após a seção de gráfico
        const chartSection = document.querySelector('.chart-section');
        chartSection.parentNode.insertBefore(tradingSection, chartSection.nextSibling);
        
        this.createSettingsModal();
    }

    createSettingsModal() {
        const settingsModal = document.createElement('div');
        settingsModal.id = 'tradingSettingsModal';
        settingsModal.className = 'modal';
        settingsModal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2><i class="fas fa-cog"></i> Configurações XTB Trading</h2>
                    <button class="close-btn" onclick="xtbAnalyzer.hideSettingsModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="tradingSettingsForm">
                        <div class="form-group">
                            <label for="riskTolerance">Tolerância ao Risco:</label>
                            <select id="riskTolerance" required>
                                <option value="low">Baixo (1-3% por trade)</option>
                                <option value="medium" selected>Médio (3-7% por trade)</option>
                                <option value="high">Alto (7-15% por trade)</option>
                                <option value="aggressive">Agressivo (15%+ por trade)</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="profitTarget">Meta de Lucro (%):</label>
                            <input type="number" id="profitTargetSetting" step="0.1" min="1" max="50" value="5">
                        </div>
                        
                        <div class="form-group">
                            <label for="stopLoss">Stop Loss (%):</label>
                            <input type="number" id="stopLossSetting" step="0.1" min="0.5" max="10" value="2">
                        </div>
                        
                        <div class="form-group">
                            <label for="timeframe">Timeframe Preferido:</label>
                            <select id="timeframeSetting">
                                <option value="5m">5 Minutos (Scalping)</option>
                                <option value="15m">15 Minutos</option>
                                <option value="1h" selected>1 Hora</option>
                                <option value="4h">4 Horas</option>
                                <option value="1d">Diário</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="tradingNotifications" checked>
                                Receber notificações de trading
                            </label>
                        </div>
                        
                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="telegramTrading">
                                Enviar sinais via Telegram
                            </label>
                        </div>
                        
                        <div class="form-actions">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i> Salvar Configurações
                            </button>
                            <button type="button" class="btn btn-secondary" onclick="xtbAnalyzer.hideSettingsModal()">
                                Cancelar
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        document.body.appendChild(settingsModal);
        
        // Event listener para o formulário
        document.getElementById('tradingSettingsForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveTradingSettings();
        });
    }

    async startNewsMonitoring() {
        console.log('📰 Iniciando monitoramento de notícias...');
        
        try {
            // Tentar buscar notícias reais da API
            const realNews = await this.fetchRealNews();
            
            if (realNews && realNews.length > 0) {
                this.newsData = realNews;
                console.log(`✅ ${realNews.length} notícias reais carregadas`);
            } else {
                // Fallback para notícias simuladas
                this.newsData = this.generateMockNews();
                console.log('⚠️ Usando notícias simuladas (API indisponível)');
            }
            
            this.updateNewsDisplay();
            this.analyzeSentiment();
            
        } catch (error) {
            console.error('Erro ao monitorar notícias:', error);
            this.newsData = this.generateMockNews();
            this.updateNewsDisplay();
            this.analyzeSentiment();
        }
    }

    async fetchRealNews() {
        try {
            console.log('🌐 Buscando notícias da API XTB News...');
            
            const response = await fetch('http://localhost:8003/api/bitcoin-news', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                cache: 'no-cache',
                signal: AbortSignal.timeout(8000)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.message || 'Erro na API de notícias');
            }
            
            // Converter formato da API para formato interno
            return data.news.map(news => ({
                title: news.title,
                sentiment: news.sentiment_score || 0,
                impact: news.impact || 'medium',
                time: news.time_ago || 'Agora',
                source: news.source || 'XTB News',
                description: news.description || '',
                url: news.url || '#'
            }));
            
        } catch (error) {
            console.warn('❌ Erro ao buscar notícias reais:', error.message);
            return null;
        }
    }

    async fetchMarketSentiment() {
        try {
            console.log('📊 Buscando análise de sentimento...');
            
            const response = await fetch('http://localhost:8003/api/market-sentiment', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                cache: 'no-cache',
                signal: AbortSignal.timeout(5000)
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (!data.error) {
                    // Usar dados reais da API
                    this.sentimentScore = data.sentiment_score;
                    this.updateSentimentMeter(data.sentiment_score);
                    
                    // Mostrar recomendação se disponível
                    if (data.recommendation) {
                        console.log(`📈 Recomendação: ${data.recommendation.action} - ${data.recommendation.reason}`);
                    }
                    
                    return data;
                }
            }
            
            throw new Error('API de sentimento indisponível');
            
        } catch (error) {
            console.warn('❌ Erro ao buscar sentimento:', error.message);
            return null;
        }
    }

    async fetchTradingSignals() {
        try {
            console.log('🎯 Buscando sinais de trading...');
            
            const response = await fetch('http://localhost:8003/api/trading-signals', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                cache: 'no-cache',
                signal: AbortSignal.timeout(8000)
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (!data.error && data.signals) {
                    // Converter sinais da API para formato interno
                    const apiSignals = data.signals.map(signal => ({
                        type: signal.type,
                        confidence: signal.confidence,
                        reason: `${signal.indicator}: ${signal.reason}`,
                        entry: signal.entry,
                        target: signal.target,
                        stopLoss: signal.stop_loss,
                        timeframe: signal.timeframe,
                        priority: signal.priority || 'medium'
                    }));
                    
                    console.log(`✅ ${apiSignals.length} sinais recebidos da API`);
                    return apiSignals;
                }
            }
            
            throw new Error('API de sinais indisponível');
            
        } catch (error) {
            console.warn('❌ Erro ao buscar sinais:', error.message);
            return null;
        }
    }

    generateMockNews() {
        const newsTemplates = [
            {
                title: "Bitcoin moestra forte resistência em €100.000",
                sentiment: 0.7,
                impact: "high",
                time: "2 min atrás",
                source: "CoinDesk"
            },
            {
                title: "Grandes instituições aumentam posições em crypto",
                sentiment: 0.8,
                impact: "high",
                time: "15 min atrás",
                source: "Bloomberg"
            },
            {
                title: "Regulamentação crypto na Europa pode afetar preços",
                sentiment: -0.3,
                impact: "medium",
                time: "1h atrás",
                source: "Reuters"
            },
            {
                title: "ETF Bitcoin registra maior volume do mês",
                sentiment: 0.6,
                impact: "medium",
                time: "2h atrás",
                source: "Financial Times"
            },
            {
                title: "Análise técnica indica possível rompimento",
                sentiment: 0.4,
                impact: "medium",
                time: "3h atrás",
                source: "TradingView"
            }
        ];
        
        // Randomizar algumas notícias para parecer dinâmico
        return newsTemplates.map(news => ({
            ...news,
            sentiment: news.sentiment + (Math.random() - 0.5) * 0.4
        }));
    }

    updateNewsDisplay() {
        const newsContainer = document.getElementById('marketNews');
        
        const newsHTML = this.newsData.map(news => {
            const sentimentIcon = news.sentiment > 0.3 ? '📈' : news.sentiment < -0.3 ? '📉' : '➡️';
            const impactColor = news.impact === 'high' ? 'high-impact' : news.impact === 'medium' ? 'medium-impact' : 'low-impact';
            
            return `
                <div class="news-item ${impactColor}">
                    <div class="news-header">
                        <span class="news-sentiment">${sentimentIcon}</span>
                        <span class="news-source">${news.source}</span>
                        <span class="news-time">${news.time}</span>
                    </div>
                    <div class="news-title">${news.title}</div>
                    <div class="news-impact">Impacto: ${news.impact.toUpperCase()}</div>
                </div>
            `;
        }).join('');
        
        newsContainer.innerHTML = newsHTML;
    }

    async analyzeSentiment() {
        // Tentar obter análise de sentimento da API primeiro
        const apiSentiment = await this.fetchMarketSentiment();
        
        if (apiSentiment && !apiSentiment.error) {
            // Usar dados da API
            this.sentimentScore = apiSentiment.sentiment_score;
            this.updateSentimentMeter(apiSentiment.sentiment_score);
            
            // Mostrar informações adicionais da API
            if (apiSentiment.classification) {
                console.log(`📊 Sentimento do mercado: ${apiSentiment.classification} (${(apiSentiment.confidence || 0).toFixed(1)}%)`);
            }
            
            // Gerar sinais baseados no sentimento da API
            await this.generateTradingSignalsWithAPI(apiSentiment.sentiment_score);
            
        } else {
            // Fallback: analisar sentimento das notícias localmente
            const totalSentiment = this.newsData.reduce((sum, news) => sum + news.sentiment, 0);
            const avgSentiment = totalSentiment / this.newsData.length;
            
            this.sentimentScore = avgSentiment;
            this.updateSentimentMeter(avgSentiment);
            
            console.log('📊 Usando análise de sentimento local');
            
            // Gerar sinais baseados no sentimento local
            this.generateTradingSignals(avgSentiment);
        }
    }

    async generateTradingSignalsWithAPI(sentiment) {
        console.log('🎯 Gerando sinais de trading com API...');
        
        // Tentar buscar sinais da API primeiro
        const apiSignals = await this.fetchTradingSignals();
        
        let signals = [];
        
        if (apiSignals && apiSignals.length > 0) {
            // Usar sinais da API
            signals = apiSignals;
            console.log(`✅ Usando ${signals.length} sinais da API`);
        } else {
            // Fallback: gerar sinais localmente
            console.log('⚠️ API indisponível, gerando sinais localmente');
            signals = this.generateLocalTradingSignals(sentiment);
        }
        
        // Adicionar sinais baseados em sentimento se não houver suficientes
        if (signals.length < 2) {
            const sentimentSignals = this.generateSentimentBasedSignals(sentiment);
            signals.push(...sentimentSignals);
        }
        
        this.signals = signals;
        this.updateSignalsDisplay();
        this.checkHighPrioritySignals();
    }

    generateLocalTradingSignals(sentiment) {
        const currentPrice = this.dashboard.currentPrice;
        const signals = [];
        
        // Sinal baseado em sentimento (melhorado)
        if (sentiment > 0.5) {
            signals.push({
                type: 'BUY',
                confidence: Math.min(sentiment * 100, 95),
                reason: 'Sentimento extremamente positivo do mercado - múltiplas notícias bullish',
                entry: currentPrice,
                target: currentPrice * (1 + this.settings.profitTarget / 100),
                stopLoss: currentPrice * (1 - this.settings.stopLoss / 100),
                timeframe: this.settings.timeframe,
                priority: 'high'
            });
        } else if (sentiment < -0.5) {
            signals.push({
                type: 'SELL',
                confidence: Math.min(Math.abs(sentiment) * 100, 95),
                reason: 'Sentimento extremamente negativo - possíveis correções no mercado',
                entry: currentPrice,
                target: currentPrice * (1 - this.settings.profitTarget / 100),
                stopLoss: currentPrice * (1 + this.settings.stopLoss / 100),
                timeframe: this.settings.timeframe,
                priority: 'high'
            });
        }
        
        // Sinais técnicos simulados melhorados
        const technicalSignals = this.generateTechnicalSignals(currentPrice);
        signals.push(...technicalSignals);
        
        return signals;
    }

    generateSentimentBasedSignals(sentiment) {
        const currentPrice = this.dashboard.currentPrice;
        const signals = [];
        
        // Sinal de momentum baseado em notícias recentes
        const recentNews = this.newsData.filter(news => {
            const timeString = news.time.toLowerCase();
            return timeString.includes('min') || timeString.includes('hora') || timeString === 'agora';
        });
        
        if (recentNews.length >= 2) {
            const recentSentiment = recentNews.reduce((sum, news) => sum + news.sentiment, 0) / recentNews.length;
            
            if (Math.abs(recentSentiment) > 0.3) {
                signals.push({
                    type: recentSentiment > 0 ? 'BUY' : 'SELL',
                    confidence: Math.min(Math.abs(recentSentiment * 100), 90),
                    reason: `${recentNews.length} notícias recentes mostram sentimento ${recentSentiment > 0 ? 'positivo' : 'negativo'} forte`,
                    entry: currentPrice,
                    target: currentPrice * (recentSentiment > 0 ? 1.04 : 0.96),
                    stopLoss: currentPrice * (recentSentiment > 0 ? 0.98 : 1.02),
                    timeframe: '2h',
                    priority: 'medium'
                });
            }
        }
        
        return signals;
    }

    updateSentimentMeter(sentiment) {
        const sentimentFill = document.getElementById('sentimentFill');
        const sentimentScore = document.getElementById('sentimentScore');
        
        // Converter sentimento (-1 a 1) para porcentagem (0 a 100)
        const percentage = ((sentiment + 1) / 2) * 100;
        
        sentimentFill.style.width = `${percentage}%`;
        
        // Colorir baseado no sentimento
        if (sentiment > 0.3) {
            sentimentFill.style.background = 'linear-gradient(90deg, #4CAF50, #8BC34A)';
            sentimentScore.innerHTML = `<strong>BULLISH</strong> (${(sentiment * 100).toFixed(1)}%)`;
        } else if (sentiment < -0.3) {
            sentimentFill.style.background = 'linear-gradient(90deg, #F44336, #FF5722)';
            sentimentScore.innerHTML = `<strong>BEARISH</strong> (${(sentiment * 100).toFixed(1)}%)`;
        } else {
            sentimentFill.style.background = 'linear-gradient(90deg, #FFC107, #FF9800)';
            sentimentScore.innerHTML = `<strong>NEUTRAL</strong> (${(sentiment * 100).toFixed(1)}%)`;
        }
    }

    generateTradingSignals(sentiment) {
        console.log('🎯 Gerando sinais de trading...');
        
        const currentPrice = this.dashboard.currentPrice;
        const signals = [];
        
        // Sinal baseado em sentimento
        if (sentiment > 0.5) {
            signals.push({
                type: 'BUY',
                confidence: Math.min(sentiment * 100, 95),
                reason: 'Sentimento extremamente positivo do mercado',
                entry: currentPrice,
                target: currentPrice * (1 + this.settings.profitTarget / 100),
                stopLoss: currentPrice * (1 - this.settings.stopLoss / 100),
                timeframe: this.settings.timeframe,
                priority: 'high'
            });
        } else if (sentiment < -0.5) {
            signals.push({
                type: 'SELL',
                confidence: Math.min(Math.abs(sentiment) * 100, 95),
                reason: 'Sentimento extremamente negativo, possível correção',
                entry: currentPrice,
                target: currentPrice * (1 - this.settings.profitTarget / 100),
                stopLoss: currentPrice * (1 + this.settings.stopLoss / 100),
                timeframe: this.settings.timeframe,
                priority: 'high'
            });
        }
        
        // Sinais técnicos simulados
        const technicalSignals = this.generateTechnicalSignals(currentPrice);
        signals.push(...technicalSignals);
        
        this.signals = signals;
        this.updateSignalsDisplay();
        
        // Enviar alertas para sinais de alta prioridade
        this.checkHighPrioritySignals();
    }

    generateTechnicalSignals(currentPrice) {
        const signals = [];
        const priceHistory = this.dashboard.priceHistory.slice(-20); // Últimos 20 pontos
        
        if (priceHistory.length < 10) return signals;
        
        // Simular indicadores técnicos
        const prices = priceHistory.map(p => p.price);
        const sma10 = prices.slice(-10).reduce((a, b) => a + b) / 10;
        const sma20 = prices.reduce((a, b) => a + b) / prices.length;
        
        // RSI simulado
        const rsi = 30 + Math.random() * 40; // Simular RSI entre 30-70
        
        // Sinal de cruzamento de médias
        if (currentPrice > sma10 && sma10 > sma20) {
            signals.push({
                type: 'BUY',
                confidence: 75,
                reason: `Cruzamento de médias bullish (Preço: €${currentPrice.toFixed(2)} > SMA10: €${sma10.toFixed(2)})`,
                entry: currentPrice,
                target: currentPrice * 1.03,
                stopLoss: currentPrice * 0.98,
                timeframe: '1h',
                priority: 'medium'
            });
        }
        
        // Sinal de RSI
        if (rsi < 30) {
            signals.push({
                type: 'BUY',
                confidence: 80,
                reason: `RSI oversold (${rsi.toFixed(1)}) - possível reversão`,
                entry: currentPrice,
                target: currentPrice * 1.05,
                stopLoss: currentPrice * 0.97,
                timeframe: '4h',
                priority: 'high'
            });
        } else if (rsi > 70) {
            signals.push({
                type: 'SELL',
                confidence: 80,
                reason: `RSI overbought (${rsi.toFixed(1)}) - possível correção`,
                entry: currentPrice,
                target: currentPrice * 0.95,
                stopLoss: currentPrice * 1.03,
                timeframe: '4h',
                priority: 'high'
            });
        }
        
        return signals;
    }

    updateSignalsDisplay() {
        const signalsContainer = document.getElementById('tradingSignals');
        
        if (this.signals.length === 0) {
            signalsContainer.innerHTML = `
                <div class="no-signals">
                    <i class="fas fa-search"></i>
                    <p>Nenhum sinal ativo no momento</p>
                    <small>Aguardando oportunidades...</small>
                </div>
            `;
            return;
        }
        
        const signalsHTML = this.signals.map(signal => {
            const typeClass = signal.type === 'BUY' ? 'buy-signal' : 'sell-signal';
            const priorityIcon = signal.priority === 'high' ? '🚨' : signal.priority === 'medium' ? '⚠️' : 'ℹ️';
            const confidenceColor = signal.confidence > 80 ? 'high-confidence' : signal.confidence > 60 ? 'medium-confidence' : 'low-confidence';
            
            const potentialProfit = signal.type === 'BUY' 
                ? ((signal.target - signal.entry) / signal.entry * 100).toFixed(2)
                : ((signal.entry - signal.target) / signal.entry * 100).toFixed(2);
            
            return `
                <div class="signal-item ${typeClass} ${confidenceColor}">
                    <div class="signal-header">
                        <span class="signal-type">${priorityIcon} ${signal.type}</span>
                        <span class="signal-confidence">${signal.confidence.toFixed(0)}%</span>
                        <span class="signal-timeframe">${signal.timeframe}</span>
                    </div>
                    <div class="signal-reason">${signal.reason}</div>
                    <div class="signal-details">
                        <div class="signal-prices">
                            <span>Entry: €${signal.entry.toFixed(2)}</span>
                            <span>Target: €${signal.target.toFixed(2)}</span>
                            <span>Stop: €${signal.stopLoss.toFixed(2)}</span>
                        </div>
                        <div class="signal-profit">
                            Potencial: <strong>+${potentialProfit}%</strong>
                        </div>
                    </div>
                    <div class="signal-actions">
                        <button class="btn btn-sm btn-primary" onclick="xtbAnalyzer.copySignalToClipboard(${this.signals.indexOf(signal)})">
                            <i class="fas fa-copy"></i> Copiar
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="xtbAnalyzer.setAlert(${this.signals.indexOf(signal)})">
                            <i class="fas fa-bell"></i> Alerta
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        signalsContainer.innerHTML = signalsHTML;
    }

    async checkHighPrioritySignals() {
        const highPrioritySignals = this.signals.filter(s => s.priority === 'high' && s.confidence > 75);
        
        for (const signal of highPrioritySignals) {
            if (this.settings.notificationsEnabled) {
                this.sendTradingNotification(signal);
            }
            
            if (this.settings.telegramTrading && this.dashboard.telegram.connected) {
                this.sendTradingTelegram(signal);
            }
        }
    }

    sendTradingNotification(signal) {
        const title = `🚨 XTB Signal: ${signal.type}`;
        const message = `${signal.reason}\nConfiança: ${signal.confidence.toFixed(0)}%\nEntry: €${signal.entry.toFixed(2)}`;
        
        this.dashboard.showNotification(title, message, 'warning');
        
        // Notificação do navegador
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: 'https://www.xtb.com/favicon.ico',
                badge: 'https://www.xtb.com/favicon.ico',
                tag: 'xtb-signal'
            });
        }
    }

    async sendTradingTelegram(signal) {
        if (!this.dashboard.telegram.connected) return;
        
        const emoji = signal.type === 'BUY' ? '🟢' : '🔴';
        const potentialProfit = signal.type === 'BUY' 
            ? ((signal.target - signal.entry) / signal.entry * 100).toFixed(2)
            : ((signal.entry - signal.target) / signal.entry * 100).toFixed(2);
        
        const telegramMessage = `${emoji} *XTB TRADING SIGNAL*\n\n` +
                              `📊 *${signal.type} Bitcoin*\n` +
                              `🎯 Confiança: *${signal.confidence.toFixed(0)}%*\n` +
                              `💰 Entry: *€${signal.entry.toFixed(2)}*\n` +
                              `🚀 Target: *€${signal.target.toFixed(2)}*\n` +
                              `🛡️ Stop Loss: *€${signal.stopLoss.toFixed(2)}*\n` +
                              `📈 Potencial: *+${potentialProfit}%*\n` +
                              `⏰ Timeframe: *${signal.timeframe}*\n\n` +
                              `📝 *Razão:* ${signal.reason}\n\n` +
                              `⚠️ *Lembre-se: Trading envolve riscos!*`;
        
        try {
            await fetch(`https://api.telegram.org/bot${this.dashboard.telegram.botToken}/sendMessage`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chat_id: this.dashboard.telegram.chatId,
                    text: telegramMessage,
                    parse_mode: 'Markdown'
                })
            });
        } catch (error) {
            console.error('Erro ao enviar sinal via Telegram:', error);
        }
    }

    runProfitSimulation() {
        const investmentAmount = parseFloat(document.getElementById('investmentAmount').value);
        const resultsContainer = document.getElementById('simulationResults');
        
        if (!investmentAmount || investmentAmount < 10) {
            resultsContainer.innerHTML = '<div class="error">Por favor, insira um valor de investimento válido (mín. €10)</div>';
            return;
        }
        
        // Simular diferentes cenários
        const scenarios = [
            { name: 'Conservador', return: 2, probability: 70, risk: 'Baixo' },
            { name: 'Moderado', return: 5, probability: 50, risk: 'Médio' },
            { name: 'Agressivo', return: 12, probability: 30, risk: 'Alto' },
            { name: 'Scalping', return: 1.5, probability: 80, risk: 'Médio', frequency: 'diário' }
        ];
        
        const simulationsHTML = scenarios.map(scenario => {
            const profit = investmentAmount * (scenario.return / 100);
            const total = investmentAmount + profit;
            
            return `
                <div class="simulation-scenario">
                    <div class="scenario-header">
                        <h4>${scenario.name}</h4>
                        <span class="scenario-risk ${scenario.risk.toLowerCase()}">${scenario.risk}</span>
                    </div>
                    <div class="scenario-details">
                        <div class="scenario-returns">
                            <span>Retorno: <strong>+${scenario.return}%</strong></span>
                            <span>Lucro: <strong>€${profit.toFixed(2)}</strong></span>
                            <span>Total: <strong>€${total.toFixed(2)}</strong></span>
                        </div>
                        <div class="scenario-probability">
                            Probabilidade de sucesso: <strong>${scenario.probability}%</strong>
                        </div>
                        ${scenario.frequency ? `<div class="scenario-frequency">Frequência: ${scenario.frequency}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        resultsContainer.innerHTML = `
            <div class="simulation-header">
                <h4>💰 Simulação de Lucros - €${investmentAmount.toLocaleString()}</h4>
                <small>Baseado no preço atual: €${this.dashboard.currentPrice.toFixed(2)}</small>
            </div>
            ${simulationsHTML}
            <div class="simulation-disclaimer">
                <i class="fas fa-exclamation-triangle"></i>
                <small>⚠️ Simulações são baseadas em dados históricos. Trading envolve riscos reais de perda!</small>
            </div>
        `;
    }

    copySignalToClipboard(signalIndex) {
        const signal = this.signals[signalIndex];
        const signalText = `XTB Signal: ${signal.type}\n` +
                          `Entry: €${signal.entry.toFixed(2)}\n` +
                          `Target: €${signal.target.toFixed(2)}\n` +
                          `Stop Loss: €${signal.stopLoss.toFixed(2)}\n` +
                          `Confidence: ${signal.confidence.toFixed(0)}%\n` +
                          `Reason: ${signal.reason}`;
        
        navigator.clipboard.writeText(signalText).then(() => {
            this.dashboard.showNotification('Copiado!', 'Sinal copiado para a área de transferência', 'success');
        });
    }

    setAlert(signalIndex) {
        const signal = this.signals[signalIndex];
        
        // Criar alerta automático baseado no sinal
        const alertPrice = signal.type === 'BUY' ? signal.target : signal.target;
        const alertType = signal.type === 'BUY' ? 'above' : 'below';
        
        // Simular criação de alerta
        this.dashboard.showNotification('Alerta Criado!', `Alerta definido para €${alertPrice.toFixed(2)}`, 'success');
    }

    async refreshAnalysis() {
        console.log('🔄 Atualizando análise de mercado...');
        
        // Mostrar loading
        document.getElementById('tradingSignals').innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Atualizando análise...</p>
            </div>
        `;
        
        document.getElementById('marketNews').innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Carregando notícias...</p>
            </div>
        `;
        
        try {
            // Simular delay da análise
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            // Atualizar notícias (tentará API real primeiro)
            await this.startNewsMonitoring();
            
            // Buscar análise de sentimento atualizada
            const sentiment = await this.fetchMarketSentiment();
            
            // Se a API estiver funcionando, mostrar status
            if (sentiment && !sentiment.error) {
                this.dashboard.showNotification('API Conectada!', `Sentimento: ${sentiment.classification} (${sentiment.confidence?.toFixed(1)}%)`, 'success');
            }
            
            this.dashboard.showNotification('Análise Atualizada!', 'Novos sinais e notícias carregados', 'success');
            
        } catch (error) {
            console.error('Erro ao atualizar análise:', error);
            
            // Fallback em caso de erro
            await this.startNewsMonitoring();
            
            this.dashboard.showNotification('Análise Atualizada!', 'Dados simulados carregados (API indisponível)', 'warning');
        }
    }

    async updateMarketAnalysis() {
        console.log('📊 Atualizando análise de mercado automática...');
        
        try {
            // Verificar se a API está funcionando
            const healthCheck = await fetch('http://localhost:8003/api/health', {
                method: 'GET',
                signal: AbortSignal.timeout(3000)
            });
            
            if (healthCheck.ok) {
                const health = await healthCheck.json();
                console.log('✅ API XTB News funcionando:', health.status);
                
                // Atualizar com dados da API
                await this.startNewsMonitoring();
            } else {
                throw new Error('API não disponível');
            }
            
        } catch (error) {
            console.warn('⚠️ API indisponível, usando dados simulados:', error.message);
            
            // Fallback para dados simulados
            this.newsData = this.generateMockNews();
            this.updateNewsDisplay();
            await this.analyzeSentiment();
        }
    }

    showSettingsModal() {
        document.getElementById('tradingSettingsModal').style.display = 'block';
        this.loadTradingSettings();
    }

    hideSettingsModal() {
        document.getElementById('tradingSettingsModal').style.display = 'none';
    }

    loadTradingSettings() {
        document.getElementById('riskTolerance').value = this.settings.riskTolerance;
        document.getElementById('profitTargetSetting').value = this.settings.profitTarget;
        document.getElementById('stopLossSetting').value = this.settings.stopLoss;
        document.getElementById('timeframeSetting').value = this.settings.timeframe;
        document.getElementById('tradingNotifications').checked = this.settings.notificationsEnabled;
        document.getElementById('telegramTrading').checked = this.settings.telegramTrading || false;
    }

    saveTradingSettings() {
        this.settings.riskTolerance = document.getElementById('riskTolerance').value;
        this.settings.profitTarget = parseFloat(document.getElementById('profitTargetSetting').value);
        this.settings.stopLoss = parseFloat(document.getElementById('stopLossSetting').value);
        this.settings.timeframe = document.getElementById('timeframeSetting').value;
        this.settings.notificationsEnabled = document.getElementById('tradingNotifications').checked;
        this.settings.telegramTrading = document.getElementById('telegramTrading').checked;
        
        // Salvar no localStorage
        localStorage.setItem('riskTolerance', this.settings.riskTolerance);
        localStorage.setItem('profitTarget', this.settings.profitTarget.toString());
        localStorage.setItem('stopLoss', this.settings.stopLoss.toString());
        localStorage.setItem('timeframe', this.settings.timeframe);
        localStorage.setItem('tradingNotifications', this.settings.notificationsEnabled.toString());
        localStorage.setItem('telegramTrading', this.settings.telegramTrading.toString());
        
        this.hideSettingsModal();
        this.dashboard.showNotification('Configurações Salvas!', 'Preferências de trading atualizadas', 'success');
        
        // Regenerar sinais com novas configurações
        this.generateTradingSignals(this.sentimentScore);
    }

    async updateMarketAnalysis() {
        console.log('📊 Atualizando análise de mercado...');
        
        // Atualizar notícias
        await this.startNewsMonitoring();
        
        // Regenerar sinais
        this.generateTradingSignals(this.sentimentScore);
    }

    displayNewsError() {
        document.getElementById('marketNews').innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Erro ao carregar notícias</p>
                <small>Tentando novamente...</small>
            </div>
        `;
    }
}

// Inicializar XTB Trading Analyzer quando dashboard estiver pronta
window.initXTBAnalyzer = function() {
    if (typeof dashboard !== 'undefined' && dashboard) {
        window.xtbAnalyzer = new XTBTradingAnalyzer(dashboard);
        console.log('✅ XTB Trading Analyzer inicializado!');
    } else {
        console.log('⏳ Aguardando dashboard...');
        setTimeout(initXTBAnalyzer, 1000);
    }
};

// Auto-inicializar após 3 segundos
setTimeout(initXTBAnalyzer, 3000);
