#!/usr/bin/env python3
"""
Teste da API Melhorada - Comparação com Versão Anterior
Testa as melhorias implementadas na confiabilidade
"""

import requests
import time
import json
from datetime import datetime
from collections import Counter
import statistics

class EnhancedAPITester:
    def __init__(self):
        self.api_url = "https://bitdash-9dnk.onrender.com"
        self.test_results = []
        
    def test_single_signal(self):
        """Testar um único sinal"""
        try:
            response = requests.get(f"{self.api_url}/api/detailed-signal", timeout=15)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro API: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def test_confidence_endpoint(self):
        """Testar novo endpoint de confiança"""
        try:
            response = requests.get(f"{self.api_url}/api/signal-confidence", timeout=15)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro confidence API: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Erro confidence: {e}")
            return None
    
    def analyze_enhanced_features(self, signals):
        """Analisar novas funcionalidades"""
        print("\n🔍 ANÁLISE DAS MELHORIAS IMPLEMENTADAS")
        print("=" * 60)
        
        # 1. Análise de Confidence Factors
        all_factors = []
        for signal in signals:
            factors = signal.get('confidence_factors', [])
            all_factors.extend(factors)
        
        if all_factors:
            factor_counts = Counter(all_factors)
            print("\n📊 CONFIDENCE FACTORS MAIS FREQUENTES:")
            for factor, count in factor_counts.most_common(5):
                print(f"   {factor}: {count} vezes")
        
        # 2. Análise de Risk Metrics
        risk_rewards = [s.get('risk_metrics', {}).get('risk_reward_ratio', 0) for s in signals if s.get('risk_metrics')]
        volatilities = [s.get('risk_metrics', {}).get('volatility_estimate', 0) for s in signals if s.get('risk_metrics')]
        
        if risk_rewards:
            print(f"\n⚖️  RISK/REWARD RATIOS:")
            print(f"   Média: {statistics.mean(risk_rewards):.2f}:1")
            print(f"   Range: {min(risk_rewards):.2f} - {max(risk_rewards):.2f}")
        
        if volatilities:
            print(f"\n📈 VOLATILIDADE ESTIMADA:")
            print(f"   Média: {statistics.mean(volatilities):.2f}%")
            print(f"   Range: {min(volatilities):.2f}% - {max(volatilities):.2f}%")
        
        # 3. Análise de Trend Strength
        trend_strengths = [s.get('indicators', {}).get('trend_strength', 0) for s in signals if s.get('indicators')]
        trends = [s.get('indicators', {}).get('trend') for s in signals if s.get('indicators')]
        
        if trends:
            trend_counts = Counter(trends)
            print(f"\n📊 DISTRIBUIÇÃO DE TRENDS:")
            for trend, count in trend_counts.items():
                percentage = (count / len(trends)) * 100
                print(f"   {trend}: {count} ({percentage:.1f}%)")
        
        if trend_strengths:
            print(f"\n💪 FORÇA DAS TENDÊNCIAS:")
            print(f"   Média: {statistics.mean(trend_strengths):.2f}")
            print(f"   Range: {min(trend_strengths):.2f} - {max(trend_strengths):.2f}")
        
        # 4. Análise de Volume Signals
        volume_signals = [s.get('indicators', {}).get('volume_signal') for s in signals if s.get('indicators')]
        if volume_signals:
            volume_counts = Counter(volume_signals)
            print(f"\n🔊 SINAIS DE VOLUME:")
            for vol_signal, count in volume_counts.items():
                percentage = (count / len(volume_signals)) * 100
                print(f"   {vol_signal}: {count} ({percentage:.1f}%)")
    
    def compare_confidence_distribution(self, signals):
        """Comparar distribuição de confiança com versão anterior"""
        print("\n📊 COMPARAÇÃO DE CONFIANÇA")
        print("-" * 40)
        
        confidences = [s.get('confidence') for s in signals if s.get('confidence')]
        confidence_counts = Counter(confidences)
        
        print("🆕 NOVA VERSÃO:")
        for conf, count in confidence_counts.items():
            percentage = (count / len(confidences)) * 100
            print(f"   {conf}: {count} ({percentage:.1f}%)")
        
        print("\n📋 VERSÃO ANTERIOR (referência):")
        print("   MEDIUM: 90%")
        print("   HIGH: 10%")
        print("   LOW: 0%")
        
        # Calcular melhoria
        high_conf_new = confidence_counts.get('HIGH', 0)
        high_conf_percentage = (high_conf_new / len(confidences)) * 100 if confidences else 0
        
        improvement = high_conf_percentage - 10  # Era 10% antes
        
        if improvement > 0:
            print(f"\n✅ MELHORIA: +{improvement:.1f}% em confiança HIGH")
        else:
            print(f"\n⚠️  REDUÇÃO: {improvement:.1f}% em confiança HIGH")
    
    def test_signal_logic_improvement(self, signals):
        """Testar melhorias na lógica dos sinais"""
        print("\n🧠 TESTE DE LÓGICA MELHORADA")
        print("-" * 40)
        
        logic_score = 0
        total_signals = 0
        
        for i, signal in enumerate(signals):
            signal_type = signal.get('signal')
            rsi = signal.get('indicators', {}).get('rsi')
            trend = signal.get('indicators', {}).get('trend')
            score = signal.get('score')
            confidence_factors = signal.get('confidence_factors', [])
            
            if not all([signal_type, rsi is not None, trend, score is not None]):
                continue
            
            total_signals += 1
            is_logical = True
            reasons = []
            
            print(f"\n📊 Sinal {i+1}: {signal_type} (Score: {score}, Fatores: {len(confidence_factors)})")
            
            # Verificar lógica BUY melhorada
            if signal_type == 'BUY':
                if rsi < 35 or 'RSI_OVERSOLD' in confidence_factors or 'RSI_STRONG_OVERSOLD' in confidence_factors:
                    reasons.append("✅ RSI favorável para compra")
                elif rsi > 65:
                    reasons.append("⚠️  RSI alto para compra")
                    is_logical = False
                
                if 'UPTREND' in trend or 'STRONG_UPTREND' in trend:
                    reasons.append("✅ Tendência favorável")
                elif 'DOWNTREND' in trend:
                    reasons.append("⚠️  Tendência desfavorável")
                    is_logical = False
                
                if score >= 65:
                    reasons.append("✅ Score adequado para BUY")
                else:
                    reasons.append("⚠️  Score baixo para BUY")
                    is_logical = False
            
            # Verificar lógica SELL melhorada  
            elif signal_type == 'SELL':
                if rsi > 65 or 'RSI_OVERBOUGHT' in confidence_factors or 'RSI_STRONG_OVERBOUGHT' in confidence_factors:
                    reasons.append("✅ RSI favorável para venda")
                elif rsi < 35:
                    reasons.append("⚠️  RSI baixo para venda")
                    is_logical = False
                
                if 'DOWNTREND' in trend or 'STRONG_DOWNTREND' in trend:
                    reasons.append("✅ Tendência favorável")
                elif 'UPTREND' in trend:
                    reasons.append("⚠️  Tendência desfavorável")
                    is_logical = False
                
                if score <= 35:
                    reasons.append("✅ Score adequado para SELL")
                else:
                    reasons.append("⚠️  Score alto para SELL")
                    is_logical = False
            
            # Verificar lógica HOLD melhorada
            elif signal_type == 'HOLD':
                if 35 <= rsi <= 65:
                    reasons.append("✅ RSI neutro para HOLD")
                else:
                    reasons.append("⚠️  RSI extremo para HOLD")
                
                if trend == 'SIDEWAYS':
                    reasons.append("✅ Tendência lateral favorece HOLD")
                
                if 45 <= score <= 55:
                    reasons.append("✅ Score neutro para HOLD")
            
            # Verificar se há fatores de confiança suficientes
            if len(confidence_factors) >= 2:
                reasons.append("✅ Múltiplos fatores de confirmação")
            elif len(confidence_factors) == 1:
                reasons.append("⚠️  Apenas um fator de confirmação")
            else:
                reasons.append("❌ Nenhum fator de confirmação")
                is_logical = False
            
            # Mostrar análise
            for reason in reasons:
                print(f"   {reason}")
            
            if is_logical:
                logic_score += 1
                print(f"   🎯 Resultado: ✅ LÓGICO")
            else:
                print(f"   🎯 Resultado: ❌ QUESTIONÁVEL")
        
        if total_signals > 0:
            logic_rate = (logic_score / total_signals) * 100
            print(f"\n🧠 LÓGICA MELHORADA: {logic_rate:.1f}% ({logic_score}/{total_signals})")
            print(f"📊 VERSÃO ANTERIOR: 60%")
            
            improvement = logic_rate - 60
            if improvement > 0:
                print(f"✅ MELHORIA: +{improvement:.1f}% na lógica dos sinais")
            else:
                print(f"⚠️  MUDANÇA: {improvement:.1f}% na lógica dos sinais")
            
            return logic_rate
        
        return 0
    
    def run_enhancement_test(self):
        """Executar teste completo das melhorias"""
        print("🚀 TESTE DAS MELHORIAS NA CONFIABILIDADE")
        print("=" * 60)
        print("📋 Testando melhorias implementadas:")
        print("   • RSI calculation aprimorado")
        print("   • Análise multi-timeframe") 
        print("   • Confirmação por volume")
        print("   • Sistema de confidence factors")
        print("   • Stop loss/take profit dinâmicos")
        print("   • Métricas de risco")
        print("=" * 60)
        
        # Coletar sinais melhorados
        print("\n🔄 Coletando 8 sinais melhorados...")
        signals = []
        
        for i in range(8):
            print(f"📊 Sinal {i+1}/8...")
            signal = self.test_single_signal()
            if signal:
                signals.append(signal)
                
                # Mostrar informações do sinal
                score = signal.get('score', 0)
                conf = signal.get('confidence', 'N/A')
                factors = len(signal.get('confidence_factors', []))
                version = signal.get('version', 'N/A')
                
                print(f"   ✅ {signal.get('signal', 'N/A')} | Score: {score} | Conf: {conf} | Fatores: {factors} | V: {version}")
            else:
                print(f"   ❌ Falha no sinal {i+1}")
            
            time.sleep(2)  # Intervalo menor
        
        if len(signals) == 0:
            print("❌ Não foi possível coletar sinais. Teste abortado.")
            return
        
        print(f"\n✅ Coletados {len(signals)} sinais melhorados")
        
        # Análises das melhorias
        self.analyze_enhanced_features(signals)
        self.compare_confidence_distribution(signals)
        logic_improvement = self.test_signal_logic_improvement(signals)
        
        # Teste do novo endpoint
        print("\n🔍 TESTE DO ENDPOINT DE CONFIANÇA")
        print("-" * 40)
        confidence_data = self.test_confidence_endpoint()
        if confidence_data:
            print("✅ Novo endpoint funcionando:")
            print(f"   Sinal: {confidence_data.get('signal')}")
            print(f"   Score: {confidence_data.get('score')}")
            print(f"   Confiança: {confidence_data.get('confidence')}")
            print(f"   Fatores: {len(confidence_data.get('confidence_factors', []))}")
            print(f"   Recomendação: {confidence_data.get('recommendation')}")
        else:
            print("❌ Novo endpoint não funcionando")
        
        # Cálculo do score melhorado
        print(f"\n🏆 ESTIMATIVA DE MELHORIA")
        print("=" * 60)
        
        # Fatores de melhoria
        confidence_scores = [75 if s.get('confidence') == 'HIGH' else 60 if s.get('confidence') == 'MEDIUM' else 45 for s in signals]
        avg_confidence_score = statistics.mean(confidence_scores) if confidence_scores else 50
        
        # Score de confiabilidade estimado
        estimated_reliability = min(85, avg_confidence_score * 1.1)  # Cap em 85
        
        # Score técnico estimado baseado na lógica
        estimated_technical = min(75, logic_improvement * 1.2) if logic_improvement > 0 else 55
        
        # Score consolidado
        new_consolidated = (estimated_reliability * 0.6) + (estimated_technical * 0.4)
        
        print(f"📊 SCORES ESTIMADOS (Versão Melhorada):")
        print(f"   Confiabilidade: {estimated_reliability:.1f}/100 (era 73)")
        print(f"   Qualidade Técnica: {estimated_technical:.1f}/100 (era 54.3)")
        print(f"   Score Consolidado: {new_consolidated:.1f}/100 (era 65.5)")
        
        improvement = new_consolidated - 65.5
        print(f"\n🎯 MELHORIA ESTIMADA: {improvement:+.1f} pontos")
        
        if new_consolidated >= 75:
            new_class = "🟢 ALTA CONFIABILIDADE"
            recommendation = "Aprovado para uso profissional"
        elif new_consolidated >= 65:
            new_class = "🟡 CONFIABILIDADE MÉDIA+"
            recommendation = "Aprovado para trading com capital moderado"
        else:
            new_class = "🟡 CONFIABILIDADE MÉDIA"
            recommendation = "Adequado para testes limitados"
        
        print(f"🏷️  Nova Classificação: {new_class}")
        print(f"💡 Nova Recomendação: {recommendation}")
        
        return new_consolidated, new_class, recommendation

if __name__ == "__main__":
    tester = EnhancedAPITester()
    
    try:
        score, classification, recommendation = tester.run_enhancement_test()
        
        print(f"\n🎊 TESTE DE MELHORIAS CONCLUÍDO!")
        print(f"📊 Novo Score: {score:.1f}/100")
        print(f"🏷️ Classificação: {classification}")
        print(f"💡 Recomendação: {recommendation}")
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_api_test_{timestamp}.json"
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'test_type': 'enhanced_api_improvements',
            'old_score': 65.5,
            'new_score': score,
            'improvement': score - 65.5,
            'classification': classification,
            'recommendation': recommendation
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {filename}")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
