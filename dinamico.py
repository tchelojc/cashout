# dinamico.py (versão corrigida com memória de operação)
import streamlit as st
import pandas as pd
import plotly.express as px
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np
from datetime import datetime
import json

# =============================
# ENUMS E DATACLASSES
# =============================

class RedistributionStrategy(Enum):
    NO_GOAL = "Sem Gol"
    FAV_GOAL = "Gol do Favorito"
    AZA_GOAL = "Gol do Azarão"
    ZERO_ZERO = "0x0"
    ONE_ONE = "1x1"

class RiskProfile(Enum):
    CONSERVATIVE = "Conservador"
    MODERATE = "Moderado" 
    AGGRESSIVE = "Agressivo"

class OperationStatus(Enum):
    PENDING = "Pendente"
    EXECUTED = "Executada"
    CANCELLED = "Cancelada"

@dataclass
class HedgeBet:
    bet_type: str
    amount: float
    odds: float
    description: str
    market: str
    stake_percentage: float

@dataclass
class IAAnalysis:
    profile: RiskProfile
    recommended_strategy: str
    confidence: float
    key_insights: List[str]
    action_plan: List[str]
    expected_outcome: str

@dataclass
class OperationMemory:
    operation_id: str
    timestamp: datetime
    scenario: str
    profits_before: Dict[str, float]
    ia_analysis: IAAnalysis
    hedge_bets: List[HedgeBet]
    total_investment: float
    status: OperationStatus
    results: Optional[Dict] = None
    learning_notes: List[str] = None

# =============================
# SISTEMA DE MEMÓRIA POR OPERAÇÃO
# =============================

class OperationMemoryManager:
    def __init__(self):
        self.operations: List[OperationMemory] = []
        self.current_operation_id = None
    
    def start_new_operation(self, scenario: str, profits: Dict[str, float], total_investment: float) -> str:
        """Inicia uma nova operação com ID único"""
        operation_id = f"OP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_operation_id = operation_id
        
        new_operation = OperationMemory(
            operation_id=operation_id,
            timestamp=datetime.now(),
            scenario=scenario,
            profits_before=profits.copy(),
            ia_analysis=None,
            hedge_bets=[],
            total_investment=total_investment,
            status=OperationStatus.PENDING,
            learning_notes=[]
        )
        
        self.operations.append(new_operation)
        return operation_id
    
    def save_ia_analysis(self, analysis: IAAnalysis):
        """Salva análise da IA para operação atual"""
        if self.current_operation_id:
            for op in self.operations:
                if op.operation_id == self.current_operation_id:
                    op.ia_analysis = analysis
                    break
    
    def save_hedge_bets(self, hedge_bets: List[HedgeBet]):
        """Salva apostas de hedge para operação atual"""
        if self.current_operation_id:
            for op in self.operations:
                if op.operation_id == self.current_operation_id:
                    op.hedge_bets = hedge_bets
                    op.status = OperationStatus.EXECUTED
                    break
    
    def add_learning_note(self, note: str):
        """Adiciona nota de aprendizado para operação atual"""
        if self.current_operation_id:
            for op in self.operations:
                if op.operation_id == self.current_operation_id:
                    op.learning_notes.append(f"{datetime.now().strftime('%H:%M:%S')}: {note}")
                    break
    
    def get_operation_history(self) -> List[OperationMemory]:
        """Retorna histórico de operações"""
        return sorted(self.operations, key=lambda x: x.timestamp, reverse=True)
    
    def get_operation_by_id(self, operation_id: str) -> Optional[OperationMemory]:
        """Busca operação por ID"""
        for op in self.operations:
            if op.operation_id == operation_id:
                return op
        return None
    
    def get_last_operation(self) -> Optional[OperationMemory]:
        """Retorna a última operação executada"""
        if self.operations:
            return sorted(self.operations, key=lambda x: x.timestamp, reverse=True)[0]
        return None

# =============================
# ANALISADOR DE IA INSTRUTIVO
# =============================

