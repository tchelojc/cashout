# ao_vivo.py (versão final aprimorada COM CONTINUIDADE)
import streamlit as st
import pandas as pd
import plotly.express as px
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json
import sys
import os
import numpy as np
from datetime import datetime

# Adiciona o diretório atual ao path para importar o módulo dinamico
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# =============================================
# ✅ IMPORTAÇÕES ATUALIZADAS DO MÓDULO DINAMICO
# =============================================
try:
    from dinamico import (
        DynamicHedgeManager, 
        RedistributionStrategy, 
        HedgeBet, 
        init_hedge_state, 
        render_hedge_controls, 
        render_hedge_results,
        get_current_operation_info,      # ✅ NOVA IMPORTação
        continue_operation_from_id       # ✅ NOVA IMPORTação
    )
    dinamico_available = True
except ImportError as e:
    st.error(f"Módulo dinamico não pôde ser carregado: {e}")
    dinamico_available = False

# --- Enumeração dos Tipos de Aposta ---
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

# --- Estrutura de Dados para uma Aposta ---
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
        """Calcula a probabilidade implícita baseada nas odds"""
        return (1 / self.odds) * 100 if self.odds > 0 else 0

# --- ANÁLISE DE PROBABILIDADES E VALOR DAS ODDS ---
class ProbabilityAnalyzer:
    def __init__(self):
        self.probability_mapping = {
            "Vitória Favorito": "prob_vitoria_favorito",
            "Dupla Chance X2": "prob_empate_ou_vitoria_azarao", 
            "Menos 2.5 & Dupla Chance 1X": "prob_menos_25_gols_empate_ou_vitoria_favorito",
            "Mais 1.5 & Ambas Não": "prob_mais_15_ambas_nao",
            "Resultado 0x0": "prob_0x0",
            "Menos 1.5 Gols": "prob_menos_15_gols",
            "Mais 2.5 & Dupla Chance 12": "prob_mais_25_gols_sem_empate",
            "Próximo Gol Favorito": "prob_proximo_gol_favorito"
        }
    
    def calcular_probabilidades_reais(self, estatisticas: Dict) -> Dict:
        """Calcula probabilidades reais baseadas nas estatísticas da partida"""
        vit_fav = estatisticas.get('vitorias_favorito', 3)
        gols_fav_f = estatisticas.get('gols_feitos_favorito', 8)
        gols_fav_s = estatisticas.get('gols_sofridos_favorito', 3)
        vit_aza = estatisticas.get('vitorias_azarao', 1)
        gols_aza_f = estatisticas.get('gols_feitos_azarao', 4)
        gols_aza_s = estatisticas.get('gols_sofridos_azarao', 10)
        
        # Cálculo baseado em estatísticas reais com ajustes mais precisos
        prob_vitoria_favorito = min(75, max(25, (vit_fav/5) * 100 * 0.65 + (gols_fav_f/5) * 12))
        prob_empate = min(35, max(15, 100 - prob_vitoria_favorito - (vit_aza/5) * 100 * 0.45))
        prob_vitoria_azarao = max(10, 100 - prob_vitoria_favorito - prob_empate)
        
        # Probabilidades derivadas mais realistas
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
    
    def calcular_valor_aposta(self, odds: float, probabilidade_real: float) -> float:
        """Calcula o valor esperado de uma aposta (Value Bet)"""
        probabilidade_implícita = (1 / odds) * 100
        valor = (probabilidade_real - probabilidade_implícita) / probabilidade_implícita * 100
        return valor
    
    def analisar_distribuicao(self, investment_values: Dict, odds_values: Dict, estatisticas: Dict) -> Dict:
        """Analisa a distribuição atual com base nas probabilidades reais"""
        prob_reais = self.calcular_probabilidades_reais(estatisticas)
        analise = {}
        
        for mercado, investimento in investment_values.items():
            if investimento > 0:
                odds = odds_values.get(mercado, 1.0)
                prob_chave = self.probability_mapping.get(mercado)
                prob_real = prob_reais.get(prob_chave, 50)
                
                valor_aposta = self.calcular_valor_aposta(odds, prob_real)
                probabilidade_implícita = (1 / odds) * 100
                
                analise[mercado] = {
                    'investimento': investimento,
                    'odds': odds,
                    'probabilidade_real': prob_real,
                    'probabilidade_implícita': probabilidade_implícita,
                    'valor_aposta': valor_aposta,
                    'status_valor': '✅ VALOR' if valor_aposta > 5 else '⚠️ NEUTRO' if valor_aposta >= -5 else '❌ SEM VALOR',
                    'diferenca_probabilidades': prob_real - probabilidade_implícita,
                    'retorno_esperado': (prob_real/100 * odds * investimento) - investimento
                }
        
        return analise

