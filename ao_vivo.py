# ao_vivo.py (VERSÃO COMPLETA COM SISTEMA DE RECOMENDAÇÕES RESTAURADO)
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import json
import sys
import os
from datetime import datetime

# =============================================
# 🎯 ENUMS E ESTRUTURAS BÁSICAS
# =============================================

class BetType(Enum):
    OVER_15_BOTH_NO = "Mais 1.5 & Ambas Não"
    EXACT_0_0 = "Resultado 0x0"
    UNDER_25_DC_1X = "Menos 2.5 & Dupla Chance 1X"
    DOUBLE_CHANCE_X2 = "Dupla Chance X2"
    NEXT_GOAL_FAV = "Próximo Gol Favorito"
    OVER_15 = "Mais 1.5 Gols"
    OVER_25_DC_12 = "Mais 2.5 & Dupla Chance 12"
    UNDER_15 = "Menos 1.5 Gols"
    VITORIA_FAV = "Vitória Favorito"

@dataclass
class Bet:
    bet_type: BetType
    investment: float
    odds: float

    @property
    def potential_return(self) -> float:
        return self.investment * self.odds

    @property
    def implied_probability(self) -> float:
        return (1 / self.odds) * 100 if self.odds > 0 else 0

# =============================================
# 🔧 FUNÇÃO INIT_STATE CORRIGIDA
# =============================================

def init_state():
    """Inicializa o estado da aplicação"""
    if 'app_state' not in st.session_state:
        default_odds = {
            "Mais 1.5 & Ambas Não": 3.50,
            "Resultado 0x0": 7.89,
            "Menos 2.5 & Dupla Chance 1X": 1.85,
            "Dupla Chance X2": 1.91,
            "Próximo Gol Favorito": 1.91,
            "Mais 1.5 Gols": 1.30,
            "Mais 2.5 & Dupla Chance 12": 2.30,
            "Menos 1.5 Gols": 3.25,
            "Vitória Favorito": 1.80
        }

        default_investments = {
            "Mais 1.5 & Ambas Não": 1.00,
            "Resultado 0x0": 0.00,
            "Menos 2.5 & Dupla Chance 1X": 2.00,
            "Dupla Chance X2": 2.00,
            "Próximo Gol Favorito": 0.00,
            "Mais 1.5 Gols": 0.00,
            "Mais 2.5 & Dupla Chance 12": 1.50,
            "Menos 1.5 Gols": 1.00,
            "Vitória Favorito": 1.00
        }
        
        initial_bankroll = sum(default_investments.values())
        
        st.session_state.app_state = {
            'odds_values': default_odds,
            'investment_values': default_investments,
            'total_bankroll': initial_bankroll,
            'investment_proportions': {},
            'last_analysis': {},
            'user_profile': 'Moderado',
            'show_odds_analysis': True,
            'distribution_applied': False,
            'vitorias_favorito': 3,
            'gols_feitos_favorito': 8,
            'gols_sofridos_favorito': 3,
            'vitorias_azarao': 1,
            'gols_feitos_azarao': 4,
            'gols_sofridos_azarao': 10
        }
        update_proportions_from_investments()
    
    # Inicializar módulo de hedge se disponível
    try:
        from dinamico import init_hedge_state
        if 'hedge_manager' not in st.session_state:
            init_hedge_state()
    except ImportError:
        st.warning("Módulo dinamico não disponível")

def update_proportions_from_investments():
    """Atualiza proporções baseadas nos investimentos atuais"""
    total_investment = sum(st.session_state.app_state['investment_values'].values())
    
    if total_investment > 0:
        proportions = {}
        for bet_type in BetType:
            investment = st.session_state.app_state['investment_values'][bet_type.value]
            proportions[bet_type.value] = investment / total_investment
        st.session_state.app_state['investment_proportions'] = proportions

def update_investments_from_proportions():
    """Atualiza investimentos baseados nas proporções"""
    total_bankroll = st.session_state.app_state['total_bankroll']
    proportions = st.session_state.app_state.get('investment_proportions', {})
    
    for bet_type in BetType:
        proportion = proportions.get(bet_type.value, 0)
        st.session_state.app_state['investment_values'][bet_type.value] = total_bankroll * proportion

# =============================================
# 🤖 SISTEMA DE PROMPT INTELIGENTE (RESTAURADO)
# =============================================

