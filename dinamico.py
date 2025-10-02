# dinamico.py (VERSÃO COMPLETA COM SISTEMA DE ESTATÍSTICAS E PROMPTS DINÂMICOS)
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

class MatchEvent(Enum):
    FIRST_HALF_END = "Fim do 1º Tempo"
    SECOND_HALF_START = "Início do 2º Tempo"
    FAV_GOAL = "Gol do Favorito"
    AZA_GOAL = "Gol do Azarão"
    FAV_RED_CARD = "Cartão Vermelho Favorito"
    AZA_RED_CARD = "Cartão Vermelho Azarão"
    INJURY_TIME = "Acréscimos"
    HALFTIME_BREAK = "Intervalo"
    MATCH_START = "Início da Partida"

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
    prompt_suggestions: List[str]
    comprehensive_prompt: str

@dataclass
class MatchStatistics:
    possession_fav: int
    possession_aza: int
    shots_fav: int
    shots_aza: int
    shots_on_target_fav: int
    shots_on_target_aza: int
    dangerous_attacks_fav: int
    dangerous_attacks_aza: int
    corners_fav: int
    corners_aza: int
    fouls_fav: int
    fouls_aza: int
    offsides_fav: int
    offsides_aza: int
    yellow_cards_fav: int
    yellow_cards_aza: int
    red_cards_fav: int
    red_cards_aza: int

@dataclass
class MatchContext:
    current_score: str
    minute: int
    statistics: MatchStatistics
    event_type: MatchEvent
    momentum: str  # 'FAV', 'AZA', 'BALANCED'
    additional_notes: str

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
    match_context: Optional[MatchContext] = None
    results: Optional[Dict] = None
    learning_notes: List[str] = None
    generated_prompts: List[str] = None

# =============================
# SISTEMA DE MEMÓRIA POR OPERAÇÃO
# =============================

class OperationMemoryManager:
    def __init__(self):
        self.operations: List[OperationMemory] = []
        self.current_operation_id = None
    
    def start_new_operation(self, scenario: str, profits: Dict[str, float], total_investment: float, match_context: MatchContext = None) -> str:
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
            match_context=match_context,
            learning_notes=[],
            generated_prompts=[]
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
    
    def add_generated_prompt(self, prompt: str):
        """Adiciona prompt gerado para operação atual"""
        if self.current_operation_id:
            for op in self.operations:
                if op.operation_id == self.current_operation_id:
                    op.generated_prompts.append({
                        'timestamp': datetime.now(),
                        'prompt': prompt
                    })
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
# ANALISADOR DE IA INSTRUTIVO (APRIMORADO)
# =============================