# --- SISTEMA DE RECOMENDAÇÕES INTELIGENTES ---
class RecommendationEngine:
    def __init__(self):
        self.recommendation_rules = {
            'HIGH_VALUE': {
                'condition': lambda x: x['valor_aposta'] > 10,
                'message': "🔥 OPORTUNIDADE EXCELENTE - Alto valor identificado",
                'priority': 1
            },
            'GOOD_VALUE': {
                'condition': lambda x: x['valor_aposta'] > 5,
                'message': "✅ BOA OPORTUNIDADE - Valor positivo consistente",
                'priority': 2
            },
            'NEUTRAL': {
                'condition': lambda x: -5 <= x['valor_aposta'] <= 5,
                'message': "⚠️ NEUTRO - Considerar outros fatores",
                'priority': 3
            },
            'POOR_VALUE': {
                'condition': lambda x: x['valor_aposta'] < -5,
                'message': "❌ EVITAR - Valor negativo significativo",
                'priority': 4
            }
        }
    
    def generate_recommendations(self, analysis: Dict, total_bankroll: float) -> List[Dict]:
        """Gera recomendações inteligentes baseadas na análise de valor"""
        recommendations = []
        
        for mercado, dados in analysis.items():
            for rule_name, rule in self.recommendation_rules.items():
                if rule['condition'](dados):
                    # Calcular ajuste sugerido
                    current_percent = (dados['investimento'] / total_bankroll) * 100
                    
                    if rule_name in ['HIGH_VALUE', 'GOOD_VALUE']:
                        suggested_percent = min(25, current_percent * 1.5)
                        action = "AUMENTAR"
                        reason = f"Probabilidade real ({dados['probabilidade_real']:.1f}%) supera a implícita ({dados['probabilidade_implícita']:.1f}%)"
                    else:
                        suggested_percent = max(0, current_percent * 0.5)
                        action = "REDUZIR"
                        reason = f"Probabilidade implícita ({dados['probabilidade_implícita']:.1f}%) supera a real ({dados['probabilidade_real']:.1f}%)"
                    
                    recommendations.append({
                        'mercado': mercado,
                        'acao': action,
                        'percentual_atual': current_percent,
                        'percentual_sugerido': suggested_percent,
                        'valor_aposta': dados['valor_aposta'],
                        'mensagem': rule['message'],
                        'motivacao': reason,
                        'prioridade': rule['priority'],
                        'investimento_sugerido': total_bankroll * (suggested_percent / 100)
                    })
                    break
        
        # Ordenar por prioridade e valor da aposta
        recommendations.sort(key=lambda x: (x['prioridade'], -abs(x['valor_aposta'])))
        return recommendations

# --- CLASSE PRINCIPAL DE ANÁLISE (APRIMORADA) ---
class BettingStrategyAnalyzer:
    def __init__(self):
        self.bets: Dict[BetType, Bet] = {}
        self.prob_analyzer = ProbabilityAnalyzer()
        self.recommendation_engine = RecommendationEngine()
        
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
    
    def analisar_valor_odds(self, estatisticas: Dict) -> Dict:
        """Analisa o valor das odds baseado nas probabilidades reais"""
        investment_values = {bet_type.value: bet.investment for bet_type, bet in self.bets.items()}
        odds_values = {bet_type.value: bet.odds for bet_type, bet in self.bets.items()}
        
        return self.prob_analyzer.analisar_distribuicao(investment_values, odds_values, estatisticas)
    
    def gerar_recomendacoes_inteligentes(self, estatisticas: Dict, total_bankroll: float) -> List[Dict]:
        """Gera recomendações inteligentes baseadas em análise estatística"""
        analysis = self.analisar_valor_odds(estatisticas)
        return self.recommendation_engine.generate_recommendations(analysis, total_bankroll)