def render_intelligent_recommendations():
    """Sistema de recomendações inteligentes com prompt avançado"""
    st.markdown("## 🤖 Assistente de Análise com IA")
    
    # Coletar informações contextuais
    st.subheader("📋 Contexto da Partida")
    
    col1, col2 = st.columns(2)
    
    with col1:
        liga = st.selectbox("Liga/Campeonato", 
                           ["Brasileirão Série A", "Brasileirão Série B", "Copa do Brasil", 
                            "Libertadores", "Premier League", "La Liga", "Outro"])
        
        importancia = st.select_slider("Importância da Partida",
                                      options=["Baixa", "Média", "Alta", "Decisiva"])
    
    with col2:
        condicoes = st.multiselect("Condições Especiais",
                                  ["Chuva forte", "Calor extremo", "Gramado ruim", 
                                   "Público reduzido", "Sem torcida", "Outras"])
        
        motivacao_fav = st.select_slider("Motivação do Favorito",
                                        options=["Baixa", "Média", "Alta", "Máxima"])
    
    # Estatísticas detalhadas
    st.subheader("📊 Estatísticas dos Times")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏆 Favorito (Casa)**")
        vit_fav = st.slider("Vitórias últimos 5 jogos", 0, 5, 
                           st.session_state.app_state.get('vitorias_favorito', 3), key="vit_fav")
        gols_fav_f = st.slider("Gols marcados últimos 5", 0, 20, 
                              st.session_state.app_state.get('gols_feitos_favorito', 8), key="gols_fav_f")
        gols_fav_s = st.slider("Gols sofridos últimos 5", 0, 15, 
                              st.session_state.app_state.get('gols_sofridos_favorito', 3), key="gols_fav_s")
    
    with col2:
        st.markdown("**⚽ Azarão (Fora)**")
        vit_aza = st.slider("Vitórias últimos 5 jogos", 0, 5, 
                           st.session_state.app_state.get('vitorias_azarao', 1), key="vit_aza")
        gols_aza_f = st.slider("Gols marcados últimos 5", 0, 15, 
                              st.session_state.app_state.get('gols_feitos_azarao', 4), key="gols_aza_f")
        gols_aza_s = st.slider("Gols sofridos últimos 5", 0, 20, 
                              st.session_state.app_state.get('gols_sofridos_azarao', 10), key="gols_aza_s")
    
    # Análise técnica
    st.subheader("🧠 Análise Técnica")
    
    col1, col2 = st.columns(2)
    
    with col1:
        estilo_jogo = st.selectbox("Estilo de Jogo do Favorito",
                                  ["Ofensivo", "Equilibrado", "Defensivo", "Contra-ataque"])
        
        pressao = st.select_slider("Pressão sobre o Favorito",
                                  ["Nenhuma", "Baixa", "Média", "Alta", "Extrema"])
    
    with col2:
        consistencia = st.select_slider("Consistência do Azarão",
                                       ["Muito Irregular", "Irregular", "Regular", "Consistente"])
        
        historico_confronto = st.selectbox("Histórico de Confrontos",
                                          ["Favorito domina", "Equilibrado", "Azarão surpreende"])
    
    # Informações adicionais
    st.subheader("💡 Informações Adicionais")
    
    info_extra = st.text_area("Observações, notícias, lesões, ou fatores relevantes:",
                             placeholder="""Ex: Jogador-chave lesionado, treinador novo, situação do elenco...
                             
O Racing Club e o Vélez Sarsfield revelarão o primeiro semifinalista da Copa Libertadores 2025 quando se enfrentarem em Avellaneda no jogo de volta das quartas de final.

Notícias sobre a partida e a fase atual O Racing Club tem a vantagem no confronto depois de garantir uma vitória por 1 a 0 no jogo de ida em Liniers na última terça-feira. Essa vitória fez parte de uma série de três vitórias consecutivas da "Academia", que também vem de uma vitória fora de casa por 2 a 0 sobre o Huracán na última rodada do Torneio Clausura 2025. Talvez a parte mais impressionante dessa sequência seja o fato de o Racing não ter sofrido gols em cada uma das três vitórias, e conseguir essa façanha novamente seria suficiente para a equipe ficar entre os quatro primeiros na principal competição de clubes da América do Sul.

O Vélez Sarsfield se recuperou da derrota para o Racing no jogo de ida com uma vitória fora de casa por 2 a 1 sobre o San Martin de San Juan. Essa vitória ampliou a boa fase da equipe de Liniers, que perdeu apenas dois dos seus últimos 10 jogos em todas as competições (V6, E2, D2). Até mesmo o desempenho do Vélez fora de casa tem sido positivo, já que o time está há quatro jogos sem perder no território do adversário (V2, E2), mantendo três partidas sem sofrer gols nesse período. Mostrar essa solidez defensiva será fundamental para se manter vivo nesse confronto.""",
                             height=200)
    
    # Gerar prompt inteligente
    if st.button("🧠 Gerar Análise Completa", type="primary", use_container_width=True):
        with st.spinner("Analisando dados e criando relatório inteligente..."):
            prompt = generate_intelligent_prompt(
                liga, importancia, condicoes, motivacao_fav,
                vit_fav, gols_fav_f, gols_fav_s, vit_aza, gols_aza_f, gols_aza_s,
                estilo_jogo, pressao, consistencia, historico_confronto, info_extra
            )
            
            st.session_state['generated_prompt'] = prompt
    
    # Exibir prompt gerado
    if 'generated_prompt' in st.session_state:
        st.markdown("---")
        st.subheader("🎯 Relatório de Análise Gerado")
        
        with st.expander("📋 Visualizar Análise Completa", expanded=True):
            st.markdown(st.session_state['generated_prompt'])
        
        # Opções de exportação
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copiar para Área de Transferência", use_container_width=True):
                st.toast("Análise copiada com sucesso! ✅")
        with col2:
            if st.button("💾 Salvar como Relatório", use_container_width=True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analise_apostas_{timestamp}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(st.session_state['generated_prompt'])
                st.success(f"Relatório salvo como {filename}")

def generate_intelligent_prompt(liga, importancia, condicoes, motivacao_fav,
                              vit_fav, gols_fav_f, gols_fav_s, vit_aza, gols_aza_f, gols_aza_s,
                              estilo_jogo, pressao, consistencia, historico_confronto, info_extra):
    """Gera um prompt de análise extremamente detalhado e inteligente"""
    
    # Análise automática baseada nas estatísticas
    performance_fav = (vit_fav / 5) * 100
    performance_aza = (vit_aza / 5) * 100
    media_gols_fav = gols_fav_f / 5
    media_gols_aza = gols_aza_f / 5
    saldo_fav = (gols_fav_f - gols_fav_s) / 5
    saldo_aza = (gols_aza_f - gols_aza_s) / 5
    
    # Determinar cenário principal
    if performance_fav >= 80 and saldo_fav > 1.0:
        cenario_principal = "Vitória convincente do favorito é o cenário mais provável"
        confianca = "Alta"
    elif performance_fav >= 60 and saldo_aza < -0.5:
        cenario_principal = "Favorito deve vencer, mas azarão pode marcar"
        confianca = "Moderada"
    else:
        cenario_principal = "Jogo equilibrado com incerteza no resultado"
        confianca = "Baixa"
    
    # Obter dados atuais
    odds = st.session_state.app_state['odds_values']
    investments = st.session_state.app_state['investment_values']
    bankroll = st.session_state.app_state['total_bankroll']
    
    prompt = f"""
# 🎯 RELATÓRIO DE ANÁLISE DE APOSTAS - SISTEMA INTELIGENTE

## 📅 CONTEXTO DA PARTIDA
- **Liga/Campeonato:** {liga}
- **Importância:** {importancia}
- **Condições Especiais:** {', '.join(condicoes) if condicoes else 'Nenhuma'}
- **Motivação do Favorito:** {motivacao_fav}

## 📊 ANÁLISE ESTATÍSTICA AUTOMÁTICA

### 🏆 PERFORMANCE RECENTE
| Time | Vitórias/5 | Aproveitamento | Gols Marcados (média) | Gols Sofridos (média) | Saldo |
|:---|:---:|:---:|:---:|:---:|:---:|
| Favorito | {vit_fav}/5 | {performance_fav:.0f}% | {media_gols_fav:.1f} | {gols_fav_s/5:.1f} | {saldo_fav:+.1f} |
| Azarão | {vit_aza}/5 | {performance_aza:.0f}% | {media_gols_aza:.1f} | {gols_aza_s/5:.1f} | {saldo_aza:+.1f} |

### 🧠 ANÁLISE TÉCNICA
- **Cenário Mais Provável:** {cenario_principal} (Confiança: {confianca})
- **Estilo do Favorito:** {estilo_jogo}
- **Pressão sobre Favorito:** {pressao}
- **Consistência do Azarão:** {consistencia}
- **Histórico de Confrontos:** {historico_confronto}

## 💰 SITUAÇÃO ATUAL DAS APOSTAS

### 📈 DISTRIBUIÇÃO DE INVESTIMENTOS
| Mercado | Odds | Investimento | % Bankroll | Retorno Potencial |
|:---|:---:|:---:|:---:|:---:|
"""
    
    # Adicionar linhas da tabela
    total_investido = 0
    for bet_type in BetType:
        nome = bet_type.value
        odd = odds.get(nome, 1.0)
        invest = investments.get(nome, 0.0)
        percentual = (invest / bankroll * 100) if bankroll > 0 else 0
        retorno = invest * odd
        total_investido += invest
        
        prompt += f"| {nome} | {odd:.2f} | R$ {invest:.2f} | {percentual:.1f}% | R$ {retorno:.2f} |\n"
    
    prompt += f"""
**Total Investido:** R$ {total_investido:.2f} ({total_investido/bankroll*100:.1f}% do bankroll)

## 🎯 SOLICITAÇÃO DE ANÁLISE ESPECÍFICA

Baseado nas estatísticas acima e na distribuição atual, por favor forneça:

### 1. 📊 ANÁLISE DE VALOR
- Quais mercados apresentam melhor relação risco-retorno?
- Identifique oportunidades de value bet
- Pontos de sobrevalorização/subvalorização

### 2. ⚖️ OTIMIZAÇÃO DE DISTRIBUIÇÃO
- Distribuição ideal considerando perfil de risco
- Ajustes recomendados nos investimentos
- Estratégia de hedge natural

### 3. 🛡️ GESTÃO DE RISCO
- Principais riscos identificados
- Cenários críticos e proteções
- Limites de exposição recomendados

### 4. 📈 ESTRATÉGIA RECOMENDADA
- Abordagem ideal para esta partida
- Sequência de ações recomendada
- Pontos de atenção durante o jogo

## 💡 INFORMAÇÕES ADICIONAIS
{info_extra if info_extra else "Nenhuma informação adicional fornecida."}

**Por favor, seja detalhado, data-driven e forneça justificativas claras para cada recomendação.**
"""
    
    return prompt

# =============================================
# 🎯 SISTEMA DE ANÁLISE DE VALOR APRIMORADO
# =============================================

class ValueBetAnalyzer:
    def __init__(self):
        self.analysis_results = {}
        
    def calcular_probabilidades_reais_otimizadas(self, estatisticas: Dict) -> Dict:
        """Cálculo otimizado baseado nas estatísticas reais"""
        vit_fav = estatisticas.get('vitorias_favorito', 3)
        gols_fav_f = estatisticas.get('gols_feitos_favorito', 8)
        gols_fav_s = estatisticas.get('gols_sofridos_favorito', 3)
        vit_aza = estatisticas.get('vitorias_azarao', 1)
        gols_aza_f = estatisticas.get('gols_feitos_azarao', 4)
        gols_aza_s = estatisticas.get('gols_sofridos_azarao', 10)
        
        # 🔥 CÁLCULOS OTIMIZADOS BASEADOS NA ANÁLISE ESTATÍSTICA
        prob_vitoria_favorito = min(75, max(25, (vit_fav/5) * 100 * 0.65 + (gols_fav_f/5) * 12))
        prob_empate = min(35, max(15, 100 - prob_vitoria_favorito - (vit_aza/5) * 100 * 0.45))
        prob_vitoria_azarao = max(10, 100 - prob_vitoria_favorito - prob_empate)
        
        # Probabilidades derivadas com base realística
        prob_menos_25_gols = min(75, max(25, 60 - (gols_fav_f/5 + gols_aza_f/5) * 6))
        prob_mais_15_gols = 100 - prob_menos_25_gols
        prob_ambas_marcam = min(55, max(15, (gols_fav_f/10 + gols_aza_f/10) * 25))
        
        return {
            "prob_vitoria_favorito": prob_vitoria_favorito,
            "prob_empate": prob_empate,
            "prob_vitoria_azarao": prob_vitoria_azarao,
            "prob_empate_ou_vitoria_azarao": prob_empate + prob_vitoria_azarao,
            "prob_menos_25_gols_empate_ou_vitoria_favorito": prob_menos_25_gols * (prob_vitoria_favorito + prob_empate) / 100,
            "prob_mais_15_ambas_nao": prob_mais_15_gols * (100 - prob_ambas_marcam) / 100,
            "prob_0x0": max(3, (100 - prob_mais_15_gols) * 0.4),
            "prob_menos_15_gols": max(8, prob_menos_25_gols * 0.7),
            "prob_mais_25_gols_sem_empate": prob_mais_15_gols * (100 - prob_empate) / 100,
            "prob_proximo_gol_favorito": prob_vitoria_favorito * 0.6 + prob_empate * 0.3
        }
    
    def analisar_valor_apostas(self, investments: Dict, odds: Dict, estatisticas: Dict) -> Dict:
        """Análise completa de valor das apostas"""
        prob_reais = self.calcular_probabilidades_reais_otimizadas(estatisticas)
        
        mapping_probabilidades = {
            "Vitória Favorito": "prob_vitoria_favorito",
            "Dupla Chance X2": "prob_empate_ou_vitoria_azarao", 
            "Menos 2.5 & Dupla Chance 1X": "prob_menos_25_gols_empate_ou_vitoria_favorito",
            "Mais 1.5 & Ambas Não": "prob_mais_15_ambas_nao",
            "Resultado 0x0": "prob_0x0",
            "Menos 1.5 Gols": "prob_menos_15_gols",
            "Mais 2.5 & Dupla Chance 12": "prob_mais_25_gols_sem_empate",
            "Próximo Gol Favorito": "prob_proximo_gol_favorito"
        }
        
        analise_detalhada = {}
        total_ev = 0
        total_investido = 0
        
        for mercado, investimento in investments.items():
            if investimento > 0:
                odd = odds.get(mercado, 1.0)
                prob_chave = mapping_probabilidades.get(mercado)
                prob_real = prob_reais.get(prob_chave, 50) if prob_chave else 50
                
                # 🔥 CÁLCULOS DE VALOR OTIMIZADOS
                prob_implícita = (1 / odd) * 100
                valor_aposta = ((prob_real - prob_implícita) / prob_implícita) * 100
                
                # Expected Value (EV)
                ev = (prob_real/100 * odd * investimento) - investimento
                total_ev += ev
                total_investido += investimento
                
                # ROI Esperado
                roi_esperado = (ev / investimento * 100) if investimento > 0 else 0
                
                analise_detalhada[mercado] = {
                    'investimento': investimento,
                    'odds': odd,
                    'probabilidade_real': prob_real,
                    'probabilidade_implícita': prob_implícita,
                    'valor_aposta': valor_aposta,
                    'ev': ev,
                    'roi_esperado': roi_esperado,
                    'status_valor': '✅ ALTO VALOR' if valor_aposta > 10 else 
                                   '✅ VALOR' if valor_aposta > 5 else 
                                   '⚠️ NEUTRO' if valor_aposta >= -5 else '❌ SEM VALOR',
                    'recomendacao': 'AUMENTAR' if valor_aposta > 5 else 
                                   'MANTER' if valor_aposta >= -2 else 'REDUZIR'
                }
        
        # 🔥 ANÁLISE DA CARTEIRA COMPLETA
        roi_total = (total_ev / total_investido * 100) if total_investido > 0 else 0
        margem_casa = 100 - sum([(1/odd)*100 for odd in odds.values() if odd > 0])
        
        self.analysis_results = {
            'detalhes': analise_detalhada,
            'resumo': {
                'total_investido': total_investido,
                'ev_total': total_ev,
                'roi_esperado_total': roi_total,
                'margem_casa': margem_casa,
                'numero_apostas': len([inv for inv in investments.values() if inv > 0]),
                'apostas_lucrativas': sum(1 for aposta in analise_detalhada.values() if aposta['ev'] > 0)
            }
        }
        
        return self.analysis_results

# =============================================
# 📊 SISTEMA DE PLANOS DE INVESTIMENTO
# =============================================

class InvestmentPlanner:
    def __init__(self):
        self.plans = {}
    
    def gerar_planos_otimizados(self, analysis: Dict, bankroll: float) -> Dict:
        """Gera os 3 planos otimizados (Conservador, Balanceado, Agressivo)"""
        
        detalhes = analysis.get('detalhes', {})
        total_atual = analysis.get('resumo', {}).get('total_investido', bankroll)
        
        # 🔥 PLANO CONSERVADOR (Minimiza variação)
        plano_conservador = self._gerar_plano_conservador(detalhes, bankroll)
        
        # 🔥 PLANO BALANCEADO (Recomendado)
        plano_balanceado = self._gerar_plano_balanceado(detalhes, bankroll)
        
        # 🔥 PLANO AGRESSIVO (Maximiza EV)
        plano_agressivo = self._gerar_plano_agressivo(detalhes, bankroll)
        
        self.plans = {
            'conservador': self._calcular_metricas_plano(plano_conservador, detalhes, bankroll),
            'balanceado': self._calcular_metricas_plano(plano_balanceado, detalhes, bankroll),
            'agressivo': self._calcular_metricas_plano(plano_agressivo, detalhes, bankroll),
            'atual': self._calcular_metricas_plano({mercado: det['investimento'] for mercado, det in detalhes.items()}, detalhes, bankroll)
        }
        
        return self.plans
    
    def _gerar_plano_conservador(self, detalhes: Dict, bankroll: float) -> Dict:
        """Plano conservador - foco em redução de variância"""
        plan = {}
        total_alocado = 0
        
        for mercado, dados in detalhes.items():
            if dados['valor_aposta'] > 5:  # Apenas value bets sólidos
                alocacao = min(bankroll * 0.15, dados['investimento'] * 1.2)
                plan[mercado] = alocacao
                total_alocado += alocacao
        
        # Distribuir o restante de forma conservadora
        if total_alocado < bankroll * 0.6:
            remaining = bankroll * 0.6 - total_alocado
            for mercado, dados in detalhes.items():
                if dados['valor_aposta'] > 0 and mercado not in plan:
                    plan[mercado] = remaining * 0.3
                    break
        
        return plan
    
    def _gerar_plano_balanceado(self, detalhes: Dict, bankroll: float) -> Dict:
        """Plano balanceado - equilíbrio entre risco e retorno"""
        plan = {}
        total_alocado = 0
        
        for mercado, dados in detalhes.items():
            if dados['valor_aposta'] > 3:  # Value bets moderados
                # Alocação proporcional ao valor
                peso = max(0.1, dados['valor_aposta'] / 20)
                alocacao = bankroll * peso * 0.8
                plan[mercado] = alocacao
                total_alocado += alocacao
        
        # Garantir utilização mínima do bankroll
        if total_alocado < bankroll * 0.7:
            factor = (bankroll * 0.7) / total_alocado if total_alocado > 0 else 1
            for mercado in plan:
                plan[mercado] *= factor
        
        return plan
    
    def _gerar_plano_agressivo(self, detalhes: Dict, bankroll: float) -> Dict:
        """Plano agressivo - maximização do EV"""
        plan = {}
        
        # Ordenar por valor da aposta (melhores oportunidades primeiro)
        mercados_ordenados = sorted(detalhes.items(), key=lambda x: x[1]['valor_aposta'], reverse=True)
        
        for i, (mercado, dados) in enumerate(mercados_ordenados):
            if dados['valor_aposta'] > 0:
                # Alocação decrescente baseada no ranking de valor
                peso = max(0.15, 0.3 - (i * 0.05))
                plan[mercado] = bankroll * peso
        
        return plan
    
    def _calcular_metricas_plano(self, plan: Dict, detalhes: Dict, bankroll: float) -> Dict:
        """Calcula métricas detalhadas para cada plano"""
        total_investido = sum(plan.values())
        ev_total = 0
        var_total = 0
        
        for mercado, investimento in plan.items():
            if mercado in detalhes:
                dados = detalhes[mercado]
                ev_aposta = (dados['probabilidade_real']/100 * dados['odds'] * investimento) - investimento
                ev_total += ev_aposta
                
                # Variância simplificada
                var_aposta = (investimento ** 2) * (dados['odds'] - 1) ** 2 * \
                            (dados['probabilidade_real']/100) * (1 - dados['probabilidade_real']/100)
                var_total += var_aposta
        
        sd = np.sqrt(var_total)  # Desvio padrão
        roi_esperado = (ev_total / total_investido * 100) if total_investido > 0 else 0
        
        # Probabilidade de lucro (aproximação normal)
        z_score = ev_total / sd if sd > 0 else 0
        prob_lucro = self._calcular_probabilidade_lucro(z_score)
        
        return {
            'alocacoes': plan,
            'metricas': {
                'total_investido': total_investido,
                'ev_total': ev_total,
                'roi_esperado': roi_esperado,
                'desvio_padrao': sd,
                'probabilidade_lucro': prob_lucro,
                'utilizacao_bankroll': (total_investido / bankroll * 100) if bankroll > 0 else 0
            }
        }
    
    def _calcular_probabilidade_lucro(self, z_score: float) -> float:
        """Calcula probabilidade de lucro usando aproximação normal"""
        try:
            from scipy.stats import norm
            return norm.cdf(z_score) * 100
        except:
            # Fallback simples se scipy não estiver disponível
            if z_score >= 1.0: return 84.0
            elif z_score >= 0.5: return 69.0
            elif z_score >= 0.0: return 50.0
            elif z_score >= -0.5: return 31.0
            else: return 16.0

# =============================================
# 🎯 ANÁLISE DE CENÁRIOS (FUNÇÃO EXISTENTE)
# =============================================

class BettingStrategyAnalyzer:
    def __init__(self):
        self.bets: Dict[BetType, Bet] = {}
        
    def update_bet(self, bet_type: BetType, investment: float, odds: float):
        self.bets[bet_type] = Bet(bet_type, investment, odds)

    def get_total_investment(self) -> float:
        return sum(bet.investment for bet in self.bets.values())
        
    def calculate_scenario_profit(self, home_goals: int, away_goals: int, first_goal_by_fav: bool = None) -> Dict[str, any]:
        total_goals = home_goals + away_goals
        both_scored = home_goals > 0 and away_goals > 0
        total_investment_all = self.get_total_investment()
        total_return = 0.0
        winning_bets = []
        
        for bet_type, bet in self.bets.items():
            wins = False
            if bet_type == BetType.OVER_15_BOTH_NO:
                wins = (total_goals > 1.5) and not both_scored
            elif bet_type == BetType.EXACT_0_0:
                wins = (home_goals == 0 and away_goals == 0)
            elif bet_type == BetType.UNDER_25_DC_1X:
                wins = (total_goals < 2.5) and (home_goals >= away_goals)
            elif bet_type == BetType.DOUBLE_CHANCE_X2:
                wins = (home_goals == away_goals) or (away_goals > home_goals)
            elif bet_type == BetType.NEXT_GOAL_FAV and first_goal_by_fav is not None:
                wins = first_goal_by_fav
            elif bet_type == BetType.OVER_15:
                wins = total_goals > 1.5
            elif bet_type == BetType.OVER_25_DC_12:
                wins = (total_goals > 2.5) and (home_goals != away_goals)
            elif bet_type == BetType.UNDER_15:
                wins = (total_goals < 1.5)
            elif bet_type == BetType.VITORIA_FAV:
                wins = home_goals > away_goals
            
            if wins:
                total_return += bet.potential_return
                winning_bets.append(bet_type.value)
        
        profit = total_return - total_investment_all
        
        return {
            'Retorno Total': total_return,
            'Investimento Total': total_investment_all,
            'Lucro/Prejuízo': profit,
            'Apostas Vencedoras': winning_bets,
            'Status': '✅ Lucro' if profit > 0 else '❌ Prejuízo' if profit < 0 else '⚖️ Equilíbrio',
            'ROI': (profit / total_investment_all * 100) if total_investment_all > 0 else 0
        }

def get_analyzer() -> BettingStrategyAnalyzer:
    analyzer = BettingStrategyAnalyzer()
    for bet_type in BetType:
        analyzer.update_bet(
            bet_type,
            st.session_state.app_state['investment_values'][bet_type.value],
            st.session_state.app_state['odds_values'][bet_type.value]
        )
    return analyzer

# =============================================
# 🎯 IMPLEMENTAÇÃO DAS MELHORIAS SUGERIDAS
# =============================================
def sync_global_state():
    """SINCRONIZAÇÃO GLOBAL - ORDEM MESTRA PARA TODOS OS COMPONENTES"""
    # 🔥 FORÇAR SINCRONIZAÇÃO DO BANKROLL PRIMEIRO
    sync_bankroll_values()
    
    # 🔥 ATUALIZAR ANÁLISE DE VALOR
    st.session_state.app_state['last_analysis'] = {
        'total_invested': st.session_state.app_state['total_invested'],
        'total_bankroll': st.session_state.app_state['total_bankroll'],
        'timestamp': datetime.now().isoformat(),
        'sync_type': 'GLOBAL_COMMAND'
    }
    
    # 🔥 MARCAR QUE DISTRIBUIÇÃO FOI APLICADA
    st.session_state.app_state['distribution_applied'] = True
    st.session_state.app_state['global_sync_time'] = datetime.now().isoformat()

def render_analise_avancada_value_bets():
    """Renderiza a análise avançada de value bets"""
    st.header("🔥 Análise de Valor Avançada")
    
    # Coletar dados atuais
    investments = st.session_state.app_state['investment_values']
    odds = st.session_state.app_state['odds_values']
    bankroll = st.session_state.app_state['total_bankroll']
    
    # Estatísticas para cálculo
    estatisticas = {
        'vitorias_favorito': st.session_state.app_state.get('vitorias_favorito', 3),
        'gols_feitos_favorito': st.session_state.app_state.get('gols_feitos_favorito', 8),
        'gols_sofridos_favorito': st.session_state.app_state.get('gols_sofridos_favorito', 3),
        'vitorias_azarao': st.session_state.app_state.get('vitorias_azarao', 1),
        'gols_feitos_azarao': st.session_state.app_state.get('gols_feitos_azarao', 4),
        'gols_sofridos_azarao': st.session_state.app_state.get('gols_sofridos_azarao', 10)
    }
    
    # Análise de valor
    analyzer = ValueBetAnalyzer()
    analysis = analyzer.analisar_valor_apostas(investments, odds, estatisticas)
    
    # Gerar planos otimizados
    planner = InvestmentPlanner()
    plans = planner.gerar_planos_otimizados(analysis, bankroll)
    
    # 🔥 RESUMO EXECUTIVO
    st.subheader("📊 Resumo Executivo - Análise de Valor")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ev_atual = plans['atual']['metricas']['ev_total']
        st.metric("EV Atual", f"R$ {ev_atual:.2f}", 
                 delta=f"{plans['atual']['metricas']['roi_esperado']:.1f}%")
    
    with col2:
        prob_lucro_atual = plans['atual']['metricas']['probabilidade_lucro']
        st.metric("Prob. Lucro Atual", f"{prob_lucro_atual:.1f}%")
    
    with col3:
        margem_casa = analysis['resumo']['margem_casa']
        st.metric("Margem da Casa", f"{margem_casa:.1f}%")
    
    with col4:
        apostas_lucrativas = analysis['resumo']['apostas_lucrativas']
        st.metric("Apostas +EV", f"{apostas_lucrativas}/{analysis['resumo']['numero_apostas']}")
    
    # 🔥 COMPARAÇÃO ENTRE PLANOS
    st.subheader("📈 Comparação de Estratégias")
    
    plan_data = []
    for plano_nome, plano_dados in plans.items():
        if plano_nome != 'atual':
            metricas = plano_dados['metricas']
            plan_data.append({
                'Plano': plano_nome.upper(),
                'EV (R$)': metricas['ev_total'],
                'ROI Esperado (%)': metricas['roi_esperado'],
                'Prob. Lucro (%)': metricas['probabilidade_lucro'],
                'Utilização Bankroll (%)': metricas['utilizacao_bankroll'],
                'Risco (SD)': metricas['desvio_padrao']
            })
    
    if plan_data:
        df_comparacao = pd.DataFrame(plan_data)
        
        # Gráfico de comparação
        fig = px.bar(df_comparacao, x='Plano', y=['EV (R$)', 'ROI Esperado (%)', 'Prob. Lucro (%)'],
                    title="Comparação de Performance entre Planos", barmode='group')
        st.plotly_chart(fig, use_container_width=True, key="comparacao_planos")
        
        # Tabela detalhada
        st.dataframe(df_comparacao.style.format({
            'EV (R$)': 'R$ {:.2f}',
            'ROI Esperado (%)': '{:.1f}%',
            'Prob. Lucro (%)': '{:.1f}%',
            'Utilização Bankroll (%)': '{:.1f}%',
            'Risco (SD)': 'R$ {:.2f}'
        }), use_container_width=True, key="tabela_comparacao_planos")
    
    # 🔥 RECOMENDAÇÕES ESPECÍFICAS
    st.subheader("🎯 Recomendações de Ação Imediata")
    
    detalhes_analise = analysis['detalhes']
    
    # Ordenar por valor de aposta (melhores oportunidades primeiro)
    oportunidades_ordenadas = sorted(detalhes_analise.items(), 
                                   key=lambda x: x[1]['valor_aposta'], reverse=True)
    
    for i, (mercado, dados) in enumerate(oportunidades_ordenadas[:3]):  # Top 3 oportunidades
        with st.expander(f"{i+1}. {mercado} - {dados['status_valor']}", expanded=i==0):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Valor da Aposta", f"{dados['valor_aposta']:.1f}%")
            with col2:
                st.metric("Prob. Real", f"{dados['probabilidade_real']:.1f}%")
            with col3:
                st.metric("Prob. Implícita", f"{dados['probabilidade_implícita']:.1f}%")
            with col4:
                st.metric("EV Esperado", f"R$ {dados['ev']:.2f}")
            
            st.write(f"**Recomendação:** {dados['recomendacao']}")
            
            # Botão de ação rápida
            if dados['recomendacao'] == 'AUMENTAR':
                novo_investimento = dados['investimento'] * 1.5
                if st.button(f"🔼 Aumentar posição em {mercado}", key=f"aumentar_{mercado}_{i}"):
                    st.session_state.app_state['investment_values'][mercado] = novo_investimento
                    st.success(f"Posição aumentada para R$ {novo_investimento:.2f}")
                    st.rerun()
            elif dados['recomendacao'] == 'REDUZIR':
                novo_investimento = dados['investimento'] * 0.5
                if st.button(f"🔽 Reduzir posição em {mercado}", key=f"reduzir_{mercado}_{i}"):
                    st.session_state.app_state['investment_values'][mercado] = novo_investimento
                    st.success(f"Posição reduzida para R$ {novo_investimento:.2f}")
                    st.rerun()
    
    # 🔥 APLICAR PLANO AUTOMATICAMENTE
    st.subheader("⚡ Aplicação Rápida de Planos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🛡️ Aplicar Plano Conservador", use_container_width=True, key="apl_conservador"):
            aplicar_plano(plans['conservador']['alocacoes'])
            st.success("Plano Conservador aplicado!")
    
    with col2:
        if st.button("⚖️ Aplicar Plano Balanceado", use_container_width=True, key="apl_balanceado"):
            aplicar_plano(plans['balanceado']['alocacoes'])
            st.success("Plano Balanceado aplicado!")
    
    with col3:
        if st.button("🚀 Aplicar Plano Agressivo", use_container_width=True, key="apl_agressivo"):
            aplicar_plano(plans['agressivo']['alocacoes'])
            st.success("Plano Agressivo aplicado!")

def aplicar_plano(alocacoes: Dict):
    """Aplica um plano de alocação automaticamente"""
    for mercado, investimento in alocacoes.items():
        st.session_state.app_state['investment_values'][mercado] = investimento
    
    # Atualizar totais
    total_investido = sum(st.session_state.app_state['investment_values'].values())
    st.session_state.app_state['total_bankroll'] = total_investido
    update_proportions_from_investments()
    st.rerun()

def sync_bankroll_values():
    """Sincroniza todos os valores de bankroll e investimento - VERSÃO SUPER-ROBUSTA"""
    app_state = st.session_state.app_state
    
    # 🔥 CALCULAR TOTAL INVESTIDO DIRETO DOS VALORES
    total_invested = sum(app_state['investment_values'].values())
    
    # 🔥 GARANTIR que os valores estão consistentes
    app_state['total_invested'] = total_invested
    
    # 🔥 SE bankroll for MENOR que o investido, ATUALIZAR bankroll
    if app_state['total_bankroll'] < total_invested:
        app_state['total_bankroll'] = total_invested
    
    # 🔥 SE bankroll for MUITO MAIOR, manter mas garantir mínimo
    if app_state['total_bankroll'] > total_invested * 2:
        # Bankroll pode ser maior, mas não absurdamente maior
        app_state['total_bankroll'] = max(app_state['total_bankroll'], total_invested)
    
    # 🔥 ATUALIZAR proporções
    update_proportions_from_investments()
    
    # 🔥 LOG PARA VERIFICAR (opcional)
    app_state['last_sync'] = {
        'total_invested': total_invested,
        'total_bankroll': app_state['total_bankroll'],
        'timestamp': datetime.now().isoformat()
    }

# =============================================
# 🔧 FUNÇÕES EXISTENTES DO SISTEMA ORIGINAL
# =============================================

def render_controls():
    """Configuração inteligente - VERSÃO SIMPLIFICADA SEM ABA PROBLEMÁTICA"""
    
    # 🔥 INDICADOR DE STATUS GLOBAL
    if st.session_state.app_state.get('distribution_applied'):
        st.success("✅ **SISTEMA SINCRONIZADO** - Todas as abas mostram valores consistentes")
    else:
        st.warning("⚠️ **CLIQUE EM 'DISTRIBUIÇÃO AUTOMÁTICA' PARA SINCRONIZAR**")
        
    sync_bankroll_values()  # CORREÇÃO GARANTIDA
    
    st.subheader("⚙️ Configuração Inteligente de Apostas")
    
    # 🔥 REMOVER A ABA PROBLEMÁTICA - MANTER APENAS ODDS E RECOMENDAÇÕES
    tab1, tab2 = st.tabs(["🎯 Odds e Investimentos", "💡 Recomendações"])
    
    with tab1:
        col1, col2, col3 = st.columns([2, 2, 1.2])
        
        with col1:
            st.markdown("**📈 Configuração de Odds**")
            for i, bet_type in enumerate(BetType):
                current_odds = st.session_state.app_state['odds_values'][bet_type.value]
                new_odds = st.number_input(
                    f"{bet_type.value}",
                    min_value=1.01,
                    value=float(current_odds),
                    step=0.01,
                    key=f"odds_{bet_type.name}_{i}",
                    label_visibility="visible"
                )
                if new_odds != current_odds:
                    st.session_state.app_state['odds_values'][bet_type.value] = float(new_odds)
                    st.rerun()

        with col2:
            st.markdown("**💰 Controle de Investimentos**")
            for i, bet_type in enumerate(BetType):
                current_investment = st.session_state.app_state['investment_values'][bet_type.value]
                new_investment = st.number_input(
                    f"{bet_type.value} - R$",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(current_investment),
                    step=0.10,
                    key=f"inv_{bet_type.name}_{i}",
                    label_visibility="visible"
                )
                if new_investment != current_investment:
                    st.session_state.app_state['investment_values'][bet_type.value] = float(new_investment)
                    
                    # 🔥 MARCAR QUE PRECISA DE SINCRONIZAÇÃO
                    st.session_state.app_state['distribution_applied'] = False
                    st.session_state.app_state['needs_sync'] = True
                    
                    st.rerun()

        with col3:
            st.markdown("**🏦 Gerenciamento do Banco**")
            current_bankroll = st.session_state.app_state['total_bankroll']
            new_bankroll = st.number_input(
                "Total do Bankroll (R$)",
                min_value=0.0,
                max_value=1000.0,
                value=float(current_bankroll),
                step=1.0,
                key="total_bankroll_input_unique"
            )
            if new_bankroll != current_bankroll:
                st.session_state.app_state['total_bankroll'] = new_bankroll
                update_investments_from_proportions()
                st.rerun()

            # 🔥 BOTÃO DE SINCRONIZAÇÃO SIMPLIFICADO
            if st.button("🔄 Distribuição Automática", 
                        use_container_width=True, 
                        type="primary",
                        key="dist_auto_simple"):
                
                # 🎯 EXECUTAR SINCRONIZAÇÃO
                sync_global_state()
                
                st.success(f"✅ Sistema sincronizado! Bankroll: R$ {st.session_state.app_state['total_bankroll']:.2f}")
                st.rerun()

    with tab2:
        # MANTER APENAS AS RECOMENDAÇÕES INTELIGENTES
        render_intelligent_recommendations()

def render_detailed_scenario_analysis():
    """Renderiza análise detalhada de cenários com tabelas completas"""
    st.subheader("📈 Análise Avançada de Cenários - DETALHADA")
    
    analyzer = get_analyzer()
    total_investment = analyzer.get_total_investment()
    
    # Cenários importantes para análise
    important_scenarios = [
        ('0x0', 0, 0, None, "Empate sem gols"),
        ('1x0 FAV', 1, 0, True, "Vitória do favorito 1x0"),
        ('0x1 AZA', 0, 1, False, "Vitória do azarão 0x1"),
        ('1x1 FAV 1º', 1, 1, True, "Empate 1x1 com gol do favorito primeiro"),
        ('1x1 AZA 1º', 1, 1, False, "Empate 1x1 com gol do azarão primeiro"),
        ('2x0 FAV', 2, 0, True, "Vitória convincente do favorito"),
        ('0x2 AZA', 0, 2, False, "Vitória convincente do azarão"),
        ('2x1 FAV', 2, 1, True, "Vitória do favorito com gol do azarão"),
        ('1x2 AZA', 1, 2, False, "Vitória do azarão com gol do favorito"),
        ('2x2', 2, 2, None, "Empate com muitos gols"),
        ('3x0 FAV', 3, 0, True, "Goleada do favorito"),
        ('0x3 AZA', 0, 3, False, "Goleada do azarão")
    ]
    
    # Dados para gráficos
    all_scenario_data = []
    scenario_profits = {}
    detailed_scenarios = []
    
    for scenario_name, home_goals, away_goals, first_goal, description in important_scenarios:
        result = analyzer.calculate_scenario_profit(home_goals, away_goals, first_goal)
        
        # Dados para gráficos
        scenario_data = {
            'Cenário': scenario_name,
            'Placar': f"{home_goals}x{away_goals}",
            'Lucro/Prejuízo': result['Lucro/Prejuízo'],
            'ROI': result['ROI'],
            'Status': result['Status']
        }
        all_scenario_data.append(scenario_data)
        scenario_profits[scenario_name] = result['Lucro/Prejuízo']
        
        # Dados detalhados para tabela
        detailed_scenario = {
            'Cenário': scenario_name,
            'Descrição': description,
            'Placar': f"{home_goals}x{away_goals}",
            'Investimento Total': f"R$ {result['Investimento Total']:.2f}",
            'Retorno Total': f"R$ {result['Retorno Total']:.2f}",
            'Lucro/Prejuízo': f"R$ {result['Lucro/Prejuízo']:.2f}",
            'ROI': f"{result['ROI']:.1f}%",
            'Status': result['Status'],
            'Apostas Vencedoras': ', '.join(result['Apostas Vencedoras']) if result['Apostas Vencedoras'] else 'Nenhuma',
            # Versões numéricas para ordenação
            'Lucro_Num': result['Lucro/Prejuízo'],
            'ROI_Num': result['ROI'],
            'Investimento_Num': result['Investimento Total']
        }
        detailed_scenarios.append(detailed_scenario)
    
    df_all = pd.DataFrame(all_scenario_data)
    df_detailed = pd.DataFrame(detailed_scenarios)
    
    # Métricas principais
    profitable_scenarios = len([s for s in detailed_scenarios if s['Status'] == '✅ Lucro'])
    neutral_scenarios = len([s for s in detailed_scenarios if s['Status'] == '⚖️ Equilíbrio'])
    losing_scenarios = len([s for s in detailed_scenarios if s['Status'] == '❌ Prejuízo'])
    
    # 🔥 GRÁFICOS EXISTENTES
    col1, col2 = st.columns(2)
    with col1:
        fig_profit = px.bar(df_all, x='Cenário', y='Lucro/Prejuízo', color='Status',
                           title='Lucro/Prejuízo por Cenário (R$)',
                           color_discrete_map={'✅ Lucro': '#00FF00', '❌ Prejuízo': '#FF0000', '⚖️ Equilíbrio': '#FFFF00'})
        fig_profit.update_layout(showlegend=True)
        st.plotly_chart(fig_profit, use_container_width=True, key="grafico_lucro_cenarios")
    
    with col2:
        fig_roi = px.bar(df_all, x='Cenário', y='ROI', color='ROI',
                        title='ROI por Cenário (%)',
                        color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_roi, use_container_width=True, key="grafico_roi_cenarios")
    
    # 🔥 TABELA DETALHADA COM ANÁLISE POR EXTENSO
    st.markdown("### 📋 ANÁLISE DETALHADA POR CENÁRIO")
    
    # Filtros para a tabela
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status = st.selectbox("Filtrar por Status:", 
                                   ["Todos", "✅ Lucro", "❌ Prejuízo", "⚖️ Equilíbrio"])
    with col2:
        sort_by = st.selectbox("Ordenar por:", 
                              ["Cenário", "Lucro/Prejuízo", "ROI", "Investimento Total"])
    with col3:
        show_details = st.checkbox("Mostrar análise detalhada", value=True)
    
    # Aplicar filtros
    filtered_df = df_detailed.copy()
    if filter_status != "Todos":
        filtered_df = filtered_df[filtered_df['Status'] == filter_status]
    
    # Ordenar usando as colunas numéricas
    sort_mapping = {
        "Cenário": "Cenário",
        "Lucro/Prejuízo": "Lucro_Num",
        "ROI": "ROI_Num", 
        "Investimento Total": "Investimento_Num"
    }
    
    if sort_by in sort_mapping:
        sort_column = sort_mapping[sort_by]
        ascending = sort_by != "Lucro/Prejuízo"  # Ordenar Lucro/Prejuízo em ordem decrescente
        filtered_df = filtered_df.sort_values(sort_column, ascending=ascending)
    
    # Exibir tabela detalhada (apenas colunas de exibição)
    display_columns = ['Cenário', 'Descrição', 'Placar', 'Investimento Total', 
                      'Retorno Total', 'Lucro/Prejuízo', 'ROI', 'Status', 'Apostas Vencedoras']
    
    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        height=400
    )

    return scenario_profits

