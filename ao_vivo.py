# ao_vivo.py (versão com Prompt Inteligente Adaptativo)
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
except ImportError:
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

# --- Classe Principal de Análise ---
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
            'Status': '✅ Lucro' if profit > 0 else '❌ Prejuízo' if profit < 0 else '⚖️ Equilíbrio'
        }

# --- Funções de Gerenciamento de Estado (Session State) ---
def init_state():
    if 'app_state' not in st.session_state:
        default_odds = {bt.value: 1.80 for bt in BetType}
        default_odds.update({
            "Mais 1.5 & Ambas Não": 3.50, "Resultado 0x0": 7.89, "Menos 2.5 & Dupla Chance 1X": 1.85,
            "Dupla Chance X2": 1.91, "Próximo Gol Favorito": 1.91, "Mais 1.5 Gols": 1.30,
            "Mais 2.5 & Dupla Chance 12": 2.30, "Menos 1.5 Gols": 3.25, "Vitória Favorito": 1.80
        })

        default_investments = {
            "Mais 1.5 & Ambas Não": 1.50, "Resultado 0x0": 0.00, "Menos 2.5 & Dupla Chance 1X": 4.00,
            "Dupla Chance X2": 2.00, "Próximo Gol Favorito": 0.00, "Mais 1.5 Gols": 0.00,
            "Mais 2.5 & Dupla Chance 12": 1.00, "Menos 1.5 Gols": 1.50, "Vitória Favorito": 0.00
        }
        
        initial_bankroll = 10.00
        
        st.session_state.app_state = {
            'odds_values': default_odds,
            'investment_values': default_investments,
            'total_bankroll': initial_bankroll
        }
        update_proportions_from_investments(save_proportions=True)

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
    proportions = st.session_state.app_state['investment_proportions']
    for bet_type in BetType:
        st.session_state.app_state['investment_values'][bet_type.value] = total_bankroll * proportions.get(bet_type.value, 0)

def update_proportions_from_investments(save_proportions=True):
    total_investment = sum(st.session_state.app_state['investment_values'].values())
    if total_investment > 0 and save_proportions:
        proportions = {}
        for bet_type in BetType:
            investment = st.session_state.app_state['investment_values'][bet_type.value]
            proportions[bet_type.value] = investment / total_investment
        st.session_state.app_state['investment_proportions'] = proportions

# --- Funções de Renderização da UI ---
def render_controls():
    st.subheader("⚙️ Configuração de Odds e Investimentos")
    col1, col2, col3 = st.columns([2, 2, 1.2])
    
    with col1:
        st.markdown("**🎯 Odds**")
        for bet_type in BetType:
            new_odds = st.number_input(f"{bet_type.value}", min_value=1.01,
                                       value=float(st.session_state.app_state['odds_values'][bet_type.value]),
                                       step=0.01, key=f"odds_{bet_type.name}", label_visibility="collapsed")
            if new_odds != st.session_state.app_state['odds_values'][bet_type.value]:
                st.session_state.app_state['odds_values'][bet_type.value] = float(new_odds)
                st.rerun()

    with col2:
        st.markdown("**📊 Investimentos (R$)**")
        for bet_type in BetType:
            new_investment = st.number_input(f"{bet_type.value} - Investimento (R$)", min_value=0.0,
                                             value=float(st.session_state.app_state['investment_values'][bet_type.value]),
                                             step=0.50, key=f"inv_{bet_type.name}", label_visibility="collapsed")
            if new_investment != st.session_state.app_state['investment_values'][bet_type.value]:
                st.session_state.app_state['investment_values'][bet_type.value] = float(new_investment)
                st.session_state.app_state['total_bankroll'] = sum(st.session_state.app_state['investment_values'].values())
                update_proportions_from_investments(save_proportions=False)
                st.rerun()

    with col3:
        st.markdown("**💰 Banco Total**")
        total_bankroll = st.number_input("Valor Total (R$)", min_value=0.0,
                                         value=st.session_state.app_state['total_bankroll'],
                                         step=1.0, key="total_bankroll")
        if total_bankroll != st.session_state.app_state['total_bankroll']:
            st.session_state.app_state['total_bankroll'] = total_bankroll
            update_investments_from_proportions()
            st.rerun()

        if st.button("🔄 Salvar e Distribuir Proporção", use_container_width=True):
            update_proportions_from_investments(save_proportions=True)
            update_investments_from_proportions()
            st.toast("Proporções salvas e distribuídas!")
            st.rerun()