def init_state():
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

        # DISTRIBUIÇÃO INICIAL CORRIGIDA - TOTAL 8.50
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
        
        # BANKROLL INICIAL = SOMA DOS INVESTIMENTOS (8.50)
        initial_bankroll = sum(default_investments.values())
        
        st.session_state.app_state = {
            'odds_values': default_odds,
            'investment_values': default_investments,
            'total_bankroll': initial_bankroll,
            'investment_proportions': {},
            'last_analysis': {},
            'user_profile': 'Moderado',
            'show_odds_analysis': True,
            'distribution_applied': False
        }
        update_proportions_from_investments()
    
    if dinamico_available and 'hedge_manager' not in st.session_state:
        init_hedge_state()

def get_analyzer() -> BettingStrategyAnalyzer:
    analyzer = BettingStrategyAnalyzer()
    for bet_type in BetType:
        analyzer.update_bet(
            bet_type,
            st.session_state.app_state['investment_values'][bet_type.value],
            st.session_state.app_state['odds_values'][bet_type.value]
        )
    return analyzer

def update_investments_from_proportions():
    total_bankroll = st.session_state.app_state['total_bankroll']
    proportions = st.session_state.app_state.get('investment_proportions', {})
    
    for bet_type in BetType:
        proportion = proportions.get(bet_type.value, 0)
        st.session_state.app_state['investment_values'][bet_type.value] = total_bankroll * proportion
    
    # GARANTIR QUE O BANKROLL SEJA ATUALIZADO COM OS NOVOS VALORES
    total_invested = sum(st.session_state.app_state['investment_values'].values())
    st.session_state.app_state['total_bankroll'] = total_invested  # Mantém consistência

def update_proportions_from_investments():
    total_investment = sum(st.session_state.app_state['investment_values'].values())
    
    if total_investment > 0:
        proportions = {}
        for bet_type in BetType:
            investment = st.session_state.app_state['investment_values'][bet_type.value]
            proportions[bet_type.value] = investment / total_investment
        st.session_state.app_state['investment_proportions'] = proportions
    else:
        # Se não há investimento, define proporções zeradas
        for bet_type in BetType:
            st.session_state.app_state['investment_proportions'][bet_type.value] = 0.0

