# ao_vivo.py (versão corrigida)
import streamlit as st
import pandas as pd
import plotly.express as px
from enum import Enum
from dataclasses import dataclass
from typing import Dict
import json
import sys
import os

# Adiciona o diretório atual ao path para importar o módulo dinamico
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa o módulo dinamico
try:
    from dinamico import DynamicHedgeManager, RedistributionStrategy, HedgeBet, init_hedge_state, render_hedge_controls, render_hedge_results
    dinamico_available = True
except ImportError as e:
    st.error(f"Módulo dinamico não pôde ser carregado: {e}")
    dinamico_available = False

# Definindo tipos de apostas
class BetType(Enum):
    OVER_15_BOTH_NO = "Mais 1.5 & Ambas Não"
    EXACT_0_0 = "Resultado 0x0"
    UNDER_25_BOTH_NO = "Menos 2.5 & Dupla Chance 1X"
    DOUBLE_CHANCE_X2 = "Dupla Chance X2"
    NEXT_GOAL_FAV = "Próximo Gol Favorito"
    OVER_15 = "Mais 1.5 Gols"
    BOTH_YES = "Ambas Sim & Dupla Chance"   # 🔄 atualizado
    UNDER_15 = "Menos 1.5 Gols"

@dataclass
class Bet:
    bet_type: BetType
    investment: float
    odds: float

    @property
    def potential_return(self) -> float:
        """Retorno sempre atualizado (investment * odds)"""
        return self.investment * self.odds

class BettingStrategyAnalyzer:
    def __init__(self):
        self.bets: Dict[BetType, Bet] = {}
        
    def update_bet(self, bet_type: BetType, investment: float, odds: float):
        self.bets[bet_type] = Bet(bet_type, investment, odds)

    def get_total_investment(self) -> float:
        return sum(bet.investment for bet in self.bets.values())
        
    def calculate_scenario_profit(self, home_goals: int, away_goals: int, first_goal_by_fav: bool = None) -> Dict[str, float]:
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
            # <-- lógica alterada: agora exige total < 2.5 E dupla chance Favorito/Empate (1X) -->
            elif bet_type == BetType.UNDER_25_BOTH_NO:
                # ganha quando total < 2.5 e o resultado é Favorito OU Empate (1X)
                wins = (total_goals < 2.5) and (home_goals >= away_goals)
            elif bet_type == BetType.DOUBLE_CHANCE_X2:
                wins = (home_goals == away_goals) or (away_goals > home_goals)
            elif bet_type == BetType.NEXT_GOAL_FAV:
                if first_goal_by_fav is not None:
                    wins = first_goal_by_fav
            elif bet_type == BetType.OVER_15:
                wins = total_goals > 1.5
            elif bet_type == BetType.BOTH_YES:
                # Agora protege apenas se ambos marcam E não termina empatado
                wins = both_scored and (home_goals != away_goals)
            elif bet_type == BetType.UNDER_15:
                wins = (total_goals < 1.5)
            
            if wins:
                total_return += bet.potential_return
                winning_bets.append(bet_type.value)
        
        profit = total_return - total_investment_all
        
        return {
            'Retorno Total': total_return,
            'Investimento Total': total_investment_all,
            'Lucro/Prejuízo': profit,
            'Apostas Vencedoras': winning_bets,
            'Status': '✅ Lucro' if profit > 0 else '❌ Prejuízo' if profit < 0 else '⚖️ Equilíbrio'
        }

def init_state():
    if 'app_state' not in st.session_state:
        # Odds definidas pelo usuário (atualize o label aqui também)
        default_odds = {
            "Mais 1.5 & Ambas Não": 6.50,
            "Resultado 0x0": 7.89,
            "Menos 2.5 & Dupla Chance 1X": 1.85,
            "Dupla Chance X2": 1.91,
            "Próximo Gol Favorito": 1.91,
            "Mais 1.5 Gols": 1.30,
            "Ambas Sim & Dupla Chance": 1.95,   # 🔄 atualizado
            "Menos 1.5 Gols": 3.25
        }

        default_investments = {
            "Mais 1.5 & Ambas Não": 1.50,
            "Resultado 0x0": 0.00,
            "Menos 2.5 & Dupla Chance 1X": 0.00,
            "Dupla Chance X2": 3.00,
            "Próximo Gol Favorito": 3.00,
            "Mais 1.5 Gols": 0.00,
            "Ambas Sim & Dupla Chance": 0.00,   # 🔄 atualizado
            "Menos 1.5 Gols": 3.00
        }
        
        # Banco inicial exato
        initial_bankroll = 10.50
        
        # Proporções automáticas (investimento relativo ao banco)
        default_proportions = {
            bet_type: (default_investments[bet_type] / initial_bankroll 
                       if initial_bankroll > 0 else 0)
            for bet_type in default_investments
        }
        
        st.session_state.app_state = {
            'odds_values': default_odds,
            'investment_values': default_investments,
            'investment_proportions': default_proportions,
            'total_bankroll': initial_bankroll,
            'selected_scenarios': [],
            'distribution_applied': True,
            'initial_setup': True
        }
        
    # Inicializa o estado do módulo dinâmico se disponível
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

