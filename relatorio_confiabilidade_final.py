#!/usr/bin/env python3
"""
Relatório Consolidado de Confiabilidade dos Sinais Bitcoin
Combina todos os testes para uma avaliação final
"""

import json
from datetime import datetime

def create_consolidated_report():
    """Criar relatório consolidado de confiabilidade"""
    
    print("📊 RELATÓRIO CONSOLIDADO DE CONFIABILIDADE")
    print("=" * 60)
    print("🕒 Data do Relatório:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("=" * 60)
    
    # RESULTADOS DOS TESTES
    print("\n🧪 RESULTADOS DOS TESTES REALIZADOS")
    print("-" * 60)
    
    # Teste 1: Confiabilidade Geral
    print("\n1️⃣ TESTE DE CONFIABILIDADE GERAL")
    print("   📋 Método: Análise de 10 sinais coletados em intervalos de 3s")
    print("   🎯 Score: 73/100 (73%)")
    print("   🏷️  Classificação: 🟡 CONFIABILIDADE MÉDIA")
    print("   📊 Detalhes:")
    print("      • Distribuição Sinais: HOLD 50%, SELL 30%, BUY 20%")
    print("      • Score médio: 50 (range: 40-70)")
    print("      • Desvio padrão: 9.4 (baixa variação)")
    print("      • Confiança: 90% MEDIUM, 10% HIGH")
    print("      • RSI médio: 49.6 (range: 27.4-77.8)")
    print("      • Risk/Reward médio: 1.83:1")
    
    # Teste 2: Validação Técnica
    print("\n2️⃣ TESTE DE VALIDAÇÃO TÉCNICA")
    print("   📋 Método: Análise da coerência dos indicadores técnicos")
    print("   🎯 Score: 54.3/100 (54%)")
    print("   🏷️  Classificação: 🟠 QUALIDADE MÉDIA")
    print("   📊 Detalhes:")
    print("      • RSI Coerência: 100% (5/5 sinais corretos)")
    print("      • Lógica Sinais: 60% (3/5 coerentes)")
    print("      • Alvos Válidos: 100% (5/5 válidos)")
    print("      • Trend dominante: SIDEWAYS (mercado lateral)")
    print("      • SL Distance: 3-5% (adequado)")
    print("      • TP Distance: 5-10% (adequado)")
    
    # ANÁLISE CONSOLIDADA
    print("\n📈 ANÁLISE CONSOLIDADA")
    print("-" * 60)
    
    # Pontos Fortes
    print("\n✅ PONTOS FORTES:")
    print("   🎯 Alvos de preço (SL/TP) bem calculados (100% válidos)")
    print("   📊 RSI tecnicamente correto (100% coerência)")
    print("   🔄 API estável e responsiva (100% disponibilidade)")
    print("   ⚖️  Risk/Reward ratio adequado (1.67-2.00:1)")
    print("   📉 Baixa variação nos scores (desvio padrão 9.4)")
    print("   🛡️  Gestão de risco conservadora")
    
    # Pontos Fracos
    print("\n❌ PONTOS FRACOS:")
    print("   🧠 Lógica dos sinais às vezes inconsistente (60% coerência)")
    print("   📊 Baixa confiança geral (90% MEDIUM, apenas 10% HIGH)")
    print("   🔄 Tendência a sinais HOLD excessivos (50% dos casos)")
    print("   📈 Dificuldade em identificar momentos de compra/venda")
    print("   ⚠️  Alguns sinais SELL com RSI baixo (ilógico)")
    
    # AVALIAÇÃO FINAL
    print("\n🏆 AVALIAÇÃO FINAL")
    print("=" * 60)
    
    # Calcular score consolidado
    reliability_score = 73
    technical_score = 54.3
    consolidated_score = (reliability_score * 0.6) + (technical_score * 0.4)
    
    print(f"🎯 SCORE CONSOLIDADO: {consolidated_score:.1f}/100")
    print(f"   • Confiabilidade Geral: {reliability_score}/100 (peso 60%)")
    print(f"   • Qualidade Técnica: {technical_score:.1f}/100 (peso 40%)")
    
    # Classificação final
    if consolidated_score >= 70:
        final_class = "🟢 ALTA CONFIABILIDADE"
        risk_level = "BAIXO"
        recommendation = "Adequado para trading real com gestão de risco"
        max_capital = "Até 5% do capital total"
    elif consolidated_score >= 55:
        final_class = "🟡 CONFIABILIDADE MÉDIA"
        risk_level = "MÉDIO"
        recommendation = "Adequado para testes com capital pequeno"
        max_capital = "Até 2% do capital total"
    elif consolidated_score >= 40:
        final_class = "🟠 CONFIABILIDADE BAIXA"
        risk_level = "ALTO"
        recommendation = "Apenas para estudos e paper trading"
        max_capital = "Sem capital real"
    else:
        final_class = "🔴 CONFIABILIDADE MUITO BAIXA"
        risk_level = "MUITO ALTO"
        recommendation = "Não recomendado"
        max_capital = "Sem capital real"
    
    print(f"\n🏷️  CLASSIFICAÇÃO: {final_class}")
    print(f"⚠️  NÍVEL DE RISCO: {risk_level}")
    print(f"💡 RECOMENDAÇÃO: {recommendation}")
    print(f"💰 CAPITAL MÁXIMO: {max_capital}")
    
    # RECOMENDAÇÕES ESPECÍFICAS
    print("\n💡 RECOMENDAÇÕES ESPECÍFICAS")
    print("-" * 60)
    
    print("\n🔧 MELHORIAS SUGERIDAS:")
    print("   1. Ajustar lógica dos sinais SELL (verificar RSI)")
    print("   2. Reduzir tendência excessiva para HOLD")
    print("   3. Implementar níveis de confiança mais diversos")
    print("   4. Adicionar filtros de volume para confirmação")
    print("   5. Integrar análise de múltiplos timeframes")
    
    print("\n📋 USO RECOMENDADO:")
    print("   ✅ Confirmar sinais com análise manual")
    print("   ✅ Usar stop loss SEMPRE")
    print("   ✅ Limitar posição a 1-2% do capital")
    print("   ✅ Testar em paper trading primeiro")
    print("   ✅ Monitorar performance constantemente")
    
    print("\n⚠️  CUIDADOS IMPORTANTES:")
    print("   ❌ Nunca seguir sinais cegamente")
    print("   ❌ Não aumentar posições em sinais consecutivos")
    print("   ❌ Evitar trading em momentos de alta volatilidade")
    print("   ❌ Não usar em mercados de forte tendência")
    print("   ❌ Nunca investir mais do que pode perder")
    
    # CONCLUSÃO
    print("\n🎊 CONCLUSÃO")
    print("=" * 60)
    
    reliability_text = ""
    if consolidated_score >= 65:
        reliability_text = "O sistema apresenta confiabilidade adequada para uso cauteloso"
    elif consolidated_score >= 50:
        reliability_text = "O sistema tem potencial mas requer melhorias"
    else:
        reliability_text = "O sistema precisa de ajustes significativos"
    
    print(f"📊 {reliability_text}.")
    print(f"🎯 Score final de {consolidated_score:.1f}/100 indica {final_class.lower()}.")
    
    if consolidated_score >= 55:
        print("✅ APROVADO para testes com capital limitado e gestão rigorosa de risco.")
    else:
        print("❌ NÃO APROVADO para uso com capital real no momento.")
    
    print(f"\n💼 Para uso profissional, recomenda-se score mínimo de 75/100.")
    print(f"🔬 Para estudos acadêmicos, o sistema atual é adequado.")
    print(f"📈 Para paper trading, pode ser usado sem restrições.")
    
    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"relatorio_confiabilidade_final_{timestamp}.txt"
    
    try:
        # Capturar todo o output em um arquivo
        report_content = f"""RELATÓRIO CONSOLIDADO DE CONFIABILIDADE DOS SINAIS BITCOIN
Data: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

RESULTADOS DOS TESTES:
1. Confiabilidade Geral: 73/100 (MÉDIA)
2. Qualidade Técnica: 54.3/100 (MÉDIA)

SCORE CONSOLIDADO: {consolidated_score:.1f}/100
CLASSIFICAÇÃO: {final_class}
NÍVEL DE RISCO: {risk_level}
RECOMENDAÇÃO: {recommendation}
CAPITAL MÁXIMO: {max_capital}

PONTOS FORTES:
- Alvos de preço bem calculados (100% válidos)
- RSI tecnicamente correto (100% coerência)
- API estável e responsiva
- Risk/Reward ratio adequado
- Gestão de risco conservadora

PONTOS FRACOS:
- Lógica dos sinais inconsistente (60% coerência)
- Baixa confiança geral (90% MEDIUM)
- Tendência excessiva para HOLD
- Sinais SELL às vezes ilógicos

CONCLUSÃO:
{reliability_text}. Score de {consolidated_score:.1f}/100 indica {final_class.lower()}.
{'APROVADO' if consolidated_score >= 55 else 'NÃO APROVADO'} para testes com capital limitado.
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n💾 Relatório salvo em: {filename}")
        
    except Exception as e:
        print(f"\n❌ Erro ao salvar relatório: {e}")
    
    return consolidated_score, final_class, recommendation

if __name__ == "__main__":
    try:
        score, classification, recommendation = create_consolidated_report()
        
        print(f"\n" + "="*60)
        print(f"🎯 VEREDICTO FINAL: {score:.1f}/100")
        print(f"🏷️  {classification}")
        print(f"💡 {recommendation}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