def render_controls():
    st.subheader("⚙️ Configuração Inteligente de Apostas")
    
    # Sistema de abas para organização
    tab1, tab2, tab3 = st.tabs(["🎯 Odds e Investimentos", "📊 Análise em Tempo Real", "💡 Recomendações"])
    
    with tab1:
        col1, col2, col3 = st.columns([2, 2, 1.2])
        
        with col1:
            st.markdown("**📈 Configuração de Odds**")
            bet_names_odds = [
                "Mais 1.5 & Ambas Não",
                "Resultado 0x0", 
                "Menos 2.5 & Dupla Chance 1X",
                "Dupla Chance X2",
                "Próximo Gol Favorito",
                "Mais 1.5 Gols",
                "Mais 2.5 & Dupla Chance 12",
                "Menos 1.5 Gols",
                "Vitória Favorito"
            ]
            
            for i, bet_type in enumerate(BetType):
                current_odds = st.session_state.app_state['odds_values'][bet_type.value]
                new_odds = st.number_input(
                    f"{bet_names_odds[i]}",
                    min_value=1.01,
                    value=float(current_odds),
                    step=0.01,
                    key=f"odds_{bet_type.name}",
                    label_visibility="visible"
                )
                if new_odds != current_odds:
                    st.session_state.app_state['odds_values'][bet_type.value] = float(new_odds)
                    st.rerun()

        with col2:
            st.markdown("**💰 Controle de Investimentos**")
            bet_names_investments = [
                "Mais 1.5 & Ambas Não - R$",
                "Resultado 0x0 - R$", 
                "Menos 2.5 & Dupla Chance 1X - R$",
                "Dupla Chance X2 - R$",
                "Próximo Gol Favorito - R$",
                "Mais 1.5 Gols - R$",
                "Mais 2.5 & Dupla Chance 12 - R$",
                "Menos 1.5 Gols - R$",
                "Vitória Favorito - R$"
            ]
            
            for i, bet_type in enumerate(BetType):
                current_investment = st.session_state.app_state['investment_values'][bet_type.value]
                new_investment = st.number_input(
                    f"{bet_names_investments[i]}",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(current_investment),
                    step=0.10,
                    key=f"inv_{bet_type.name}",
                    label_visibility="visible"
                )
                if new_investment != current_investment:
                    # ATUALIZA O INVESTIMENTO IMEDIATAMENTE
                    st.session_state.app_state['investment_values'][bet_type.value] = float(new_investment)
                    
                    # ATUALIZA O BANKROLL COM A SOMA ATUALIZADA
                    total_invested = sum(st.session_state.app_state['investment_values'].values())
                    st.session_state.app_state['total_bankroll'] = total_invested
                    
                    # ATUALIZA AS PROPORÇÕES
                    update_proportions_from_investments()
                    
                    st.session_state.app_state['distribution_applied'] = False
                    st.rerun()  # FORÇA ATUALIZAÇÃO IMEDIATA

        with col3:
            st.markdown("**🏦 Gerenciamento do Banco**")
            
            # USA O VALOR ATUAL DO BANKROLL DO SESSION STATE
            current_bankroll = st.session_state.app_state['total_bankroll']
            
            new_bankroll = st.number_input(
                "Total do Bankroll (R$)",
                min_value=0.0,
                max_value=1000.0,
                value=float(current_bankroll),  # USA O VALOR ATUAL
                step=1.0,
                key="total_bankroll_input"
            )

            if new_bankroll != current_bankroll:
                st.session_state.app_state['total_bankroll'] = new_bankroll
                update_investments_from_proportions()
                st.rerun()

            if st.button("🔄 Distribuição Automática", use_container_width=True):
                update_investments_from_proportions()
                st.session_state.app_state['distribution_applied'] = True
                st.success("Distribuição aplicada!")
                st.rerun()
                
            # ✅ CORREÇÃO: REMOVIDA A INFORMAÇÃO REDUNDANTE DO "TOTAL ALOCADO"
            st.markdown("---")
            st.markdown("**📋 Resumo da Estratégia**")
            
            total_bankroll = st.session_state.app_state['total_bankroll']
            total_invested = sum(st.session_state.app_state['investment_values'].values())
            
            if total_bankroll > 0:
                # ✅ APENAS INFORMAÇÕES ESSENCIAIS E NÃO REDUNDANTES
                utilization = (total_invested / total_bankroll) * 100
                st.metric("Utilização do Bankroll", f"{utilization:.1f}%")
                
                # Mostrar apenas as apostas ativas de forma simplificada
                investments = st.session_state.app_state['investment_values']
                active_bets = [(bet, amount) for bet, amount in investments.items() if amount > 0]
                
                if active_bets:
                    st.markdown("**🎯 Apostas Ativas:**")
                    # Mostrar apenas o top 3 para não poluir a interface
                    top_bets = sorted(active_bets, key=lambda x: x[1], reverse=True)[:3]
                    for bet, amount in top_bets:
                        st.write(f"• {bet}: R$ {amount:.2f}")
                else:
                    st.info("ℹ️ Nenhuma aposta ativa")

    with tab2:
        render_realtime_analysis()
    
    with tab3:
        render_intelligent_recommendations()
        
def render_realtime_analysis():
    """Análise em tempo real dos investimentos"""
    st.markdown("**📊 Análise Instantânea**")
    
    # USA OS VALORES ATUAIS DO SESSION STATE
    total_invested = sum(st.session_state.app_state['investment_values'].values())
    total_bankroll = st.session_state.app_state['total_bankroll']
    
    if total_bankroll > 0:
        investment_percentage = (total_invested / total_bankroll) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Investido", f"R$ {total_invested:.2f}")
        with col2:
            st.metric("Bankroll Disponível", f"R$ {total_bankroll:.2f}")
        with col3:
            st.metric("% Utilizado", f"{investment_percentage:.1f}%")
        
        # Barra de progresso
        st.progress(min(1.0, investment_percentage / 100))
        
        # Alertas inteligentes
        if investment_percentage > 80:
            st.warning("⚠️ Alto comprometimento do bankroll. Considere reduzir exposição.")
        elif investment_percentage < 20:
            st.info("💡 Baixa utilização do bankroll. Oportunidade para aumentar posições.")
    
    # Lista de apostas ativas - SEMPRE ATUALIZADA
    active_bets = []
    for bet_type in BetType:
        investment = st.session_state.app_state['investment_values'][bet_type.value]
        if investment > 0:
            odds = st.session_state.app_state['odds_values'][bet_type.value]
            potential_return = investment * odds
            active_bets.append({
                'Mercado': bet_type.value,
                'Investimento': investment,
                'Odds': odds,
                'Retorno Potencial': potential_return
            })
    
    if active_bets:
        st.markdown("**🎯 Apostas Ativas**")
        df_active = pd.DataFrame(active_bets)
        st.dataframe(df_active.style.format({
            'Investimento': 'R$ {:.2f}',
            'Retorno Potencial': 'R$ {:.2f}',
            'Odds': '{:.2f}'
        }), use_container_width=True)