# Atualiza investimentos baseado nas proporções quando o bankroll muda
def update_investments_from_proportions():
    total_bankroll = st.session_state.app_state['total_bankroll']
    proportions = st.session_state.app_state['investment_proportions']
    
    for bet_type in BetType:
        st.session_state.app_state['investment_values'][bet_type.value] = total_bankroll * proportions[bet_type.value]

# Atualiza proporções quando investimentos individuais são modificados
def update_proportions_from_investments():
    total_investment = sum(st.session_state.app_state['investment_values'].values())
    
    if total_investment > 0:
        for bet_type in BetType:
            investment = st.session_state.app_state['investment_values'][bet_type.value]
            st.session_state.app_state['investment_proportions'][bet_type.value] = investment / total_investment

def render_controls():
    # Verifica se precisa sincronizar os widgets
    if st.session_state.app_state.get('needs_sync', False):
        st.session_state.app_state['needs_sync'] = False
        st.rerun()
    
    st.subheader("⚙️ Configuração de Odds e Investimentos")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    # --- Coluna 1: Odds ---
    with col1:
        st.markdown("**🎯 Configuração de Odds**")
        for bet_type in BetType:
            current_odds = st.session_state.app_state['odds_values'][bet_type.value]
            key_odds = f"odds_{bet_type.name}"
            
            new_odds = st.number_input(
                f"{bet_type.value} - Odds",
                min_value=1.01,
                value=float(current_odds),
                step=0.01,
                key=key_odds
            )
            
            if new_odds != current_odds:
                st.session_state.app_state['odds_values'][bet_type.value] = float(new_odds)

    # --- Coluna 2: Investimentos ---
    with col2:
        st.markdown("**📊 Controle de Investimentos**")
        for bet_type in BetType:
            current_investment = st.session_state.app_state['investment_values'][bet_type.value]
            key_inv = f"inv_{bet_type.name}"
            
            new_investment = st.number_input(
                f"{bet_type.value} - Investimento (R$)",
                min_value=0.0,
                max_value=100.0,
                value=float(current_investment),
                step=0.01,
                key=key_inv
            )
            
            if new_investment != current_investment:
                st.session_state.app_state['investment_values'][bet_type.value] = float(new_investment)
                update_proportions_from_investments()
                st.session_state.app_state['total_bankroll'] = sum(
                    st.session_state.app_state['investment_values'].values()
                )
                st.session_state.app_state['distribution_applied'] = False

    with col3:
        st.markdown("**💰 Banco Total**")
        total_bankroll = st.number_input(
            "Valor Total (R$)",
            min_value=0.0,
            max_value=1000.0,
            value=st.session_state.app_state['total_bankroll'],
            step=1.0,
            key="total_bankroll"
        )

        if total_bankroll != st.session_state.app_state['total_bankroll']:
            # Atualiza bankroll âncora
            st.session_state.app_state['total_bankroll'] = total_bankroll

            # Recalcula investimentos proporcionais
            update_investments_from_proportions()

            # Marca para sincronizar na próxima renderização
            st.session_state.app_state['needs_sync'] = True
            st.session_state.app_state['distribution_applied'] = True
            st.rerun()

        if st.button("🔄 Distribuir Proporcionalmente"):
            update_investments_from_proportions()
            st.session_state.app_state['distribution_applied'] = True
            st.session_state.app_state['needs_sync'] = True
            st.rerun()