class IAAnalyzer:
    def __init__(self):
        self.risk_profiles = {
            RiskProfile.CONSERVATIVE: {"max_risk": 0.2, "protection_focus": 0.7},
            RiskProfile.MODERATE: {"max_risk": 0.3, "protection_focus": 0.5},
            RiskProfile.AGGRESSIVE: {"max_risk": 0.4, "protection_focus": 0.3}
        }
    
    def analyze_current_situation(self, zero_profit: float, fav_profit: float, aza_profit: float, total_investment: float = 100) -> IAAnalysis:
        """Analisa a situação atual e gera INSTRUÇÕES CLARAS de aplicação"""
        
        profits = [zero_profit, fav_profit, aza_profit]
        max_profit = max(profits)
        min_profit = min(profits)
        volatility = abs(max_profit - min_profit)
        
        # Determinar perfil baseado na volatilidade
        if volatility < 5:
            profile = RiskProfile.CONSERVATIVE
            strategy = "Proteção Máxima"
            insights = ["Baixa volatilidade entre cenários", "Risco controlado", "Foco em proteção"]
            action_plan = self._generate_conservative_actions(zero_profit, fav_profit, aza_profit, total_investment)
            expected_outcome = "Proteção de 70% do lucro máximo com risco mínimo"
            
        elif volatility < 15:
            profile = RiskProfile.MODERATE
            strategy = "Hedge Balanceado"
            insights = ["Volatilidade moderada", "Oportunidade de hedge equilibrado", "Risco calculado"]
            action_plan = self._generate_moderate_actions(zero_profit, fav_profit, aza_profit, total_investment)
            expected_outcome = "Balanceamento entre proteção e oportunidade (50/50)"
            
        else:
            profile = RiskProfile.AGGRESSIVE
            strategy = "Hedge Oportunista"
            insights = ["Alta volatilidade", "Potencial para ganhos significativos", "Risco elevado"]
            action_plan = self._generate_aggressive_actions(zero_profit, fav_profit, aza_profit, total_investment)
            expected_outcome = "Busca por maximização de lucros com aceitação de risco"
        
        # Calcular confiança
        positive_profits = sum(1 for p in profits if p > 0)
        confidence = 0.5 + (positive_profits * 0.15)
        
        return IAAnalysis(
            profile=profile,
            recommended_strategy=strategy,
            confidence=min(0.95, confidence),
            key_insights=insights,
            action_plan=action_plan,
            expected_outcome=expected_outcome
        )
    
    def _generate_conservative_actions(self, zero_profit: float, fav_profit: float, aza_profit: float, total_investment: float) -> List[str]:
        """Gera instruções específicas para perfil conservador"""
        max_profit = max(zero_profit, fav_profit, aza_profit)
        actions = [
            f"🎯 OBJETIVO: Proteger {max_profit:.2f} de lucro máximo",
            f"💰 INVESTIR: Máximo 20% do bankroll (R$ {total_investment * 0.2:.2f})",
            f"🛡️ ESTRATÉGIA: 70% em proteção, 30% em oportunidades seguras",
            f"⏰ TIMING: Aplicar hedge imediatamente",
            f"📊 META: Garantir pelo menos 70% do lucro máximo ({max_profit * 0.7:.2f})",
            f"🚨 STOP: Não exceder R$ {total_investment * 0.25:.2f} em hedge"
        ]
        return actions
    
    def _generate_moderate_actions(self, zero_profit: float, fav_profit: float, aza_profit: float, total_investment: float) -> List[str]:
        """Gera instruções específicas para perfil moderado"""
        max_profit = max(zero_profit, fav_profit, aza_profit)
        actions = [
            f"🎯 OBJETIVO: Balancear proteção e oportunidade",
            f"💰 INVESTIR: Até 30% do bankroll (R$ {total_investment * 0.3:.2f})",
            f"⚖️ ESTRATÉGIA: 50% proteção, 50% oportunidades",
            f"⏰ TIMING: Aplicar hedge nos próximos 10-15 minutos",
            f"📊 META: Lucro líquido mínimo de {max_profit * 0.5:.2f}",
            f"🚨 STOP: Reavaliar se perdas potenciais > R$ {total_investment * 0.15:.2f}"
        ]
        return actions
    
    def _generate_aggressive_actions(self, zero_profit: float, fav_profit: float, aza_profit: float, total_investment: float) -> List[str]:
        """Gera instruções específicas para perfil agressivo"""
        max_profit = max(zero_profit, fav_profit, aza_profit)
        actions = [
            f"🎯 OBJETIVO: Maximizar lucro aproveitando volatilidade",
            f"💰 INVESTIR: Até 40% do bankroll (R$ {total_investment * 0.4:.2f})",
            f"🎲 ESTRATÉGIA: 30% proteção, 70% oportunidades agressivas",
            f"⏰ TIMING: Aplicar hedge durante picos de odds",
            f"📊 META: Potencial de lucro > {max_profit * 1.2:.2f}",
            f"🚨 STOP: Limitar perda máxima em R$ {total_investment * 0.2:.2f}"
        ]
        return actions