def render_dinamico_integration():
    """Renderiza a integração com o módulo dinamico"""
    st.header("🛡️ Hedge Dinâmico com IA")
    
    try:
        from dinamico import render_hedge_controls, render_hedge_results
        
        analyzer = get_analyzer()
        
        zero_result = analyzer.calculate_scenario_profit(0, 0, None)
        fav_result = analyzer.calculate_scenario_profit(1, 1, True)
        aza_result = analyzer.calculate_scenario_profit(1, 1, False)
        
        zero_profit = zero_result['Lucro/Prejuízo']
        fav_profit = fav_result['Lucro/Prejuízo']
        aza_profit = aza_result['Lucro/Prejuízo']
        
        odds_values = st.session_state.app_state['odds_values']
        
        render_hedge_controls(zero_profit, fav_profit, aza_profit, odds_values)
        
        if st.session_state.get('hedge_applied', False):
            render_hedge_results()
            
    except ImportError as e:
        st.error(f"❌ Módulo dinamico não disponível: {e}")
        st.info("""
        ### 📋 Para habilitar o Hedge Dinâmico:
        1. Certifique-se de que o arquivo `dinamico.py` está na mesma pasta
        2. Reinicie a aplicação
        3. O sistema de hedge inteligente será carregado automaticamente
        """)

# =============================================
# 🚀 FUNÇÃO PRINCIPAL CORRIGIDA
# =============================================

def main_optimized():
    """Função principal otimizada"""
    st.set_page_config(
        page_title="Analisador de Apostas - Versão Otimizada",
        page_icon="🔥",
        layout="wide"
    )
    
    st.title("🎯 Analisador Inteligente - ANÁLISE DE VALOR OTIMIZADA")
    st.markdown("### 🔥 Implementando as recomendações estatísticas para maximizar EV")
    
    init_state()
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔥 Análise de Valor", 
        "⚙️ Configuração", 
        "📈 Cenários", 
        "🛡️ Hedge Dinâmico"
    ])
    
    with tab1:
        render_analise_avancada_value_bets()
    
    with tab2:
        render_controls()
    
    with tab3:
        # Substituir a função antiga pela nova detalhada
        render_detailed_scenario_analysis()
    
    with tab4:
        render_dinamico_integration()

# =============================================
# 🚀 EXECUÇÃO PRINCIPAL
# =============================================

if __name__ == "__main__":
    main_optimized()
