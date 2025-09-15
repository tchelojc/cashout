# dinamico.py
import streamlit as st
import pandas as pd
import plotly.express as px
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List

# =============================
# ENUMS E DATACLASSES
# =============================

class RedistributionStrategy(Enum):
    NO_GOAL = "Sem Gol"
    FAV_GOAL = "Gol do Favorito"
    AZA_GOAL = "Gol do Azarão"
    ZERO_ZERO = "0x0"
    ONE_ONE = "1x1"

@dataclass
class HedgeBet:
    bet_type: str
    amount: float
    odds: float
    description: str

# =============================
# GERENCIADOR DINÂMICO
# =============================

class DynamicHedgeManager:
    def __init__(self):
        self.current_hedge_bets: List[HedgeBet] = []
        self.applied_strategy = None
        self.scenario_details = {}

    def apply_from_result(self, strategy: RedistributionStrategy, zero_profit: float, fav_profit: float, aza_profit: float, odds_values: Dict, scenario_details: Dict = None):
        """
        Aplica redistribuição com base na estratégia selecionada
        """
        bets: List[HedgeBet] = []
        kept_profit = 0.0
        self.scenario_details = scenario_details or {}

        # Estratégia para 0x0
        if strategy == RedistributionStrategy.ZERO_ZERO:
            if "zero_zero_type" in self.scenario_details:
                if self.scenario_details["zero_zero_type"] == "0x0":
                    if zero_profit < 0:
                        reinvest = abs(zero_profit) * 0.8
                        kept_profit = 0.0
                        bets.append(HedgeBet(
                            "Não Sair Gols",
                            reinvest,
                            odds_values.get("Não Sair Gols", 3.0),
                            "Recuperação do valor investido"
                        ))
                    else:
                        reinvest = zero_profit * 0.8
                        kept_profit = zero_profit * 0.2
                        bets.append(HedgeBet(
                            "Dupla Chance 1X",
                            reinvest * 0.5,
                            odds_values.get("Dupla Chance 1X", 1.5),
                            "Protege favorito não perder"
                        ))
                        bets.append(HedgeBet(
                            "Dupla Chance X2",
                            reinvest * 0.5,
                            odds_values.get("Dupla Chance X2", 2.5),
                            "Protege azarão não perder"
                        ))

        # Estratégia para 1x1
        elif strategy == RedistributionStrategy.ONE_ONE:
            if "one_one_scorer" in self.scenario_details:
                scorer = self.scenario_details["one_one_scorer"]
                
                if scorer == "FAV":
                    profit_ref = fav_profit
                    dupla_protection = "Dupla Chance 1X"
                else:
                    profit_ref = aza_profit
                    dupla_protection = "Dupla Chance X2"
                
                if profit_ref < 0:
                    reinvest = abs(profit_ref) * 0.8
                    kept_profit = 0.0
                    
                    bets.append(HedgeBet(
                        "Não Sair Gols",
                        reinvest * 0.5,
                        odds_values.get("Não Sair Gols", 3.0),
                        "Protege recuperação do valor investido"
                    ))
                    
                    bets.append(HedgeBet(
                        dupla_protection,
                        reinvest * 0.25,
                        odds_values.get(dupla_protection, 2.0),
                        "Proteção dupla chance"
                    ))
                    bets.append(HedgeBet(
                        "Empate",
                        reinvest * 0.25,
                        odds_values.get("Empate", 3.5),
                        "Protege empate"
                    ))
                else:
                    reinvest = profit_ref * 0.8
                    kept_profit = profit_ref * 0.2
                    
                    bets.append(HedgeBet(
                        "Empate",
                        reinvest * 0.4,
                        odds_values.get("Empate", 3.5),
                        "Protege empate final"
                    ))
                    bets.append(HedgeBet(
                        "Dupla Chance 1X",
                        reinvest * 0.3,
                        odds_values.get("Dupla Chance 1X", 1.5),
                        "Protege favorito não perder"
                    ))
                    bets.append(HedgeBet(
                        "Dupla Chance X2",
                        reinvest * 0.3,
                        odds_values.get("Dupla Chance X2", 2.5),
                        "Protege azarão não perder"
                    ))

        # Estratégias originais mantidas para compatibilidade
        elif strategy == RedistributionStrategy.NO_GOAL:
            kept_profit = max(zero_profit, fav_profit, aza_profit, 0) * 0.5
            
            if kept_profit > 0:
                bets.append(HedgeBet(
                    "Menos 0.5 Gols",
                    kept_profit,
                    odds_values.get("Menos 0.5 Gols", 3.0),
                    "Protege 0x0"
                ))

        elif strategy == RedistributionStrategy.FAV_GOAL:
            if fav_profit < 0:
                reinvest = abs(fav_profit) * 0.8
                kept_profit = 0.0
                bets.append(HedgeBet(
                    "Não Sair Gols",
                    reinvest * 0.5,
                    odds_values.get("Não Sair Gols", 3.0),
                    "Protege recuperação do valor investido"
                ))
                bets.append(HedgeBet(
                    "Ambas Marcam - Não",
                    reinvest * 0.25,
                    odds_values.get("Ambas Marcam - Não", 2.0),
                    "Protege contra ambas marcarem"
                ))
                bets.append(HedgeBet(
                    "Mais de 2.5 Gols",
                    reinvest * 0.25,
                    odds_values.get("Mais de 2.5 Gols", 2.0),
                    "Protege cenários de muitos gols"
                ))
            else:
                reinvest = fav_profit * 0.8
                kept_profit = fav_profit * 0.2
                bets.append(HedgeBet(
                    "Ambas Marcam - Não",
                    reinvest * 0.5,
                    odds_values.get("Ambas Marcam - Não", 2.0),
                    "Protege estagnação do placar"
                ))
                bets.append(HedgeBet(
                    "Mais de 2.5 Gols",
                    reinvest * 0.5,
                    odds_values.get("Mais de 2.5 Gols", 2.0),
                    "Protege jogos abertos"
                ))

        elif strategy == RedistributionStrategy.AZA_GOAL:
            if aza_profit < 0:
                reinvest = abs(aza_profit) * 0.8
                kept_profit = 0.0
                bets.append(HedgeBet(
                    "Vitória do Azarão",
                    reinvest * 0.5,
                    odds_values.get("Vitória do Azarão", 2.0),
                    "Protege recuperando o valor investido"
                ))
                bets.append(HedgeBet(
                    "Ambas Marcam - Não",
                    reinvest * 0.25,
                    odds_values.get("Ambas Marcam - Não", 2.0),
                    "Protege contra empate com ambos marcando"
                ))
                bets.append(HedgeBet(
                    "Mais de 2.5 Gols",
                    reinvest * 0.25,
                    odds_values.get("Mais de 2.5 Gols", 2.0),
                    "Protege cenários de muitos gols"
                ))
            else:
                reinvest = aza_profit * 0.8
                kept_profit = aza_profit * 0.2
                bets.append(HedgeBet(
                    "Vitória do Azarão",
                    reinvest * 0.6,
                    odds_values.get("Vitória do Azarão", 2.0),
                    "Aposta reforçada na vitória do azarão"
                ))
                bets.append(HedgeBet(
                    "Mais de 2.5 Gols",
                    reinvest * 0.4,
                    odds_values.get("Mais de 2.5 Gols", 2.0),
                    "Protege jogos abertos"
                ))

        self.current_hedge_bets = bets
        self.applied_strategy = strategy
        
        strategy_info = {
            "zero_profit": zero_profit,
            "fav_profit": fav_profit,
            "aza_profit": aza_profit,
            "strategy": strategy.value,
            "kept_profit": kept_profit,
            "reinvested": sum(b.amount for b in bets),
            "num_bets": len(bets),
            "scenario_details": self.scenario_details
        }
        st.session_state.last_strategy = strategy_info
        
        return kept_profit, bets

    def get_strategy_summary(self) -> Dict:
        if not self.current_hedge_bets:
            return {}

        total_invested = sum(b.amount for b in self.current_hedge_bets)
        potential_returns = {b.bet_type: b.amount * b.odds for b in self.current_hedge_bets}

        return {
            "strategy": self.applied_strategy.value if self.applied_strategy else "Nenhuma",
            "total_hedge_investment": total_invested,
            "hedge_bets": [
                {"type": b.bet_type, "amount": b.amount, "odds": b.odds, "desc": b.description}
                for b in self.current_hedge_bets
            ],
            "potential_returns": potential_returns,
            "expected_profit": sum(potential_returns.values()) - total_invested,
            "scenario_details": self.scenario_details
        }