# =============================
# GERENCIADOR DINÂMICO INSTRUTIVO (CORRIGIDO)
# =============================

class DynamicHedgeManager:
    def __init__(self):
        self.current_hedge_bets: List[HedgeBet] = []
        self.applied_strategy = None
        self.ia_analyzer = IAAnalyzer()
        self.memory_manager = OperationMemoryManager()
    
    def apply_ia_strategy(self, zero_profit: float, fav_profit: float, aza_profit: float, odds_values: Dict, total_investment: float = 100) -> Tuple[float, List[HedgeBet], IAAnalysis]:
        """Aplica estratégia da IA com instruções claras"""
        
        # Iniciar nova operação na memória
        profits = {"0x0": zero_profit, "1x1_FAV": fav_profit, "1x1_AZA": aza_profit}
        operation_id = self.memory_manager.start_new_operation(
            "Hedge Dinâmico IA", profits, total_investment
        )
        
        # Obter análise detalhada da IA
        ia_analysis = self.ia_analyzer.analyze_current_situation(zero_profit, fav_profit, aza_profit, total_investment)
        self.memory_manager.save_ia_analysis(ia_analysis)
        
        # Aplicar estratégia baseada no perfil
        if ia_analysis.profile == RiskProfile.MODERATE:
            kept_profit, hedge_bets = self._apply_moderate_strategy(zero_profit, fav_profit, aza_profit, odds_values, total_investment, ia_analysis)
        elif ia_analysis.profile == RiskProfile.CONSERVATIVE:
            kept_profit, hedge_bets = self._apply_conservative_strategy(zero_profit, fav_profit, aza_profit, odds_values, total_investment)
        else:
            kept_profit, hedge_bets = self._apply_aggressive_strategy(zero_profit, fav_profit, aza_profit, odds_values, total_investment)
        
        # Salvar operação na memória
        self.memory_manager.save_hedge_bets(hedge_bets)
        self.memory_manager.add_learning_note(f"Estratégia {ia_analysis.profile.value} aplicada com sucesso")
        
        self.current_hedge_bets = hedge_bets
        self.applied_strategy = f"IA_{ia_analysis.profile.value}"
        
        return kept_profit, hedge_bets, ia_analysis
    
    def _apply_moderate_strategy(self, zero_profit: float, fav_profit: float, aza_profit: float, odds_values: Dict, total_investment: float, ia_analysis: IAAnalysis) -> Tuple[float, List[HedgeBet]]:
        """Estratégia moderada com instruções claras"""
        bets = []
        max_hedge = total_investment * 0.3
        
        # Aposta principal de proteção
        protection_bet = HedgeBet(
            "Proteção Balanceada",
            max_hedge * 0.5,
            odds_values.get("Dupla Chance 1X", 1.8),
            "Proteção principal do investimento",
            "Dupla Chance",
            0.5
        )
        bets.append(protection_bet)
        
        # Aposta de oportunidade
        opportunity_bet = HedgeBet(
            "Oportunidade Moderada",
            max_hedge * 0.3,
            odds_values.get("Ambas Marcam - Não", 2.0),
            "Aproveitamento de valor moderado",
            "Ambas Marcam",
            0.3
        )
        bets.append(opportunity_bet)
        
        # Aposta de segurança
        safety_bet = HedgeBet(
            "Segurança Extra",
            max_hedge * 0.2,
            odds_values.get("Não Sair Gols", 3.0),
            "Proteção adicional contra surpresas",
            "Clean Sheet",
            0.2
        )
        bets.append(safety_bet)
        
        kept_profit = max(zero_profit, fav_profit, aza_profit, 0) * 0.5
        return kept_profit, bets
    
    def _apply_conservative_strategy(self, zero_profit: float, fav_profit: float, aza_profit: float, odds_values: Dict, total_investment: float) -> Tuple[float, List[HedgeBet]]:
        """Estratégia conservadora com foco absoluto em proteção"""
        bets = []
        max_hedge = total_investment * 0.2
        
        # Aposta principal ultra-conservadora
        main_bet = HedgeBet(
            "Proteção Máxima",
            max_hedge * 0.7,
            odds_values.get("Não Sair Gols", 3.0),
            "Proteção conservadora principal",
            "Clean Sheet",
            0.7
        )
        bets.append(main_bet)
        
        # Aposta secundária
        secondary_bet = HedgeBet(
            "Backup Seguro",
            max_hedge * 0.3,
            odds_values.get("Dupla Chance 1X", 1.8),
            "Proteção adicional conservadora",
            "Dupla Chance",
            0.3
        )
        bets.append(secondary_bet)
        
        kept_profit = max(zero_profit, fav_profit, aza_profit, 0) * 0.7
        return kept_profit, bets
    
    def _apply_aggressive_strategy(self, zero_profit: float, fav_profit: float, aza_profit: float, odds_values: Dict, total_investment: float) -> Tuple[float, List[HedgeBet]]:
        """Estratégia agressiva focada em maximização"""
        bets = []
        max_hedge = total_investment * 0.4
        
        # Aposta agressiva principal
        aggressive_bet = HedgeBet(
            "Oportunidade Agressiva",
            max_hedge * 0.6,
            odds_values.get("Mais de 2.5 Gols", 2.0),
            "Busca por maximização agressiva",
            "Over 2.5",
            0.6
        )
        bets.append(aggressive_bet)
        
        # Aposta de medio prazo
        medium_bet = HedgeBet(
            "Valor Médio",
            max_hedge * 0.25,
            odds_values.get("Dupla Chance X2", 2.5),
            "Aproveitamento de valor médio",
            "Dupla Chance",
            0.25
        )
        bets.append(medium_bet)
        
        # Pequena proteção
        small_protection = HedgeBet(
            "Proteção Mínima",
            max_hedge * 0.15,
            odds_values.get("Não Sair Gols", 3.0),
            "Proteção básica contra catástrofe",
            "Clean Sheet",
            0.15
        )
        bets.append(small_protection)
        
        kept_profit = max(zero_profit, fav_profit, aza_profit, 0) * 0.1
        return kept_profit, bets

    # 🔧 CORREÇÃO: ADICIONAR MÉTODO get_strategy_summary QUE FALTAVA
    def get_strategy_summary(self) -> Dict:
        """Retorna resumo da estratégia aplicada - MÉTODO CORRIGIDO"""
        if not self.current_hedge_bets:
            return {}
        
        total_invested = sum(b.amount for b in self.current_hedge_bets)
        expected_return = sum(b.amount * b.odds for b in self.current_hedge_bets)
        
        return {
            "strategy": self.applied_strategy or "Nenhuma",
            "total_hedge_investment": total_invested,
            "expected_return": expected_return,
            "expected_profit": expected_return - total_invested,
            "hedge_bets": [
                {
                    "type": b.bet_type,
                    "amount": b.amount,
                    "odds": b.odds,
                    "market": b.market,
                    "stake_percentage": b.stake_percentage,
                    "description": b.description
                }
                for b in self.current_hedge_bets
            ]
        }
    
    def get_current_operation_id(self) -> Optional[str]:
        """Retorna o ID da operação atual"""
        return self.memory_manager.current_operation_id
    
    def get_operation_summary(self, operation_id: str) -> Optional[Dict]:
        """Retorna resumo completo de uma operação específica"""
        operation = self.memory_manager.get_operation_by_id(operation_id)
        if not operation:
            return None
        
        total_hedge_investment = sum(b.amount for b in operation.hedge_bets) if operation.hedge_bets else 0
        expected_return = sum(b.amount * b.odds for b in operation.hedge_bets) if operation.hedge_bets else 0
        
        return {
            "operation_id": operation.operation_id,
            "timestamp": operation.timestamp,
            "scenario": operation.scenario,
            "status": operation.status.value,
            "total_investment": operation.total_investment,
            "total_hedge_investment": total_hedge_investment,
            "expected_profit": expected_return - total_hedge_investment,
            "ia_analysis": {
                "profile": operation.ia_analysis.profile.value if operation.ia_analysis else "N/A",
                "strategy": operation.ia_analysis.recommended_strategy if operation.ia_analysis else "N/A",
                "confidence": operation.ia_analysis.confidence if operation.ia_analysis else 0,
                "action_plan": operation.ia_analysis.action_plan if operation.ia_analysis else []
            } if operation.ia_analysis else None,
            "hedge_bets": [
                {
                    "type": b.bet_type,
                    "amount": b.amount,
                    "odds": b.odds,
                    "market": b.market,
                    "description": b.description
                }
                for b in operation.hedge_bets
            ] if operation.hedge_bets else [],
            "learning_notes": operation.learning_notes or []
        }