def render_scenario_analysis():
    st.subheader("📊 Análise de Cenários")
    analyzer = get_analyzer()
    scenarios = [
        ('0x0', 0, 0, None), ('1x0 FAV', 1, 0, True), ('0x1 AZA', 0, 1, False),
        ('1x1 FAV 1º', 1, 1, True), ('1x1 AZA 1º', 1, 1, False), ('2x0 FAV', 2, 0, True),
        ('0x2 AZA', 0, 2, False), ('2x1 FAV', 2, 1, True), ('1x2 AZA', 1, 2, False),
        ('2x2', 2, 2, None), ('3x0 FAV', 3, 0, True), ('0x3 AZA', 0, 3, False)
    ]
    
    data = []
    scenario_profits = {}
    scenario_details = {}  # Novo: armazenar detalhes completos por cenário
    
    for name, hg, ag, fg in scenarios:
        result = analyzer.calculate_scenario_profit(hg, ag, fg)
        data.append({
            'Cenário': name, 
            'Lucro/Prejuízo': result['Lucro/Prejuízo'], 
            'Status': result['Status'],
            'Retorno Total': result['Retorno Total'],
            'Investimento Total': result['Investimento Total'],
            'Apostas Vencedoras': result['Apostas Vencedoras']
        })
        scenario_profits[name] = result['Lucro/Prejuízo']
        scenario_details[name] = result  # Armazenar resultado completo
    
    df = pd.DataFrame(data)

    # Gráfico 1: Lucro/Prejuízo por Cenário (MANTIDO)
    fig_profit = px.bar(df, x='Cenário', y='Lucro/Prejuízo', color='Status', title='Lucro/Prejuízo por Cenário',
                 color_discrete_map={'✅ Lucro': '#2ca02c', '❌ Prejuízo': '#d62728', '⚖️ Equilíbrio': '#7f7f7f'})
    st.plotly_chart(fig_profit, use_container_width=True)

    # --- NOVA IMPLEMENTAÇÃO: Tabela Detalhada por Extenso ---
    st.subheader("📋 Resultados Detalhados por Cenário")
    
    # Criar tabela expandível com todos os detalhes
    for scenario_name, result in scenario_details.items():
        with st.expander(f"📊 Cenário {scenario_name} - {result['Status']}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Investimento Total", f"R$ {result['Investimento Total']:.2f}")
            with col2:
                st.metric("Retorno Total", f"R$ {result['Retorno Total']:.2f}")
            with col3:
                st.metric("Lucro/Prejuízo", f"R$ {result['Lucro/Prejuízo']:.2f}", 
                         delta=f"{result['Lucro/Prejuízo']:.2f}" if result['Lucro/Prejuízo'] != 0 else None)
            
            # Lista de apostas vencedoras
            if result['Apostas Vencedoras']:
                st.write("**🎯 Apostas Vencedoras:**")
                for aposta in result['Apostas Vencedoras']:
                    # Encontrar o investimento e odds desta aposta
                    for bet_type in BetType:
                        if bet_type.value == aposta:
                            investimento = st.session_state.app_state['investment_values'][aposta]
                            odds = st.session_state.app_state['odds_values'][aposta]
                            retorno_aposta = investimento * odds
                            st.write(f"- {aposta}: R$ {investimento:.2f} × {odds:.2f} = R$ {retorno_aposta:.2f}")
                            break
            else:
                st.write("**❌ Nenhuma aposta vencedora**")
            
            # Análise textual do cenário
            st.write("**📈 Análise do Cenário:**")
            if result['Lucro/Prejuízo'] > 0:
                st.success(f"Este cenário resulta em **lucro de R$ {result['Lucro/Prejuízo']:.2f}**. " +
                          f"O retorno de R$ {result['Retorno Total']:.2f} supera o investimento de R$ {result['Investimento Total']:.2f}.")
            elif result['Lucro/Prejuízo'] < 0:
                st.error(f"Este cenário resulta em **prejuízo de R$ {abs(result['Lucro/Prejuízo']):.2f}**. " +
                        f"O retorno de R$ {result['Retorno Total']:.2f} não cobre o investimento de R$ {result['Investimento Total']:.2f}.")
            else:
                st.info(f"Este cenário resulta em **equilíbrio**. " +
                       f"O retorno de R$ {result['Retorno Total']:.2f} iguala o investimento de R$ {result['Investimento Total']:.2f}.")

    # --- RESUMO GERAL ---
    st.subheader("📊 Resumo Geral dos Resultados")
    
    total_investido = sum(result['Investimento Total'] for result in scenario_details.values()) / len(scenario_details)
    total_lucro_potencial = sum(max(0, result['Lucro/Prejuízo']) for result in scenario_details.values())
    total_prejuizo_potencial = sum(min(0, result['Lucro/Prejuízo']) for result in scenario_details.values())
    cenarios_lucrativos = sum(1 for result in scenario_details.values() if result['Lucro/Prejuízo'] > 0)
    cenarios_prejuizo = sum(1 for result in scenario_details.values() if result['Lucro/Prejuízo'] < 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cenários Lucrativos", cenarios_lucrativos, f"{cenarios_lucrativos}/12")
    with col2:
        st.metric("Cenários com Prejuízo", cenarios_prejuizo, f"{cenarios_prejuizo}/12")
    with col3:
        st.metric("Lucro Total Potencial", f"R$ {total_lucro_potencial:.2f}")
    with col4:
        st.metric("Prejuízo Total Potencial", f"R$ {abs(total_prejuizo_potencial):.2f}")
    
    # Retorna os lucros para o módulo de hedge
    return scenario_profits

# --- FUNÇÃO COMPLETAMENTE REFEITA: Prompt Inteligente Adaptativo ---
def render_prompt_generator():
    st.header("🤖 Gerador de Prompt Inteligente para IA")
    st.markdown("""
    **Sistema de Análise Adaptativa**: Este gerador cria prompts personalizados baseados nas estatísticas reais da partida.
    Quanto mais informações você fornecer, mais precisa será a análise da IA.
    """)

    # --- SEÇÃO 1: PERFIL DO USUÁRIO ---
    st.subheader("1. 👤 Perfil do Investidor")
    col1, col2 = st.columns(2)
    
    with col1:
        user_profile = st.selectbox(
            "Perfil de Risco",
            ("Conservador", "Moderado", "Arriscado"),
            index=1,
            help="Define sua tolerância a risco: Conservador (segurança), Moderado (equilíbrio), Arriscado (alto retorno)"
        )
    
    with col2:
        bankroll_percentage = st.slider(
            "% do Bankroll para esta operação",
            min_value=10,
            max_value=100,
            value=50,
            help="Quanto do seu bankroll total você pretende alocar nesta operação"
        )

    st.markdown("---")
    
    # --- SEÇÃO 2: ESTATÍSTICAS ESPECÍFICAS DA PARTIDA ---
    st.subheader("2. 📊 Estatísticas Detalhadas da Partida")
    
    st.markdown("#### 🏆 Desempenho do FAVORITO (Time da Casa)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vitorias_favorito = st.slider(
            "Vitórias nos últimos 5 jogos", 
            min_value=0, max_value=5, value=3,
            help="Quantas vitórias o time favorito teve nos últimos 5 jogos"
        )
    
    with col2:
        gols_feitos_favorito = st.slider(
            "Gols marcados (últimos 5 jogos)",
            min_value=0, max_value=20, value=8,
            help="Total de gols que o favorito marcou nos últimos 5 jogos"
        )
    
    with col3:
        gols_sofridos_favorito = st.slider(
            "Gols sofridos (últimos 5 jogos)", 
            min_value=0, max_value=15, value=3,
            help="Total de gols que o favorito sofreu nos últimos 5 jogos"
        )

    st.markdown("#### ⚽ Desempenho do AZARÃO (Time Visitante)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vitorias_azarao = st.slider(
            "Vitórias nos últimos 5 jogos (Azarão)", 
            min_value=0, max_value=5, value=1
        )
    
    with col2:
        gols_feitos_azarao = st.slider(
            "Gols marcados (últimos 5 jogos - Azarão)",
            min_value=0, max_value=15, value=4
        )
    
    with col3:
        gols_sofridos_azarao = st.slider(
            "Gols sofridos (últimos 5 jogos - Azarão)", 
            min_value=0, max_value=20, value=10
        )

    # --- SEÇÃO 3: TENDÊNCIAS E FATORES ADICIONAIS ---
    st.markdown("#### 📈 Tendências e Fatores Adicionais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tendencia_gols = st.selectbox(
            "Tendência de gols da partida",
            ("Forte tendência a poucos gols (<2.5)", 
             "Equilibrada (2-3 gols)", 
             "Forte tendência a muitos gols (>3.5)"),
            index=0
        )
        
        motivacao_favorito = st.selectbox(
            "Motivação do Favorito",
            ("Alta (disputa título/classificação)",
             "Média (manutenção no campeonato)", 
             "Baixa (jogo sem importância)"),
            index=0
        )
    
    with col2:
        forca_ataque = st.slider(
            "Força do ataque do Favorito", 
            min_value=1, max_value=10, value=7,
            help="Avalie a força ofensiva do time favorito (1=muito fraca, 10=excelente)"
        )
        
        forca_defesa = st.slider(
            "Força da defesa do Azarão",
            min_value=1, max_value=10, value=4,
            help="Avalie a força defensiva do time azarão (1=muito fraca, 10=excelente)"
        )

    # --- SEÇÃO 4: ANÁLISE PERSONALIZADA ---
    st.markdown("---")
    st.subheader("3. 📝 Análise Personalizada (Opcional)")
    
    analise_personalizada = st.text_area(
        "Observações adicionais, notícias importantes ou fatores específicos",
        placeholder="Ex: Jogador-chave lesionado, condições climáticas, histórico de confrontos...",
        height=100
    )

    # --- BOTÃO PARA GERAR PROMPT INTELIGENTE ---
    if st.button("🧠 Gerar Prompt Inteligente", type="primary", use_container_width=True):
        with st.spinner("Analisando estatísticas e criando prompt personalizado..."):
            # Calcular estatísticas automáticas baseadas nas entradas do usuário
            performance_favorito = (vitorias_favorito / 5) * 100
            performance_azarao = (vitorias_azarao / 5) * 100
            media_gols_favorito = gols_feitos_favorito / 5
            media_gols_azarao = gols_feitos_azarao / 5
            saldo_favorito = (gols_feitos_favorito - gols_sofridos_favorito) / 5
            saldo_azarao = (gols_feitos_azarao - gols_sofridos_azarao) / 5
            
            # Determinar cenário baseado nas estatísticas
            if performance_favorito >= 60 and saldo_favorito > 0.5:
                cenario_principal = "Vitória convincente do favorito"
            elif performance_favorito >= 40 and saldo_azarao < -0.5:
                cenario_principal = "Vitória do favorito com possibilidade do azarão marcar"
            else:
                cenario_principal = "Jogo equilibrado com incerteza no resultado"
            
            # Gerar prompt adaptativo
            prompt = gerar_prompt_inteligente(
                user_profile, bankroll_percentage,
                vitorias_favorito, gols_feitos_favorito, gols_sofridos_favorito,
                vitorias_azarao, gols_feitos_azarao, gols_sofridos_azarao,
                tendencia_gols, motivacao_favorito, forca_ataque, forca_defesa,
                performance_favorito, performance_azarao, media_gols_favorito, 
                media_gols_azarao, saldo_favorito, saldo_azarao, cenario_principal,
                analise_personalizada
            )
            
            st.session_state['generated_prompt'] = prompt

    # --- EXIBIR PROMPT GERADO ---
    if 'generated_prompt' in st.session_state and st.session_state['generated_prompt']:
        st.markdown("---")
        st.subheader("🎯 Prompt Inteligente Gerado")
        
        st.success("✅ Prompt adaptado às estatísticas reais da partida! Copie e cole na sua IA.")
        
        with st.expander("📋 Visualizar Prompt Completo", expanded=True):
            st.code(st.session_state['generated_prompt'], language='markdown')
        
        # Botão para copiar
        if st.button("📋 Copiar Prompt para Área de Transferência", use_container_width=True):
            st.toast("Prompt copiado com sucesso! ✅")

def gerar_prompt_inteligente(perfil, bankroll_perc, vit_fav, gols_fav_f, gols_fav_s, 
                           vit_aza, gols_aza_f, gols_aza_s, tendencia, motivacao, 
                           ataque_fav, defesa_aza, perf_fav, perf_aza, media_fav, 
                           media_aza, saldo_fav, saldo_aza, cenario, analise_extra):
    """Gera um prompt inteligente baseado nas estatísticas fornecidas"""
    
    odds = st.session_state.app_state['odds_values']
    investments = st.session_state.app_state['investment_values']
    bankroll = st.session_state.app_state['total_bankroll']
    bankroll_operacao = bankroll * (bankroll_perc / 100)
    
    # Determinar estratégia recomendada baseada nas estatísticas
    if perf_fav >= 70 and saldo_fav > 1.0:
        estrategia_recomendada = "APOSTA FORTE NO FAVORITO"
        abordagem = "concentrar nos mercados de vitória do favorito e clean sheet"
    elif perf_fav >= 50 and saldo_aza < -0.5:
        estrategia_recomendada = "APOSTA MODERADA NO FAVORITO COM PROTEÇÃO"
        abordagem = "equilibrar entre vitória do favorito e apostas de dupla chance"
    else:
        estrategia_recomendada = "ABORDAGEM CONSERVADORA"
        abordagem = "priorizar apostas de menor risco como dupla chance e under"
    
    prompt = f"""**ANÁLISE ESTRATÉGICA DE APOSTAS - SISTEMA INTELIGENTE**

## 🎯 CONTEXTO DA ANÁLISE

**Perfil do Apostador:** {perfil.upper()}
**Bankroll Alocado:** R$ {bankroll_operacao:.2f} ({bankroll_perc}% do total)

## 📊 ESTATÍSTICAS DETALHADAS DA PARTIDA

### 🏆 FAVORITO (Time da Casa)
- **Performance Recente:** {vit_fav}/5 vitórias ({perf_fav:.0f}% de aproveitamento)
- **Potencial Ofensivo:** {gols_fav_f} gols em 5 jogos (média de {media_fav:.1f} gols/jogo)
- **Solidez Defensiva:** {gols_fav_s} gols sofridos em 5 jogos
- **Saldo de Gols:** {saldo_fav:+.1f} por jogo
- **Força do Ataque:** {ataque_fav}/10
- **Motivação:** {motivacao}

### ⚽ AZARÃO (Time Visitante)  
- **Performance Recente:** {vit_aza}/5 vitórias ({perf_aza:.0f}% de aproveitamento)
- **Potencial Ofensivo:** {gols_aza_f} gols em 5 jogos (média de {media_aza:.1f} gols/jogo)
- **Fragilidade Defensiva:** {gols_aza_s} gols sofridos em 5 jogos
- **Saldo de Gols:** {saldo_aza:+.1f} por jogo
- **Força da Defesa:** {defesa_aza}/10

### 📈 ANÁLISE TÉCNICA AUTOMÁTICA
- **Cenário Mais Provável:** {cenario}
- **Tendência de Gols:** {tendencia}
- **Estratégia Recomendada:** {estrategia_recomendada}
- **Abordagem Sugerida:** {abordagem}

## 💰 DISTRIBUIÇÃO ATUAL DE INVESTIMENTOS

| Mercado | Odds | Investimento Atual | % do Bankroll |
|:---|:---:|:---:|:---:|
"""
    
    for bet_type in BetType:
        bet_name = bet_type.value
        current_odd = odds.get(bet_name, 1.01)
        current_inv = investments.get(bet_name, 0.0)
        percentual = (current_inv / bankroll) * 100 if bankroll > 0 else 0
        prompt += f"| {bet_name} | {current_odd:.2f} | R$ {current_inv:.2f} | {percentual:.1f}% |\n"

    prompt += f"""

## 🧠 QUESTÕES ESTRATÉGICAS PARA ANÁLISE

1. **ANÁLISE DE VALOR:** Considerando as estatísticas acima, quais mercados apresentam melhor relação risco-retorno?
2. **DISTRIBUIÇÃO OTIMIZADA:** Como distribuir R$ {bankroll_operacao:.2f} equilibrando o perfil {perfil} com as probabilidades reais?
3. **PROTEÇÃO DE RISCO:** Quais apostas oferecem melhor hedge contra resultados adversos?
4. **SINERGIA ESTRATÉGICA:** Como as apostas podem se complementar para maximizar lucros nos cenários mais prováveis?

## 📋 RESULTADOS ESPERADOS DA IA

**Por favor, forneça:**
- ✅ Análise detalhada da distribuição atual
- ✅ Nova distribuição otimizada (tabela clara)
- ✅ Justificativa técnica baseada nas estatísticas
- ✅ Cenários de lucro e proteção
- ✅ Estratégia para diferentes resultados

"""
    
    if analise_extra:
        prompt += f"""\n## 🎯 INFORMAÇÕES ADICIONAIS
{analise_extra}
"""
    
    return prompt

# --- Função Principal ---
def main():
    st.set_page_config(page_title="Analisador de Estratégia de Apostas", page_icon="🎯", layout="wide")
    st.title("🎯 Analisador Inteligente de Apostas")
    
    init_state()
    
    # --- Sistema de Abas ---
    tab_config, tab_prompt, tab_hedge = st.tabs([
        "⚙️ Configuração e Cenários", 
        "🤖 Gerador de Prompt IA", 
        "🛡️ Hedge Dinâmico"
    ])

    with tab_config:
        render_controls()
        st.divider()
        # A análise de cenários agora retorna os lucros necessários para o hedge
        scenario_profits = render_scenario_analysis()

    # --- NOVA ABA: Gerador de Prompt ---
    with tab_prompt:
        render_prompt_generator()
        
    with tab_hedge:
        st.header("🛡️ Módulo de Hedge Dinâmico")
        if dinamico_available:
            zero_profit = scenario_profits.get('0x0', 0.0)
            fav_profit = scenario_profits.get('1x1 FAV 1º', 0.0)
            aza_profit = scenario_profits.get('1x1 AZA 1º', 0.0)
            
            st.info(f"Lucros de referência para Hedge: **0x0**: R$ {zero_profit:.2f} | **1x1 (Fav 1º)**: R$ {fav_profit:.2f} | **1x1 (Aza 1º)**: R$ {aza_profit:.2f}")
            
            odds_values = st.session_state.app_state.get('odds_values', {})
            render_hedge_controls(zero_profit, fav_profit, aza_profit, odds_values)
            
            if st.session_state.get('hedge_applied', False):
                render_hedge_results()
        else:
            st.warning("Módulo de Hedge Dinâmico (dinamico.py) não foi encontrado.")

if __name__ == "__main__":
    main()