# Distribuição automática baseada em cenários (33% para cada cenário)
def apply_scenario_based_distribution(selected_scenarios):
    """Aplica distribuição automática baseada nos cenários selecionados - 33% para cada cenário"""
    total_bankroll = st.session_state.app_state['total_bankroll']
    
    # Define novas proporções baseadas nos cenários
    new_proportions = {
        "Mais 1.5 & Ambas Não": 0.0,
        "Resultado 0x0": 0.0,
        "Menos 2.5 & Ambas Não": 0.0,
        "Dupla Chance X2": 0.0,
        "Próximo Gol Favorito": 0.0,
        "Mais 1.5 Gols": 0.0,
        "Ambas Sim": 0.0,
        "Menos 1.5 Gols": 0.0
    }
    
    # Calcula o valor de 33% do bankroll total
    scenario_allocation = total_bankroll * 0.33
    
    # Aplica pesos baseados nos cenários selecionados
    for scenario in selected_scenarios:
        if scenario in ["1x0 FAV", "0x1 AZA"]:
            # Distribui 33% igualmente entre: Menos 1.5, Próximo Gol Favorito e Dupla Chance
            allocation_per_bet = scenario_allocation / 3
            
            new_proportions[BetType.UNDER_15.value] += allocation_per_bet
            new_proportions[BetType.NEXT_GOAL_FAV.value] += allocation_per_bet
            new_proportions[BetType.DOUBLE_CHANCE_X2.value] += allocation_per_bet
                
        elif scenario in ["2x0 FAV", "0x2 AZA"]:
            # Agora cobre também com Mais 1.5 & Ambas Não
            allocation_per_bet = scenario_allocation / 3
            
            new_proportions[BetType.OVER_15_BOTH_NO.value] += allocation_per_bet
            new_proportions[BetType.OVER_15.value] += allocation_per_bet
            
            if "FAV" in scenario:
                new_proportions[BetType.NEXT_GOAL_FAV.value] += allocation_per_bet
            else:
                new_proportions[BetType.DOUBLE_CHANCE_X2.value] += allocation_per_bet
                
        elif scenario in ["1x1 FAV 1º", "1x1 AZA 1º", "2x2"]:
            # Distribui 33% igualmente entre: Ambas Sim, Dupla Chance, Próximo Gol Favorito
            allocation_per_bet = scenario_allocation / 3
            
            new_proportions[BetType.BOTH_YES.value] += allocation_per_bet
            new_proportions[BetType.DOUBLE_CHANCE_X2.value] += allocation_per_bet
            new_proportions[BetType.NEXT_GOAL_FAV.value] += allocation_per_bet
    
    # Converte valores absolutos em proporções
    total_allocated = sum(new_proportions.values())
    if total_allocated > 0:
        for bet_type in new_proportions:
            new_proportions[bet_type] = new_proportions[bet_type] / total_bankroll
    
    # Garante que a soma das proporções seja 1 (100%)
    proportion_sum = sum(new_proportions.values())
    if proportion_sum < 1.0:
        # Distribui o restante proporcionalmente entre as outras apostas
        remaining_proportion = 1.0 - proportion_sum
        num_other_bets = len([p for p in new_proportions.values() if p == 0])
        if num_other_bets > 0:
            for bet_type in new_proportions:
                if new_proportions[bet_type] == 0:
                    new_proportions[bet_type] = remaining_proportion / num_other_bets
    
    # Atualiza as proporções e investimentos
    st.session_state.app_state['investment_proportions'] = new_proportions
    update_investments_from_proportions()

def render_action_buttons(df_all: pd.DataFrame):
    st.subheader("⚡ Ações")

    col1, col2, col3 = st.columns(3)

    # --- Botão 1: Próxima Etapa ---
    with col1:
        if st.button("➡️ Próxima Etapa"):
            st.session_state["next_step_ready"] = True
            st.success("Próxima etapa pronta para carregar!")

    # --- Botão 2: Salvar Operação ---
    with col2:
        if st.button("💾 Salvar Operação"):
            # Salva odds e investimentos em JSON
            save_data = {
                "odds_values": st.session_state.app_state['odds_values'],
                "investment_values": st.session_state.app_state['investment_values'],
                "total_bankroll": st.session_state.app_state['total_bankroll']
            }
            with open("operacao_salva.json", "w") as f:
                json.dump(save_data, f, indent=4)
            st.success("Operação salva em 'operacao_salva.json' ✅")

    # --- Botão 3: Destacar Aplicações ---
    with col3:
        if st.button("🌟 Destacar Aplicações"):
            df_highlight = df_all.copy()
            # Marca apostas com valor aplicado
            active_bets = {
                k: v for k, v in st.session_state.app_state['investment_values'].items() if v > 0
            }
            st.write("### 📌 Apostas Ativas")
            st.json(active_bets)