# =============================
# INTERFACE INSTRUTIVA (CORRIGIDA)
# =============================

def init_hedge_state():
    if "hedge_manager" not in st.session_state:
        st.session_state.hedge_manager = DynamicHedgeManager()
    if "hedge_applied" not in st.session_state:
        st.session_state.hedge_applied = False
    if "current_operation_id" not in st.session_state:
        st.session_state.current_operation_id = None

def render_ia_instructions(ia_analysis: IAAnalysis):
    """Renderiza instruções claras da IA"""
    st.markdown("### 🎯 PLANO DE AÇÃO DA IA")
    
    # Container destacado com instruções
    with st.container():
        st.success("**INSTRUÇÕES DE APLICAÇÃO:**")
        
        for instruction in ia_analysis.action_plan:
            st.write(f"📍 {instruction}")
        
        st.info(f"**Resultado Esperado:** {ia_analysis.expected_outcome}")

def render_hedge_controls(zero_profit: float, fav_profit: float, aza_profit: float, odds_values: Dict):
    st.subheader("🧠 Controle Dinâmico com IA Instrutiva")
    
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lucro 0x0", f"R$ {zero_profit:.2f}", delta="Positivo" if zero_profit > 0 else "Negativo")
    with col2:
        st.metric("Lucro 1x1 FAV", f"R$ {fav_profit:.2f}", delta="Positivo" if fav_profit > 0 else "Negativo")
    with col3:
        st.metric("Lucro 1x1 AZA", f"R$ {aza_profit:.2f}", delta="Positivo" if aza_profit > 0 else "Negativo")

    # Calcular total investido
    total_investment = abs(zero_profit) + abs(fav_profit) + abs(aza_profit)
    
    # Análise da IA
    st.markdown("### 🤖 ANÁLISE INTELIGENTE DA IA")
    
    ia_analyzer = IAAnalyzer()
    analysis = ia_analyzer.analyze_current_situation(zero_profit, fav_profit, aza_profit, total_investment)
    
    # Exibir análise
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Perfil de Risco:** {analysis.profile.value}")
        st.info(f"**Estratégia Recomendada:** {analysis.recommended_strategy}")
    with col2:
        st.info(f"**Nível de Confiança:** {analysis.confidence:.0%}")
        st.info(f"**Investimento Total:** R$ {total_investment:.2f}")
    
    # Insights da IA
    with st.expander("🔍 Insights Detalhados da IA"):
        for insight in analysis.key_insights:
            st.write(f"• {insight}")

    # INSTRUÇÕES CLARAS DE APLICAÇÃO
    render_ia_instructions(analysis)

    # Configuração de Odds
    st.markdown("### ⚙️ CONFIGURAÇÃO DE MERCADOS")
    
    default_odds = {
        "Não Sair Gols": 3.0,
        "Dupla Chance 1X": 1.8,
        "Dupla Chance X2": 2.5,
        "Ambas Marcam - Não": 2.0,
        "Mais de 2.5 Gols": 2.0
    }
    
    final_odds = odds_values.copy() if odds_values else {}
    for bet_type, default_odd in default_odds.items():
        if bet_type not in final_odds:
            final_odds[bet_type] = st.number_input(
                f"Odd para {bet_type}", 
                value=default_odd, 
                min_value=1.1, 
                max_value=10.0, 
                step=0.1,
                key=f"odd_{bet_type}"
            )

    # BOTÃO DE APLICAÇÃO COM FEEDBACK CLARO
    st.markdown("### 🚀 EXECUTAR ESTRATÉGIA")
    
    if st.button("✅ APLICAR ESTRATÉGIA DA IA", type="primary", use_container_width=True):
        with st.spinner("Executando análise e aplicando estratégia..."):
            try:
                kept_profit, hedge_bets, ia_analysis = st.session_state.hedge_manager.apply_ia_strategy(
                    zero_profit, fav_profit, aza_profit, final_odds, total_investment
                )
                
                st.session_state.hedge_applied = True
                st.session_state.current_operation_id = st.session_state.hedge_manager.get_current_operation_id()
                
                # FEEDBACK DETALHADO DA APLICAÇÃO
                st.success("🎉 **ESTRATÉGIA APLICADA COM SUCESSO!**")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Lucro Garantido", f"R$ {kept_profit:.2f}")
                with col2:
                    st.metric("Total Apostas", f"R$ {sum(b.amount for b in hedge_bets):.2f}")
                with col3:
                    st.metric("Operação ID", st.session_state.current_operation_id)
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro na aplicação: {e}")