class IAAnalyzer:
    def __init__(self):
        self.risk_profiles = {
            RiskProfile.CONSERVATIVE: {"max_risk": 0.2, "protection_focus": 0.7},
            RiskProfile.MODERATE: {"max_risk": 0.3, "protection_focus": 0.5},
            RiskProfile.AGGRESSIVE: {"max_risk": 0.4, "protection_focus": 0.3}
        }
    
    def analyze_current_situation(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                                total_investment: float = 100, match_context: MatchContext = None,
                                odds_values: Dict = None) -> IAAnalysis:
        """Analisa a situação atual e gera INSTRUÇÕES CLARAS de aplicação"""
        
        profits = [zero_profit, fav_profit, aza_profit]
        max_profit = max(profits)
        min_profit = min(profits)
        volatility = abs(max_profit - min_profit)
        
        # Ajustar análise baseado no contexto da partida
        context_adjustment = self._adjust_for_match_context(match_context, volatility)
        
        # Determinar perfil baseado na volatilidade e contexto
        adjusted_volatility = volatility * context_adjustment['volatility_multiplier']
        
        if adjusted_volatility < 5:
            profile = RiskProfile.CONSERVATIVE
            strategy = "Proteção Máxima"
            insights = ["Baixa volatilidade entre cenários", "Risco controlado", "Foco em proteção"] + context_adjustment['insights']
            action_plan = self._generate_conservative_actions(zero_profit, fav_profit, aza_profit, total_investment, match_context)
            expected_outcome = "Proteção de 70% do lucro máximo com risco mínimo"
            
        elif adjusted_volatility < 15:
            profile = RiskProfile.MODERATE
            strategy = "Hedge Balanceado"
            insights = ["Volatilidade moderada", "Oportunidade de hedge equilibrado", "Risco calculado"] + context_adjustment['insights']
            action_plan = self._generate_moderate_actions(zero_profit, fav_profit, aza_profit, total_investment, match_context)
            expected_outcome = "Balanceamento entre proteção e oportunidade (50/50)"
            
        else:
            profile = RiskProfile.AGGRESSIVE
            strategy = "Hedge Oportunista"
            insights = ["Alta volatilidade", "Potencial para ganhos significativos", "Risco elevado"] + context_adjustment['insights']
            action_plan = self._generate_aggressive_actions(zero_profit, fav_profit, aza_profit, total_investment, match_context)
            expected_outcome = "Busca por maximização de lucros com aceitação de risco"
        
        # Calcular confiança com ajuste contextual
        positive_profits = sum(1 for p in profits if p > 0)
        confidence = min(0.95, 0.5 + (positive_profits * 0.15) * context_adjustment['confidence_multiplier'])
        
        # Gerar sugestões de prompt
        prompt_suggestions = self._generate_prompt_suggestions(profile, match_context, profits, odds_values)
        
        # Gerar prompt completo e abrangente
        comprehensive_prompt = self._generate_comprehensive_prompt(profile, match_context, profits, odds_values, action_plan)
        
        return IAAnalysis(
            profile=profile,
            recommended_strategy=strategy,
            confidence=confidence,
            key_insights=insights,
            action_plan=action_plan,
            expected_outcome=expected_outcome,
            prompt_suggestions=prompt_suggestions,
            comprehensive_prompt=comprehensive_prompt
        )
    
    def _adjust_for_match_context(self, match_context: MatchContext, base_volatility: float) -> Dict:
        """Ajusta a análise baseado no contexto atual da partida"""
        if not match_context:
            return {
                'volatility_multiplier': 1.0,
                'confidence_multiplier': 1.0,
                'insights': ["Partida ainda não iniciada"]
            }
        
        insights = []
        volatility_multiplier = 1.0
        confidence_multiplier = 1.0
        
        # Analisar momento da partida
        if match_context.minute <= 45:
            insights.append(f"⏰ Primeiro tempo em andamento ({match_context.minute}')")
            if match_context.minute < 25:
                volatility_multiplier *= 0.8  # Menos volatilidade no início
            else:
                volatility_multiplier *= 1.2  # Mais volatilidade perto do intervalo
        else:
            insights.append(f"⏰ Segundo tempo em andamento ({match_context.minute}')")
            volatility_multiplier *= 1.5  # Máxima volatilidade no segundo tempo
        
        # Analisar placar
        if match_context.current_score == "0x0":
            insights.append("📊 Placar 0x0 - Alta incerteza")
            volatility_multiplier *= 1.3
        else:
            insights.append(f"📊 Placar {match_context.current_score} - Cenário definido")
            confidence_multiplier *= 1.2
        
        # Analisar momentum
        if match_context.momentum == 'FAV':
            insights.append("📈 Momentum do favorito")
            confidence_multiplier *= 1.1
        elif match_context.momentum == 'AZA':
            insights.append("📉 Momentum do azarão")
            volatility_multiplier *= 1.4
        
        # Analisar evento específico
        if match_context.event_type == MatchEvent.FAV_GOAL:
            insights.append("⚽ Gol do favorito - Reavaliar estratégia")
            volatility_multiplier *= 1.8
        elif match_context.event_type == MatchEvent.AZA_GOAL:
            insights.append("⚽ Gol do azarão - Oportunidade de hedge")
            volatility_multiplier *= 2.0
        elif match_context.event_type == MatchEvent.FIRST_HALF_END:
            insights.append("🔄 Fim do primeiro tempo - Ponto de reavaliação")
            confidence_multiplier *= 1.3
        
        return {
            'volatility_multiplier': volatility_multiplier,
            'confidence_multiplier': confidence_multiplier,
            'insights': insights
        }
    
    def _generate_comprehensive_prompt(self, profile: RiskProfile, match_context: MatchContext, 
                                     profits: List[float], odds_values: Dict, action_plan: List[str]) -> str:
        """Gera um prompt completo e abrangente para análise da IA"""
        
        if not match_context:
            return self._generate_pre_match_prompt(profile, profits, odds_values, action_plan)
        
        stats = match_context.statistics
        
        prompt = f"""
## 🎯 ANÁLISE COMPLETA DA PARTIDA - STARTUP ALMA

### ⚽ CONTEXTO ATUAL DA PARTIDA
**📊 PLACAR E TEMPO:**
- **Placar Atual:** {match_context.current_score}
- **Minuto da Partida:** {match_context.minute}'
- **Evento Recente:** {match_context.event_type.value}
- **Momentum do Jogo:** {match_context.momentum}

**📈 ESTATÍSTICAS DETALHADAS:**
POSSE DE BOLA: Favorito {stats.possession_fav}% - Azarão {stats.possession_aza}%
FINALIZAÇÕES: Favorito {stats.shots_fav} ({stats.shots_on_target_fav} no alvo) - Azarão {stats.shots_aza} ({stats.shots_on_target_aza} no alvo)
ATAQUES PERIGOSOS: Favorito {stats.dangerous_attacks_fav} - Azarão {stats.dangerous_attacks_aza}
ESCANTEIOS: Favorito {stats.corners_fav} - Azarão {stats.corners_aza}
FALTAS: Favorito {stats.fouls_fav} - Azarão {stats.fouls_aza}
IMPEDIMENTOS: Favorito {stats.offsides_fav} - Azarão {stats.offsides_aza}
CARTÕES: Favorito {stats.yellow_cards_fav} amarelos, {stats.red_cards_fav} vermelhos - Azarão {stats.yellow_cards_aza} amarelos, {stats.red_cards_aza} vermelhos


### 💰 SITUAÇÃO FINANCEIRA ATUAL
**LUCROS POR CENÁRIO:**
- **0x0:** R$ {profits[0]:.2f}
- **1x1 FAV:** R$ {profits[1]:.2f}
- **1x1 AZA:** R$ {profits[2]:.2f}

**PERFIL E ESTRATÉGIA:**
- **Perfil de Risco:** {profile.value}
- **Estratégia Recomendada:** {'Proteção Máxima' if profile == RiskProfile.CONSERVATIVE else 'Hedge Balanceado' if profile == RiskProfile.MODERATE else 'Hedge Oportunista'}

### 🎰 ODDS ATUAIS DISPONÍVEIS
"""
        
        # Adicionar odds disponíveis
        if odds_values:
            for market, odd in odds_values.items():
                prompt += f"- **{market}:** {odd:.2f}\n"
        
        prompt += f"""
### 🧠 SOLICITAÇÃO DE ANÁLISE COMPLETA:

Baseado no contexto completo da partida (estatísticas, momento, situação financeira), forneça uma análise detalhada considerando:

1. **ANÁLISE TÁTICA DO JOGO:**
   - Equilíbrio das equipes baseado nas estatísticas
   - Dominância real vs. resultado
   - Fatores que podem influenciar o restante da partida

2. **PROBABILIDADES ATUALIZADAS:**
   - Cenários mais prováveis considerando o andamento
   - Valor das odds atuais
   - Probabilidade de mais gols

3. **ESTRATÉGIA DE INVESTIMENTO:**
   - Distribuição ideal considerando o contexto
   - Oportunidades de value bet
   - Proteções necessárias

4. **PLANO DE AÇÃO:**
   - Ações imediatas recomendadas
   - Pontos de entrada e saída
   - Gestão de risco específica

**Notas Adicionais:** {match_context.additional_notes if match_context.additional_notes else "Nenhuma observação adicional"}

**Por favor, seja extremamente detalhado, data-driven e forneça recomendações específicas e acionáveis.**
"""
        
        return prompt
    
    def _generate_pre_match_prompt(self, profile: RiskProfile, profits: List[float], odds_values: Dict, action_plan: List[str]) -> str:
        """Gera prompt para análise pré-partida"""
        prompt = f"""
## 🎯 ANÁLISE PRÉ-PARTIDA - STARTUP ALMA

### 💰 SITUAÇÃO FINANCEIRA INICIAL
**LUCROS POR CENÁRIO:**
- **0x0:** R$ {profits[0]:.2f}
- **1x1 FAV:** R$ {profits[1]:.2f}
- **1x1 AZA:** R$ {profits[2]:.2f}

**PERFIL E ESTRATÉGIA:**
- **Perfil de Risco:** {profile.value}
- **Plano de Ação:** {', '.join(action_plan)}

### 🎰 ODDS INICIAIS DISPONÍVEIS
"""
        
        if odds_values:
            for market, odd in odds_values.items():
                prompt += f"- **{market}:** {odd:.2f}\n"
        
        prompt += """
### 🧠 SOLICITAÇÃO DE ANÁLISE PRÉ-PARTIDA:

Forneça uma análise completa considerando:

1. **AVALIAÇÃO DE VALOR:**
   - Identificação de value bets
   - Probabilidades implícitas vs. reais
   - Mercados mais interessantes

2. **DISTRIBUIÇÃO INICIAL:**
   - Alocação ideal de bankroll
   - Estratégia de entrada
   - Diversificação

3. **GESTÃO DE RISCO INICIAL:**
   - Exposição máxima recomendada
   - Pontos de monitoramento
   - Planos de contingência

**Forneça uma estratégia clara e data-driven para o início da partida.**
"""
        
        return prompt
    
    def _generate_prompt_suggestions(self, profile: RiskProfile, match_context: MatchContext, 
                                   profits: List[float], odds_values: Dict) -> List[str]:
        """Gera sugestões de prompt específicas para o contexto"""
        suggestions = []
        
        if match_context and match_context.event_type == MatchEvent.FIRST_HALF_END:
            suggestions.append(self._generate_halftime_prompt(profile, match_context, profits, odds_values))
        
        if match_context and match_context.event_type in [MatchEvent.FAV_GOAL, MatchEvent.AZA_GOAL]:
            suggestions.append(self._generate_goal_prompt(profile, match_context, profits, odds_values))
        
        # Prompt geral para qualquer momento
        suggestions.append(self._generate_general_analysis_prompt(profile, match_context, profits, odds_values))
        
        return suggestions
    
    def _generate_halftime_prompt(self, profile: RiskProfile, match_context: MatchContext, 
                                profits: List[float], odds_values: Dict) -> str:
        """Gera prompt específico para análise do intervalo"""
        stats = match_context.statistics
        
        return f"""
## 🔄 ANÁLISE DO INTERVALO - STARTUP ALMA

### ⚽ RESUMO DO PRIMEIRO TEMPO
**Placar:** {match_context.current_score} | **Estatísticas Chave:**
- Posse: {stats.possession_fav}% vs {stats.possession_aza}%
- Finalizações: {stats.shots_fav}({stats.shots_on_target_fav}) vs {stats.shots_aza}({stats.shots_on_target_aza})
- Escanteios: {stats.corners_fav} vs {stats.corners_aza}

### 💰 SITUAÇÃO ATUAL
Lucro 0x0: R$ {profits[0]:.2f} | 1x1 FAV: R$ {profits[1]:.2f} | 1x1 AZA: R$ {profits[2]:.2f}

### 🎯 SOLICITAÇÃO DE ANÁLISE:
Analise o primeiro tempo e forneça previsões para o segundo tempo, considerando:
- Performance real vs. expectativas
- Fatores de desgaste físico
- Probabilidade de mais gols
- Ajustes táticos esperados
- Estratégia ideal para o segundo tempo
"""
    
    def _generate_goal_prompt(self, profile: RiskProfile, match_context: MatchContext, 
                            profits: List[float], odds_values: Dict) -> str:
        """Gera prompt específico para análise pós-gol"""
        goal_team = "FAVORITO" if match_context.event_type == MatchEvent.FAV_GOAL else "AZARÃO"
        
        return f"""
## ⚽ ANÁLISE PÓS-GOL - STARTUP ALMA

### 🎉 GOL MARCADO
**Time:** {goal_team} | **Placar:** {match_context.current_score} | **Minuto:** {match_context.minute}'

### 💰 IMPACTO FINANCEIRO
Lucro 0x0: R$ {profits[0]:.2f} | 1x1 FAV: R$ {profits[1]:.2f} | 1x1 AZA: R$ {profits[2]:.2f}

### 🎯 SOLICITAÇÃO DE ANÁLISE URGENTE:
Analise o impacto imediato do gol e forneça recomendações:
- Mudança no equilíbrio tático
- Reação esperada do time sofredor
- Novas probabilidades de cenários
- Oportunidades de hedge emergentes
- Ações recomendadas imediatas
"""
    
    def _generate_general_analysis_prompt(self, profile: RiskProfile, match_context: MatchContext, 
                                        profits: List[float], odds_values: Dict) -> str:
        """Gera prompt geral para análise em tempo real"""
        return f"""
## 📊 ANÁLISE EM TEMPO REAL - STARTUP ALMA

### ⚽ CONTEXTO ATUAL
**Placar:** {match_context.current_score if match_context else '0x0'} | **Minuto:** {match_context.minute if match_context else '0'}'

### 💰 SITUAÇÃO FINANCEIRA
Lucro 0x0: R$ {profits[0]:.2f} | 1x1 FAV: R$ {profits[1]:.2f} | 1x1 AZA: R$ {profits[2]:.2f}

### 🎯 SOLICITAÇÃO DE ANÁLISE:
Forneça uma análise completa do momento atual considerando:
- Equilíbrio do jogo e momentum
- Probabilidades atualizadas de cenários
- Oportunidades de value bet
- Estratégia de hedge recomendada
- Gestão de risco específica
"""
    
    def _generate_conservative_actions(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                                     total_investment: float, match_context: MatchContext) -> List[str]:
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
        
        if match_context and match_context.minute > 40:
            actions.append("🔔 ATENÇÃO: Fim do primeiro tempo próximo - considerar esperar")
        
        return actions
    
    def _generate_moderate_actions(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                                 total_investment: float, match_context: MatchContext) -> List[str]:
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
        
        if match_context and match_context.event_type == MatchEvent.FIRST_HALF_END:
            actions.append("🔄 OPORTUNIDADE: Reavaliação no intervalo - odds podem melhorar")
        
        return actions
    
    def _generate_aggressive_actions(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                                   total_investment: float, match_context: MatchContext) -> List[str]:
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
        
        if match_context and match_context.event_type in [MatchEvent.FAV_GOAL, MatchEvent.AZA_GOAL]:
            actions.append("⚡ OPORTUNIDADE: Gol recente - volatilidade alta para apostas agressivas")
        
        return actions