def render_scenario_analysis():
    st.subheader("📊 Análise de Todos os Cenários")
    
    analyzer = get_analyzer()
    
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
    scenario_profits = {}  # Armazena lucros por cenário
    
    for scenario_name, home_goals, away_goals, first_goal in important_scenarios:
        result = analyzer.calculate_scenario_profit(home_goals, away_goals, first_goal)
        scenario_data = {
            'Cenário': scenario_name,
            'Placar': f"{home_goals}x{away_goals}",
            '1º Gol': 'FAV' if first_goal is True else 'AZA' if first_goal is False else '-',
            'Retorno Total': result['Retorno Total'],
            'Investimento Total': result['Investimento Total'],
            'Lucro/Prejuízo': result['Lucro/Prejuízo'],
            'Status': result['Status'],
            'Apostas Vencedoras': ', '.join(result['Apostas Vencedoras']) if result['Apostas Vencedoras'] else 'Nenhuma'
        }
        
        all_scenario_data.append(scenario_data)
        scenario_profits[scenario_name] = result['Lucro/Prejuízo']
    
    df_all = pd.DataFrame(all_scenario_data)
    
    # Gráfico
    fig = px.bar(
        df_all, 
        x='Cenário', 
        y='Lucro/Prejuízo', 
        color='Status',
        title='Lucro/Prejuízo por Cenário',
        color_discrete_map={'✅ Lucro': 'green', '❌ Prejuízo': 'red', '⚖️ Equilíbrio': 'gray'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela
    st.dataframe(
        df_all.style.format({
            'Retorno Total': 'R$ {:.2f}',
            'Investimento Total': 'R$ {:.2f}',
            'Lucro/Prejuízo': 'R$ {:.2f}'
        }).map(
            lambda x: 'background-color: #ffcccc' if 'Prejuízo' in str(x) else 'background-color: #ccffcc' if 'Lucro' in str(x) else '',
            subset=['Status']
        ),
        use_container_width=True,
        hide_index=True
    )

    # --- Botões extras ---
    render_action_buttons(df_all)
    
    # --- Módulo Dinâmico ---
    if dinamico_available:
        st.divider()
        st.subheader("🛡️ Módulo de Hedge Dinâmico")
        
        # Obtém os lucros específicos dos cenários 0x0 e 1x1
        zero_profit = scenario_profits.get('0x0', 0.0)
        fav_profit  = scenario_profits.get('1x1 FAV 1º', 0.0)
        aza_profit  = scenario_profits.get('1x1 AZA 1º', 0.0)
        
        st.info(f"Referências: 0x0 R$ {zero_profit:.2f} | 1x1 FAV R$ {fav_profit:.2f} | 1x1 AZA R$ {aza_profit:.2f}")
        
        # Passa as odds para o módulo dinâmico (pegar do app_state)
        odds_values = st.session_state.app_state.get('odds_values', {})
        st.session_state.odds_values = odds_values
        
        # Renderiza os controles do módulo dinâmico (ordem correta de argumentos)
        # assinatura esperada: render_hedge_controls(zero_profit, fav_profit, aza_profit, odds_values)
        render_hedge_controls(zero_profit, fav_profit, aza_profit, st.session_state.app_state.get('odds_values', {}))
        
        # Renderiza os resultados se aplicado
        if st.session_state.get('hedge_applied', False):
            render_hedge_results()
    else:
        st.warning("Módulo dinâmico não disponível. Verifique se o arquivo dinamico.py está no mesmo diretório.")

def main():
    st.set_page_config(
        page_title="Analisador de Estratégia de Apostas",
        page_icon="🎯",
        layout="wide"
    )
    
    init_state()
    
    st.title("🎯 Analisador de Estratégia de Apostas")
    
    # Controles centralizados
    render_controls()
    
    # Análise de cenários
    render_scenario_analysis()

if __name__ == "__main__":
    main()