def render_hedge_results():
    if not st.session_state.hedge_applied:
        return

    st.subheader("📊 RESULTADOS DA OPERAÇÃO")
    
    # Obter operação atual
    current_op_id = st.session_state.current_operation_id
    if not current_op_id:
        st.info("Nenhuma operação ativa")
        return
        
    operation_summary = st.session_state.hedge_manager.get_operation_summary(current_op_id)
    
    if not operation_summary:
        st.info("Operação não encontrada")
        return

    # Detalhes da operação
    st.markdown(f"**Operação:** {operation_summary['operation_id']} | **Status:** {operation_summary['status']}")
    st.markdown(f"**Início:** {operation_summary['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")

    # Resumo da estratégia - AGORA FUNCIONANDO
    summary = st.session_state.hedge_manager.get_strategy_summary()
    
    if summary:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Estratégia", summary['strategy'])
        with col2:
            st.metric("Total Investido", f"R$ {summary['total_hedge_investment']:.2f}")
        with col3:
            st.metric("Lucro Esperado", f"R$ {summary['expected_profit']:.2f}")

    # INSTRUÇÕES DE APLICAÇÃO DA OPERAÇÃO
    if operation_summary['ia_analysis']:
        st.markdown("### 📋 INSTRUÇÕES DA OPERAÇÃO")
        for instruction in operation_summary['ia_analysis']['action_plan']:
            st.write(f"✅ {instruction}")

    # Detalhes das apostas
    if operation_summary['hedge_bets']:
        st.markdown("### 💰 APOSTAS APLICADAS")
        
        bets_data = []
        for bet in operation_summary['hedge_bets']:
            bets_data.append({
                'Mercado': bet['market'],
                'Tipo': bet['type'],
                'Valor': f"R$ {bet['amount']:.2f}",
                'Odd': bet['odds'],
                'Retorno Potencial': f"R$ {bet['amount'] * bet['odds']:.2f}",
                'Descrição': bet['description']
            })
        
        df = pd.DataFrame(bets_data)
        st.dataframe(df, use_container_width=True)

    # HISTÓRICO DE OPERAÇÕES
    st.markdown("### 📚 HISTÓRICO DE OPERAÇÕES")
    operations = st.session_state.hedge_manager.memory_manager.get_operation_history()
    
    if operations:
        for op in operations[:5]:  # Últimas 5 operações
            with st.expander(f"Operação {op.operation_id} - {op.timestamp.strftime('%H:%M:%S')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Status:** {op.status.value}")
                    if op.ia_analysis:
                        st.write(f"**Perfil:** {op.ia_analysis.profile.value}")
                with col2:
                    st.write(f"**Investimento:** R$ {op.total_investment:.2f}")
                    st.write(f"**Apostas:** {len(op.hedge_bets)}")
                
                if op.learning_notes:
                    st.write("**Aprendizados:**")
                    for note in op.learning_notes[-3:]:  # Últimos 3 aprendizados
                        st.write(f"• {note}")