def render_intelligent_recommendations():
    """Sistema de recomendações inteligentes"""
    st.markdown("**💡 Recomendações Baseadas em Análise**")
    
    # Coletar estatísticas básicas para análise
    estatisticas = {
        'vitorias_favorito': st.session_state.get('vitorias_favorito', 3),
        'gols_feitos_favorito': st.session_state.get('gols_feitos_favorito', 8),
        'gols_sofridos_favorito': st.session_state.get('gols_sofridos_favorito', 3),
        'vitorias_azarao': st.session_state.get('vitorias_azarao', 1),
        'gols_feitos_azarao': st.session_state.get('gols_feitos_azarao', 4),
        'gols_sofridos_azarao': st.session_state.get('gols_sofridos_azarao', 10)
    }
    
    analyzer = get_analyzer()
    recommendations = analyzer.gerar_recomendacoes_inteligentes(
        estatisticas, 
        st.session_state.app_state['total_bankroll']
    )
    
    if recommendations:
        for rec in recommendations:
            with st.expander(f"{rec['acao']} - {rec['mercado']} ({rec['mensagem']})", expanded=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Motivo:** {rec['motivacao']}")
                    st.write(f"**Valor da Aposta:** {rec['valor_aposta']:.1f}%")
                
                with col2:
                    st.metric("Atual", f"{rec['percentual_atual']:.1f}%")
                
                with col3:
                    st.metric("Sugerido", f"{rec['percentual_sugerido']:.1f}%")
                
                # Botão de ação rápida
                if st.button(f"🔄 Aplicar para {rec['mercado']}", key=f"apply_{rec['mercado']}"):
                    # Aplica a recomendação automaticamente
                    new_investment = rec['investimento_sugerido']
                    st.session_state.app_state['investment_values'][rec['mercado']] = new_investment
                    update_proportions_from_investments()
                    st.success(f"Investimento em {rec['mercado']} ajustado para R$ {new_investment:.2f}")
                    st.rerun()
    else:
        st.info("🔍 Configure as odds e investimentos para receber recomendações personalizadas.")

# --- ANÁLISE DE CENÁRIOS APRIMORADA ---
def render_scenario_analysis():
    st.subheader("📈 Análise Avançada de Cenários")
    
    # Seção de análise de valor das odds
    if st.session_state.get('show_odds_analysis', True):
        render_odds_value_analysis()
    
    analyzer = get_analyzer()
    
    # Cenários mais realistas e abrangentes
    important_scenarios = [
        ('0x0', 0, 0, None),
        ('1x0 FAV', 1, 0, True),
        ('0x1 AZA', 0, 1, False),
        ('1x1 FAV 1º', 1, 1, True),
        ('1x1 AZA 1º', 1, 1, False),
        ('2x0 FAV', 2, 0, True),
        ('0x2 AZA', 0, 2, False),
        ('2x1 FAV', 2, 1, True),
        ('1x2 AZA', 1, 2, False),
        ('2x2', 2, 2, None),
        ('3x0 FAV', 3, 0, True),
        ('0x3 AZA', 0, 3, False)
    ]
    
    all_scenario_data = []
    scenario_profits = {}
    scenario_details = {}
    
    for scenario_name, home_goals, away_goals, first_goal in important_scenarios:
        result = analyzer.calculate_scenario_profit(home_goals, away_goals, first_goal)
        scenario_data = {
            'Cenário': scenario_name,
            'Placar': f"{home_goals}x{away_goals}",
            '1º Gol': 'FAV' if first_goal is True else 'AZA' if first_goal is False else '-',
            'Retorno Total': result['Retorno Total'],
            'Investimento Total': result['Investimento Total'],
            'Lucro/Prejuízo': result['Lucro/Prejuízo'],
            'ROI': result['ROI'],
            'Status': result['Status'],
            'Apostas Vencedoras': result['Apostas Vencedoras']
        }
        
        all_scenario_data.append(scenario_data)
        scenario_profits[scenario_name] = result['Lucro/Prejuízo']
        scenario_details[scenario_name] = result
    
    df_all = pd.DataFrame(all_scenario_data)
    
    # Visualizações gráficas aprimoradas
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de lucro/prejuízo
        fig_profit = px.bar(
            df_all, 
            x='Cenário', 
            y='Lucro/Prejuízo', 
            color='Status',
            title='Lucro/Prejuízo por Cenário',
            color_discrete_map={
                '✅ Lucro': '#00cc96', 
                '❌ Prejuízo': '#ef553b', 
                '⚖️ Equilíbrio': '#636efa'
            }
        )
        st.plotly_chart(fig_profit, use_container_width=True)
    
    with col2:
        # Gráfico de ROI
        fig_roi = px.bar(
            df_all,
            x='Cenário',
            y='ROI',
            color='ROI',
            title='ROI por Cenário (%)',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_roi, use_container_width=True)
    
    # Tabela interativa detalhada
    st.subheader("📋 Detalhamento por Cenário")
    
    for scenario_name, result in scenario_details.items():
        with st.expander(f"🎯 {scenario_name} - {result['Status']} (ROI: {result['ROI']:.1f}%)", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Investimento", f"R$ {result['Investimento Total']:.2f}")
            with col2:
                st.metric("Retorno", f"R$ {result['Retorno Total']:.2f}")
            with col3:
                st.metric("Lucro/Prejuízo", f"R$ {result['Lucro/Prejuízo']:.2f}")
            with col4:
                st.metric("ROI", f"{result['ROI']:.1f}%")
            
            # Análise detalhada das apostas vencedoras
            if result['Apostas Vencedoras']:
                st.write("**✅ Apostas Vencedoras:**")
                for aposta in result['Apostas Vencedoras']:
                    investimento = st.session_state.app_state['investment_values'].get(aposta, 0)
                    odds = st.session_state.app_state['odds_values'].get(aposta, 1.0)
                    retorno = investimento * odds
                    st.write(f"- {aposta}: R$ {investimento:.2f} × {odds:.2f} = R$ {retorno:.2f}")
            else:
                st.write("**❌ Nenhuma aposta vencedora**")
            
            # Insights automáticos
            if result['Lucro/Prejuízo'] > 0:
                st.success(f"**Insight:** Este cenário é favorável. ROI de {result['ROI']:.1f}% indica boa estratégia.")
            elif result['Lucro/Prejuízo'] < -5:
                st.error(f"**Alerta:** Prejuízo significativo. Considere ajustar a estratégia para este cenário.")
    
    # Resumo executivo
    st.subheader("📊 Resumo Executivo")
    
    cenarios_lucrativos = sum(1 for r in scenario_details.values() if r['Lucro/Prejuízo'] > 0)
    cenarios_prejuizo = sum(1 for r in scenario_details.values() if r['Lucro/Prejuízo'] < 0)
    lucro_total_potencial = sum(max(0, r['Lucro/Prejuízo']) for r in scenario_details.values())
    prejuizo_total_potencial = sum(min(0, r['Lucro/Prejuízo']) for r in scenario_details.values())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cenários Lucrativos", f"{cenarios_lucrativos}/12", 
                 f"{cenarios_lucrativos/12*100:.1f}%")
    with col2:
        st.metric("Cenários com Prejuízo", f"{cenarios_prejuizo}/12",
                 f"{cenarios_prejuizo/12*100:.1f}%")
    with col3:
        st.metric("Lucro Potencial Total", f"R$ {lucro_total_potencial:.2f}")
    with col4:
        st.metric("Prejuízo Potencial Total", f"R$ {abs(prejuizo_total_potencial):.2f}")
    
    # Análise final de viabilidade
    if lucro_total_potencial > abs(prejuizo_total_potencial):
        st.success("🎯 **ESTRATÉGIA VIÁVEL**: O lucro potencial supera o prejuízo potencial.")
    else:
        st.warning("⚠️ **ATENÇÃO**: O prejuízo potencial supera o lucro potencial. Considere ajustes.")
    
    return scenario_profits

def render_odds_value_analysis():
    """Análise de valor das odds em tempo real"""
    st.markdown("### 🔍 Análise de Valor das Odds")
    
    # Coletar estatísticas básicas
    estatisticas = {
        'vitorias_favorito': 3,
        'gols_feitos_favorito': 8,
        'gols_sofridos_favorito': 3,
        'vitorias_azarao': 1,
        'gols_feitos_azarao': 4,
        'gols_sofridos_azarao': 10
    }
    
    analyzer = get_analyzer()
    analysis = analyzer.analisar_valor_odds(estatisticas)
    
    if analysis:
        analysis_data = []
        for mercado, dados in analysis.items():
            if dados['investimento'] > 0:
                analysis_data.append({
                    'Mercado': mercado,
                    'Investimento': dados['investimento'],
                    'Odds': dados['odds'],
                    'Prob. Real': dados['probabilidade_real'],
                    'Prob. Implícita': dados['probabilidade_implícita'],
                    'Valor': dados['valor_aposta'],
                    'Status': dados['status_valor']
                })
        
        if analysis_data:
            df_analysis = pd.DataFrame(analysis_data)
            
            # Aplicar formatação condicional
            def colorize_value(val):
                if val > 5:
                    return 'color: green; font-weight: bold'
                elif val < -5:
                    return 'color: red; font-weight: bold'
                else:
                    return 'color: orange'
            
            st.dataframe(
                df_analysis.style.format({
                    'Investimento': 'R$ {:.2f}',
                    'Odds': '{:.2f}',
                    'Prob. Real': '{:.1f}%',
                    'Prob. Implícita': '{:.1f}%',
                    'Valor': '{:.1f}%'
                }).applymap(colorize_value, subset=['Valor']),
                use_container_width=True
            )

# --- SISTEMA DE PROMPT INTELIGENTE APRIMORADO ---
def render_prompt_generator():
    st.header("🤖 Assistente de Análise com IA")
    
    # Coletar informações contextuais
    st.subheader("1. 📋 Contexto da Partida")
    
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
    st.subheader("2. 📊 Estatísticas dos Times")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏆 Favorito (Casa)**")
        vit_fav = st.slider("Vitórias últimos 5 jogos", 0, 5, 3, key="vit_fav")
        gols_fav_f = st.slider("Gols marcados últimos 5", 0, 20, 8, key="gols_fav_f")
        gols_fav_s = st.slider("Gols sofridos últimos 5", 0, 15, 3, key="gols_fav_s")
    
    with col2:
        st.markdown("**⚽ Azarão (Fora)**")
        vit_aza = st.slider("Vitórias últimos 5 jogos", 0, 5, 1, key="vit_aza")
        gols_aza_f = st.slider("Gols marcados últimos 5", 0, 15, 4, key="gols_aza_f")
        gols_aza_s = st.slider("Gols sofridos últimos 5", 0, 20, 10, key="gols_aza_s")
    
    # Análise técnica
    st.subheader("3. 🧠 Análise Técnica")
    
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
    st.subheader("4. 💡 Informações Adicionais")
    
    info_extra = st.text_area("Observações, notícias, lesões, ou fatores relevantes:",
                             placeholder="Ex: Jogador-chave lesionado, treinador novo, situação do elenco...",
                             height=100)
    
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

# --- FUNÇÃO PRINCIPAL ---
def main():
    st.set_page_config(
        page_title="Analisador Inteligente de Apostas",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # INICIALIZAR O ESTADO PRIMEIRO
    init_state()
        
    st.title("🎯 Analisador Inteligente de Apostas")
    st.markdown("Sistema integrado de análise probabilística, value betting e gestão de risco")
    
    # Sistema de abas principal
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚙️ Configuração Principal", 
        "📈 Análise de Cenários", 
        "🤖 Assistente de IA", 
        "🛡️ Hedge Dinâmico"
    ])

    with tab1:
        render_controls()

    with tab2:
        scenario_profits = render_scenario_analysis()

    with tab3:
        render_prompt_generator()

    with tab4:
        st.header("🛡️ Módulo de Hedge Dinâmico")
        if dinamico_available:
            # =============================================
            # 🔄 SISTEMA DE CONTINUIDADE DE OPERAÇÕES
            # =============================================
            
            # Verificar se há operação em andamento
            if st.session_state.get('current_operation_id'):
                operation_info = get_current_operation_info()
                if operation_info:
                    st.success(f"🔄 **OPERAÇÃO ATIVA:** {operation_info['operation_id']}")
                    
                    # Mostrar resumo da operação atual
                    with st.expander("📋 Resumo da Operação Ativa", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Status", operation_info['status'])
                        with col2:
                            st.metric("Investimento Total", f"R$ {operation_info['total_investment']:.2f}")
                        with col3:
                            st.metric("Lucro Esperado", f"R$ {operation_info['expected_profit']:.2f}")
                        
                        if operation_info['ia_analysis']:
                            st.write(f"**Perfil IA:** {operation_info['ia_analysis']['profile']}")
                            st.write(f"**Estratégia:** {operation_info['ia_analysis']['strategy']}")
            
            # Seção para continuar operação específica
            with st.expander("🔍 Continuar Operação Existente", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    operation_id = st.text_input(
                        "ID da Operação:",
                        placeholder="Ex: OP_20250922_203750",
                        key="continue_operation_id"
                    )
                
                with col2:
                    st.write("")  # Espaçamento
                    if st.button("🔄 Carregar Operação", use_container_width=True):
                        if operation_id:
                            if continue_operation_from_id(operation_id):
                                st.success(f"✅ Operação **{operation_id}** carregada com sucesso!")
                                st.rerun()
                            else:
                                st.error("❌ Operação não encontrada. Verifique o ID.")
                        else:
                            st.warning("⚠️ Digite um ID de operação válido")
            
            # Mostrar histórico rápido de operações recentes
            if dinamico_available and hasattr(st.session_state.hedge_manager, 'memory_manager'):
                operations = st.session_state.hedge_manager.memory_manager.get_operation_history()
                if operations:
                    with st.expander("📚 Operações Recentes", expanded=False):
                        st.write("**Clique em um ID para continuar:**")
                        for op in operations[:3]:  # Últimas 3 operações
                            if st.button(f"📅 {op.operation_id} - {op.timestamp.strftime('%H:%M:%S')}", 
                                       key=f"op_btn_{op.operation_id}"):
                                if continue_operation_from_id(op.operation_id):
                                    st.success(f"Operação {op.operation_id} carregada!")
                                    st.rerun()
            
            # =============================================
            # 📊 ANÁLISE PRINCIPAL DE HEDGE
            # =============================================
            
            st.markdown("---")
            st.subheader("📈 Análise de Cenários para Hedge")
            
            zero_profit = scenario_profits.get('0x0', 0.0)
            fav_profit = scenario_profits.get('1x1 FAV 1º', 0.0)
            aza_profit = scenario_profits.get('1x1 AZA 1º', 0.0)
            
            # Mostrar métricas dos cenários
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Lucro 0x0", f"R$ {zero_profit:.2f}", 
                         delta_color="normal" if zero_profit > 0 else "inverse")
            with col2:
                st.metric("Lucro 1x1 FAV", f"R$ {fav_profit:.2f}", 
                         delta_color="normal" if fav_profit > 0 else "inverse")
            with col3:
                st.metric("Lucro 1x1 AZA", f"R$ {aza_profit:.2f}", 
                         delta_color="normal" if aza_profit > 0 else "inverse")
            
            st.info(f"**Referências para Hedge:** 0x0: R$ {zero_profit:.2f} | 1x1 FAV: R$ {fav_profit:.2f} | 1x1 AZA: R$ {aza_profit:.2f}")
            
            odds_values = st.session_state.app_state.get('odds_values', {})
            
            # =============================================
            # 🎯 CONTROLES DE HEDGE DINÂMICO
            # =============================================
            
            # Se houver operação ativa, mostrar opções de gerenciamento
            if st.session_state.get('hedge_applied', False) and st.session_state.get('current_operation_id'):
                st.markdown("### ⚙️ Gerenciamento da Operação Ativa")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📊 Atualizar Análise", use_container_width=True):
                        st.info("🔄 Atualizando análise com dados atuais...")
                        st.rerun()
                
                with col2:
                    if st.button("✏️ Modificar Estratégia", use_container_width=True):
                        st.session_state.hedge_applied = False
                        st.success("✅ Modo de edição ativado!")
                        st.rerun()
                
                with col3:
                    if st.button("🆕 Nova Operação", use_container_width=True):
                        st.session_state.hedge_applied = False
                        st.session_state.current_operation_id = None
                        st.success("✅ Pronto para iniciar nova operação!")
                        st.rerun()
            
            # Renderizar controles principais de hedge
            render_hedge_controls(zero_profit, fav_profit, aza_profit, odds_values)
            
            # Mostrar resultados se houver operação aplicada
            if st.session_state.get('hedge_applied', False):
                render_hedge_results()
                
        else:
            st.warning("Módulo de Hedge Dinâmico não disponível.")

if __name__ == "__main__":
    main()