# =============================
# ESTADO
# =============================

def init_hedge_state():
    if "hedge_manager" not in st.session_state:
        st.session_state.hedge_manager = DynamicHedgeManager()
    if "hedge_applied" not in st.session_state:
        st.session_state.hedge_applied = False
    if "current_scenario" not in st.session_state:
        st.session_state.current_scenario = None
    if "odds_values" not in st.session_state:
        st.session_state.odds_values = {}
    if "last_strategy" not in st.session_state:
        st.session_state.last_strategy = None
    if "scenario_details" not in st.session_state:
        st.session_state.scenario_details = {}

# =============================
# CONTROLES
# =============================

def render_hedge_controls(zero_profit: float, fav_profit: float, aza_profit: float, odds_values: Dict):
    st.subheader("⚡ Controle Dinâmico do Hedge")
    
    # Mostrar lucros atuais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lucro 0x0", f"R$ {zero_profit:.2f}")
    with col2:
        st.metric("Lucro 1x1 FAV", f"R$ {fav_profit:.2f}")
    with col3:
        st.metric("Lucro 1x1 AZA", f"R$ {aza_profit:.2f}")

    scenario = st.radio(
        "Selecione o cenário atual:",
        options=[e.value for e in RedistributionStrategy],
        horizontal=True,
        key="hedge_scenario"
    )
    st.session_state.current_scenario = scenario

    # Inputs específicos para cenários interativos
    scenario_details = {}
    
    if scenario == RedistributionStrategy.ZERO_ZERO.value:
        st.info("📌 O placar atual é 0x0 ou 1x1?")
        zero_zero_type = st.radio(
            "Tipo de cenário:",
            options=["0x0", "1x1"],
            horizontal=True,
            key="zero_zero_type"
        )
        scenario_details["zero_zero_type"] = zero_zero_type
        
        if zero_zero_type == "1x1":
            # Se for 1x1, redirecionar para o cenário 1x1
            scenario = RedistributionStrategy.ONE_ONE.value
            st.session_state.current_scenario = scenario

    if scenario == RedistributionStrategy.ONE_ONE.value:
        st.info("⚽ Quem fez o 1º gol no 1x1?")
        one_one_scorer = st.radio(
            "Primeiro gol:",
            options=["FAV", "AZA"],
            format_func=lambda x: "Favorito" if x == "FAV" else "Azarão",
            horizontal=True,
            key="one_one_scorer"
        )
        scenario_details["one_one_scorer"] = one_one_scorer

    st.session_state.scenario_details = scenario_details

    st.markdown("### 🎯 Ajuste das Odds em Tempo Real")
    
    # Odds para todos os mercados possíveis
    default_odds = {
        "Não Sair Gols": 3.0,
        "Ambas Marcam - Não": 2.0,
        "Mais de 2.5 Gols": 2.0,
        "Vitória do Azarão": 2.0,
        "Menos 0.5 Gols": 3.0,
        "Dupla Chance 1X": 1.5,
        "Dupla Chance X2": 2.5,
        "Empate": 3.5
    }
    
    # Usar as odds passadas como parâmetro ou as padrão
    odds_inputs = odds_values.copy() if odds_values else {}
    for bet_type, default_odd in default_odds.items():
        if bet_type not in odds_inputs:
            odds_inputs[bet_type] = default_odd

    bet_types = list(default_odds.keys())
    cols = st.columns(2)
    for i, bet in enumerate(bet_types):
        col_idx = i % 2
        with cols[col_idx]:
            odds_inputs[bet] = st.number_input(
                f"{bet}", 
                value=float(odds_inputs[bet]), 
                step=0.1, 
                format="%.2f",
                key=f"odds_{bet}"
            )

    st.session_state.odds_values = odds_inputs

    if st.button("🚀 Aplicar Estratégia de Hedge", type="primary", use_container_width=True):
        strategy = [s for s in RedistributionStrategy if s.value == scenario][0]
        
        kept_profit, hedge_bets = st.session_state.hedge_manager.apply_from_result(
            strategy, zero_profit, fav_profit, aza_profit, odds_inputs, scenario_details
        )
        
        st.session_state.hedge_applied = True
        st.success(f"✅ Estratégia aplicada! Lucro garantido: R$ {kept_profit:.2f}")
        st.rerun()