# =============================
# FUNÇÕES DE INTEGRAÇÃO COM AO_VIVO.PY
# =============================

def get_current_operation_info() -> Optional[Dict]:
    """Retorna informações da operação atual para integração com ao_vivo.py"""
    if "hedge_manager" not in st.session_state:
        return None
    
    current_op_id = st.session_state.hedge_manager.get_current_operation_id()
    if not current_op_id:
        return None
    
    return st.session_state.hedge_manager.get_operation_summary(current_op_id)

def continue_operation_from_id(operation_id: str) -> bool:
    """Continua uma operação existente a partir do ID - para integração com ao_vivo.py"""
    if "hedge_manager" not in st.session_state:
        return False
    
    operation = st.session_state.hedge_manager.memory_manager.get_operation_by_id(operation_id)
    if not operation:
        return False
    
    st.session_state.hedge_manager.memory_manager.current_operation_id = operation_id
    st.session_state.current_operation_id = operation_id
    st.session_state.hedge_applied = True
    
    # Recarregar as apostas de hedge da operação
    st.session_state.hedge_manager.current_hedge_bets = operation.hedge_bets
    st.session_state.hedge_manager.applied_strategy = f"Continuação_{operation_id}"
    
    return True

# =============================
# COMPATIBILIDADE
# =============================

def render_hedge_controls_original(zero_profit: float, fav_profit: float, aza_profit: float, odds_values: Dict):
    return render_hedge_controls(zero_profit, fav_profit, aza_profit, odds_values)

def main_hedge_module():
    """Função principal para teste"""
    st.set_page_config(page_title="Hedge Instrutivo", page_icon="🎓", layout="wide")
    st.title("🛡️ HEDGE DINÂMICO COM IA INSTRUTIVA")
    
    init_hedge_state()
    
    st.sidebar.header("📊 Dados de Entrada")
    zero_profit = st.sidebar.number_input("Lucro 0x0", value=2.27, step=0.1)
    fav_profit = st.sidebar.number_input("Lucro 1x1 FAV", value=-0.98, step=0.1)
    aza_profit = st.sidebar.number_input("Lucro 1x1 AZA", value=-0.98, step=0.1)
    
    render_hedge_controls(zero_profit, fav_profit, aza_profit, {})
    
    if st.session_state.hedge_applied:
        render_hedge_results()

if __name__ == "__main__":
    main_hedge_module()