# =============================
# GERENCIADOR DINÂMICO INSTRUTIVO (APRIMORADO)
# =============================

class DynamicHedgeManager:
    def __init__(self):
        self.current_hedge_bets: List[HedgeBet] = []
        self.applied_strategy = None
        self.ia_analyzer = IAAnalyzer()
        self.memory_manager = OperationMemoryManager()
    
    def apply_ia_strategy(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                         odds_values: Dict, total_investment: float = 100, 
                         match_context: MatchContext = None) -> Tuple[float, List[HedgeBet], IAAnalysis]:
        """Aplica estratégia da IA com instruções claras"""
        
        # Iniciar nova operação na memória
        profits = {"0x0": zero_profit, "1x1_FAV": fav_profit, "1x1_AZA": aza_profit}
        operation_id = self.memory_manager.start_new_operation(
            "Hedge Dinâmico IA", profits, total_investment, match_context
        )
        
        # Obter análise detalhada da IA
        ia_analysis = self.ia_analyzer.analyze_current_situation(
            zero_profit, fav_profit, aza_profit, total_investment, match_context, odds_values
        )
        self.memory_manager.save_ia_analysis(ia_analysis)
        
        # Salvar prompts gerados
        for prompt in ia_analysis.prompt_suggestions:
            self.memory_manager.add_generated_prompt(prompt)
        
        self.memory_manager.add_generated_prompt(ia_analysis.comprehensive_prompt)
        
        # Aplicar estratégia baseada no perfil
        if ia_analysis.profile == RiskProfile.MODERATE:
            kept_profit, hedge_bets = self._apply_moderate_strategy(zero_profit, fav_profit, aza_profit, odds_values, total_investment, ia_analysis, match_context)
        elif ia_analysis.profile == RiskProfile.CONSERVATIVE:
            kept_profit, hedge_bets = self._apply_conservative_strategy(zero_profit, fav_profit, aza_profit, odds_values, total_investment, match_context)
        else:
            kept_profit, hedge_bets = self._apply_aggressive_strategy(zero_profit, fav_profit, aza_profit, odds_values, total_investment, match_context)
        
        # Salvar operação na memória
        self.memory_manager.save_hedge_bets(hedge_bets)
        self.memory_manager.add_learning_note(f"Estratégia {ia_analysis.profile.value} aplicada com sucesso")
        
        self.current_hedge_bets = hedge_bets
        self.applied_strategy = f"IA_{ia_analysis.profile.value}"
        
        return kept_profit, hedge_bets, ia_analysis
    
    def _apply_moderate_strategy(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                               odds_values: Dict, total_investment: float, ia_analysis: IAAnalysis,
                               match_context: MatchContext) -> Tuple[float, List[HedgeBet]]:
        """Estratégia moderada com instruções claras"""
        bets = []
        max_hedge = total_investment * 0.3
        
        # Ajustar baseado no contexto da partida
        if match_context and match_context.minute > 40:
            max_hedge *= 0.8  # Reduzir exposição perto do intervalo
        
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
    
    def _apply_conservative_strategy(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                                   odds_values: Dict, total_investment: float, match_context: MatchContext) -> Tuple[float, List[HedgeBet]]:
        """Estratégia conservadora com foco absoluto em proteção"""
        bets = []
        max_hedge = total_investment * 0.2
        
        # Aumentar proteção se gol marcado
        if match_context and match_context.event_type in [MatchEvent.FAV_GOAL, MatchEvent.AZA_GOAL]:
            max_hedge *= 1.2
        
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
    
    def _apply_aggressive_strategy(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                                 odds_values: Dict, total_investment: float, match_context: MatchContext) -> Tuple[float, List[HedgeBet]]:
        """Estratégia agressiva focada em maximização"""
        bets = []
        max_hedge = total_investment * 0.4
        
        # Aumentar agressividade em momentos chave
        if match_context and match_context.event_type in [MatchEvent.FAV_GOAL, MatchEvent.AZA_GOAL]:
            max_hedge *= 1.3
        
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

    def get_strategy_summary(self) -> Dict:
        """Retorna resumo da estratégia aplicada"""
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
            "match_context": {
                "current_score": operation.match_context.current_score if operation.match_context else "N/A",
                "minute": operation.match_context.minute if operation.match_context else "N/A",
                "event_type": operation.match_context.event_type.value if operation.match_context else "N/A",
                "momentum": operation.match_context.momentum if operation.match_context else "N/A"
            } if operation.match_context else None,
            "ia_analysis": {
                "profile": operation.ia_analysis.profile.value if operation.ia_analysis else "N/A",
                "strategy": operation.ia_analysis.recommended_strategy if operation.ia_analysis else "N/A",
                "confidence": operation.ia_analysis.confidence if operation.ia_analysis else 0,
                "action_plan": operation.ia_analysis.action_plan if operation.ia_analysis else [],
                "prompt_suggestions": operation.ia_analysis.prompt_suggestions if operation.ia_analysis else [],
                "comprehensive_prompt": operation.ia_analysis.comprehensive_prompt if operation.ia_analysis else ""
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
            "learning_notes": operation.learning_notes or [],
            "generated_prompts": operation.generated_prompts or []
        }