def render_hedge_results():
    if not st.session_state.hedge_applied:
        return

    st.subheader("📊 Resultados da Estratégia")
    summary = st.session_state.hedge_manager.get_strategy_summary()

    if not summary:
        st.info("Nenhuma estratégia aplicada")
        return

    # Informações da estratégia
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Estratégia", summary['strategy'])
    with col2:
        st.metric("Total Investido", f"R$ {summary['total_hedge_investment']:.2f}")
    with col3:
        st.metric("Lucro Esperado", f"R$ {summary['expected_profit']:.2f}")

    # Detalhes do cenário se aplicável
    if summary.get('scenario_details'):
        st.info(f"📋 Detalhes do cenário: {summary['scenario_details']}")

    # Tabela de apostas
    df = pd.DataFrame(summary["hedge_bets"])
    if not df.empty:
        df["Retorno Potencial"] = df["amount"] * df["odds"]
        df["Lucro Esperado"] = df["Retorno Potencial"] - df["amount"]
        
        st.dataframe(
            df.rename(columns={
                "type": "Tipo de Aposta",
                "amount": "Valor",
                "odds": "Odds",
                "desc": "Descrição"
            }).style.format({
                "Valor": "R$ {:.2f}",
                "Retorno Potencial": "R$ {:.2f}",
                "Lucro Esperado": "R$ {:.2f}",
                "Odds": "{:.2f}"
            }).apply(
                lambda x: ['background-color: #e6f7ff' if 'Lucro Esperado' in x.name else '' for _ in x],
                subset=['Lucro Esperado']
            ),
            hide_index=True,
            use_container_width=True
        )

        # Gráfico de distribuição
        fig = px.pie(df, values="amount", names="type", 
                    title="Distribuição do Hedge", 
                    hover_data=["Retorno Potencial"])
        st.plotly_chart(fig, use_container_width=True)

    # Análise da estratégia
    if st.session_state.last_strategy:
        st.markdown("### 📈 Análise da Estratégia")
        strategy = st.session_state.last_strategy
        st.write(f"**Lucro de referência:** R$ {strategy['zero_profit']:.2f} (0x0) | R$ {strategy['fav_profit']:.2f} (1x1 FAV) | R$ {strategy['aza_profit']:.2f} (1x1 AZA)")
        st.write(f"**Estratégia:** {strategy['strategy']}")
        st.write(f"**Lucro garantido:** R$ {strategy['kept_profit']:.2f}")
        st.write(f"**Reinvestido:** R$ {strategy['reinvested']:.2f} em {strategy['num_bets']} apostas")
        
        if strategy.get('scenario_details'):
            st.write(f"**Detalhes do cenário:** {strategy['scenario_details']}")

# =============================
# MAIN
# =============================

def main_hedge_module():
    st.set_page_config(page_title="Hedge Dinâmico", page_icon="⚡", layout="wide")
    st.title("🛡️ Estratégia de Hedge Dinâmico")
    st.caption("Sistema aprimorado com tratamento para cenários 0x0 e 1x1 em tempo real")

    init_hedge_state()

    # Valores de exemplo (podem ser ajustados conforme necessário)
    zero_profit = st.number_input("Lucro 0x0", value=0.0, step=0.1)
    fav_profit = st.number_input("Lucro 1x1 FAV", value=5.35, step=0.1)
    aza_profit = st.number_input("Lucro 1x1 AZA", value=0.57, step=0.1)

    render_hedge_controls(zero_profit, fav_profit, aza_profit, {})

    if st.session_state.hedge_applied:
        render_hedge_results()

if __name__ == "__main__":
    main_hedge_module()