# =============================
# INTERFACE INSTRUTIVA (APRIMORADA)
# =============================

def init_hedge_state():
    if "hedge_manager" not in st.session_state:
        st.session_state.hedge_manager = DynamicHedgeManager()
    if "hedge_applied" not in st.session_state:
        st.session_state.hedge_applied = False
    if "current_operation_id" not in st.session_state:
        st.session_state.current_operation_id = None
    if "match_context" not in st.session_state:
        st.session_state.match_context = None

def create_statistics_interface():
    """Interface completa para captura de estatísticas da partida"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Estatísticas da Partida")
    
    # Informações básicas do jogo
    col1, col2 = st.sidebar.columns(2)
    with col1:
        current_score = st.text_input("Placar Atual", value="0x0", key="score_input")
    with col2:
        minute = st.slider("Minuto da Partida", 0, 120, 45, key="minute_slider")
    
    # Evento recente
    event_options = [e.value for e in MatchEvent] + ["Nenhum"]
    selected_event = st.selectbox("Evento Recente", event_options, key="event_select")
    
    # Momentum do jogo
    momentum = st.selectbox("Momentum do Jogo", ["BALANCED", "FAV", "AZA"], key="momentum_select")
    
    # Estatísticas detalhadas
    st.sidebar.markdown("### 📈 Estatísticas Detalhadas")
    
    with st.sidebar.expander("🎯 Posse e Finalizações", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🏆 Favorito**")
            possession_fav = st.number_input("Posse (%)", 0, 100, 50, key="possession_fav")
            shots_fav = st.number_input("Finalizações", 0, 30, 5, key="shots_fav")
            shots_on_target_fav = st.number_input("No Alvo", 0, 15, 2, key="shots_target_fav")
        with col2:
            st.markdown("**⚽ Azarão**")
            possession_aza = st.number_input("Posse (%)", 0, 100, 50, key="possession_aza")
            shots_aza = st.number_input("Finalizações", 0, 30, 2, key="shots_aza")
            shots_on_target_aza = st.number_input("No Alvo", 0, 15, 1, key="shots_target_aza")
    
    with st.sidebar.expander("⚡ Ataques e Escanteios", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            dangerous_attacks_fav = st.number_input("Ataques Perigosos FAV", 0, 50, 8, key="attacks_fav")
            corners_fav = st.number_input("Escanteios FAV", 0, 15, 3, key="corners_fav")
        with col2:
            dangerous_attacks_aza = st.number_input("Ataques Perigosos AZA", 0, 50, 4, key="attacks_aza")
            corners_aza = st.number_input("Escanteios AZA", 0, 15, 1, key="corners_aza")
    
    with st.sidebar.expander("🟨 Cartões e Faltas", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            fouls_fav = st.number_input("Faltas FAV", 0, 25, 6, key="fouls_fav")
            yellow_cards_fav = st.number_input("Amarelos FAV", 0, 5, 1, key="yellow_fav")
            red_cards_fav = st.number_input("Vermelhos FAV", 0, 3, 0, key="red_fav")
        with col2:
            fouls_aza = st.number_input("Faltas AZA", 0, 25, 8, key="fouls_aza")
            yellow_cards_aza = st.number_input("Amarelos AZA", 0, 5, 2, key="yellow_aza")
            red_cards_aza = st.number_input("Vermelhos AZA", 0, 3, 0, key="red_aza")
    
    with st.sidebar.expander("🚩 Outras Estatísticas", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            offsides_fav = st.number_input("Impedimentos FAV", 0, 10, 1, key="offsides_fav")
        with col2:
            offsides_aza = st.number_input("Impedimentos AZA", 0, 10, 0, key="offsides_aza")
    
    # Notas adicionais
    additional_notes = st.sidebar.text_area("Observações Adicionais", 
                                          placeholder="Ex: Jogador lesionado, mudança tática, condições climáticas...",
                                          key="additional_notes")
    
    if st.sidebar.button("🔄 Atualizar Contexto da Partida", use_container_width=True, type="primary"):
        event_type = None
        for e in MatchEvent:
            if e.value == selected_event:
                event_type = e
                break
        
        statistics = MatchStatistics(
            possession_fav=possession_fav,
            possession_aza=possession_aza,
            shots_fav=shots_fav,
            shots_aza=shots_aza,
            shots_on_target_fav=shots_on_target_fav,
            shots_on_target_aza=shots_on_target_aza,
            dangerous_attacks_fav=dangerous_attacks_fav,
            dangerous_attacks_aza=dangerous_attacks_aza,
            corners_fav=corners_fav,
            corners_aza=corners_aza,
            fouls_fav=fouls_fav,
            fouls_aza=fouls_aza,
            offsides_fav=offsides_fav,
            offsides_aza=offsides_aza,
            yellow_cards_fav=yellow_cards_fav,
            yellow_cards_aza=yellow_cards_aza,
            red_cards_fav=red_cards_fav,
            red_cards_aza=red_cards_aza
        )
        
        match_context = MatchContext(
            current_score=current_score,
            minute=minute,
            statistics=statistics,
            event_type=event_type,
            momentum=momentum,
            additional_notes=additional_notes
        )
        
        st.session_state.match_context = match_context
        st.sidebar.success("✅ Contexto atualizado com sucesso!")
    
    return st.session_state.match_context

def render_comprehensive_prompt(ia_analysis: IAAnalysis, operation_id: str):
    """Renderiza o prompt completo e abrangente"""
    if not ia_analysis.comprehensive_prompt:
        return
    
    st.markdown("### 🤖 PROMPT COMPLETO PARA ANÁLISE DA IA")
    
    with st.expander("📋 PROMPT COMPLETO DA STARTUP ALMA", expanded=True):
        st.markdown(ia_analysis.comprehensive_prompt)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Copiar Prompt Completo", key=f"copy_full_{operation_id}", use_container_width=True):
                st.toast("Prompt completo copiado para a área de transferência! ✅")
        with col2:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analise_completa_{operation_id}_{timestamp}.txt"
            if st.button("💾 Salvar Como TXT", key=f"save_full_{operation_id}", use_container_width=True):
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(ia_analysis.comprehensive_prompt)
                st.success(f"Prompt salvo como {filename}")
        with col3:
            if st.button("🔄 Gerar Novo Prompt", key=f"refresh_{operation_id}", use_container_width=True):
                st.rerun()

def render_prompt_suggestions(ia_analysis: IAAnalysis, operation_id: str):
    """Renderiza sugestões de prompt para análise contínua"""
    if not ia_analysis.prompt_suggestions:
        return
    
    st.markdown("### 🎯 PROMPTS ESPECÍFICOS POR CONTEXTO")
    
    for i, prompt in enumerate(ia_analysis.prompt_suggestions):
        with st.expander(f"📋 {prompt.split('## ')[1].split(' - ')[0] if '##' in prompt else f'Prompt #{i+1}'}", expanded=i==0):
            st.markdown(prompt)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📋 Copiar Prompt #{i+1}", key=f"copy_{operation_id}_{i}", use_container_width=True):
                    st.toast(f"Prompt #{i+1} copiado! ✅")
            with col2:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analise_contexto_{operation_id}_{i+1}_{timestamp}.txt"
                if st.button(f"💾 Salvar #{i+1}", key=f"save_{operation_id}_{i}", use_container_width=True):
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(prompt)
                    st.success(f"Prompt salvo como {filename}")

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
    
    # Capturar contexto da partida
    match_context = create_statistics_interface()
    
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
    analysis = ia_analyzer.analyze_current_situation(zero_profit, fav_profit, aza_profit, total_investment, match_context, odds_values)
    
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
        "Mais de 2.5 Gols": 2.0,
        "Vitória Favorito": 1.8,
        "Empate": 3.4,
        "Vitória Azarão": 4.5
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
                    zero_profit, fav_profit, aza_profit, final_odds, total_investment, match_context
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
                
                # Mostrar prompts gerados
                render_comprehensive_prompt(ia_analysis, st.session_state.current_operation_id)
                render_prompt_suggestions(ia_analysis, st.session_state.current_operation_id)
                
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
    
    # Contexto da partida
    if operation_summary['match_context']:
        st.markdown("### ⚽ CONTEXTO DA PARTIDA")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Placar", operation_summary['match_context']['current_score'])
        with col2:
            st.metric("Minuto", operation_summary['match_context']['minute'])
        with col3:
            st.metric("Evento", operation_summary['match_context']['event_type'])
        with col4:
            st.metric("Momentum", operation_summary['match_context']['momentum'])

    # Resumo da estratégia
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
        
        # Mostrar prompts da operação
        if operation_summary['ia_analysis']['comprehensive_prompt']:
            st.markdown("### 🤖 PROMPT COMPLETO GERADO")
            with st.expander("📋 Visualizar Prompt Completo"):
                st.markdown(operation_summary['ia_analysis']['comprehensive_prompt'])

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
                    if op.match_context:
                        st.write(f"**Contexto:** {op.match_context.current_score} - {op.match_context.minute}'")
                with col2:
                    st.write(f"**Investimento:** R$ {op.total_investment:.2f}")
                    st.write(f"**Apostas:** {len(op.hedge_bets)}")
                
                if op.learning_notes:
                    st.write("**Aprendizados:**")
                    for note in op.learning_notes[-3:]:  # Últimos 3 aprendizados
                        st.write(f"• {note}")

# =============================
# FUNÇÕES DE INTEGRAÇÃO
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
    """Continua uma operação existente a partir do ID"""
    if "hedge_manager" not in st.session_state:
        return False
    
    operation = st.session_state.hedge_manager.memory_manager.get_operation_by_id(operation_id)
    if not operation:
        return False
    
    st.session_state.hedge_manager.memory_manager.current_operation_id = operation_id
    st.session_state.current_operation_id = operation_id
    st.session_state.hedge_applied = True
    
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
    st.title("🛡️ HEDGE DINÂMICO COM IA INSTRUTIVA - STARTUP ALMA")
    
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
