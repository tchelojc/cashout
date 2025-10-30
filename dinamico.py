# dinamico.py (VERSÃO CORRIGIDA COM SISTEMA DE PROMPTS E BOTÕES DE CÓPIA)
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
# ENUMS E DATACLASSES SINCRONIZADOS
# =============================

class RedistributionStrategy(Enum):
    NO_GOAL = "Sem Gol"
    FAV_GOAL = "Gol do Favorito"
    AZA_GOAL = "Gol do Azarão"
    ZERO_ZERO = "0x0"
    ONE_ONE = "1x1"
    OVER_05_AZARAO = "Mais 0,5 Gols Azarão"

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
    AZA_DANGEROUS_ATTACK = "Ataque Perigoso Azarão"
    AZA_CORNER = "Escanteio Azarão"
    AZA_SHOT_ON_TARGET = "Finalização no Alvo Azarão"

@dataclass
class HedgeBet:
    bet_type: str
    amount: float
    odds: float
    description: str
    market: str
    stake_percentage: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

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
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

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
    momentum: str
    additional_notes: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

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
    
    def __post_init__(self):
        if self.learning_notes is None:
            self.learning_notes = []
        if self.generated_prompts is None:
            self.generated_prompts = []

# =============================
# SISTEMA DE ANÁLISE DE MINUTOS E ODDS
# =============================

class MinuteOddsAnalyzer:
    """Analisa as odds favoráveis baseadas no minuto da partida"""
    
    def __init__(self):
        self.minute_ranges = {
            "0-15": {"description": "Início da Partida", "focus": "Odds altas para resultados específicos"},
            "16-30": {"description": "Fase de Estudo", "focus": "Aguardando oportunidades"},
            "31-45": {"description": "Fim do 1º Tempo", "focus": "Odds favoráveis para gols"},
            "46-60": {"description": "Início do 2º Tempo", "focus": "Ajustes táticos"},
            "61-75": {"description": "Fase Decisiva", "focus": "Odds mais valorizadas"},
            "76-90": {"description": "Fim da Partida", "focus": "Proteções urgentes"},
            "91+": {"description": "Acréscimos", "focus": "Odds emergenciais"}
        }
    
    def get_favorable_odds_by_minute(self, minute: int, current_score: str, odds_values: Dict) -> Dict:
        """Retorna as odds mais favoráveis baseadas no minuto atual"""
        
        range_key = self._get_minute_range(minute)
        range_info = self.minute_ranges[range_key]
        
        favorable_odds = {}
        
        # Análise baseada no minuto e placar
        if minute <= 30:
            # Primeira fase - odds mais conservadoras
            if "Mais 0,5 Gols Azarão" in odds_values and odds_values["Mais 0,5 Gols Azarão"] > 1.8:
                favorable_odds["Mais 0,5 Gols Azarão"] = {
                    "odd": odds_values["Mais 0,5 Gols Azarão"],
                    "reason": "Boa oportunidade no início do jogo",
                    "rating": "⭐️⭐️⭐️⭐️"
                }
                
        elif 31 <= minute <= 45:
            # Fim do primeiro tempo - odds mais agressivas
            if current_score == "0x0":
                if "Ambas Marcam - Não" in odds_values and odds_values["Ambas Marcam - Não"] > 2.0:
                    favorable_odds["Ambas Marcam - Não"] = {
                        "odd": odds_values["Ambas Marcam - Não"],
                        "reason": "Jogo fechado, boa oportunidade",
                        "rating": "⭐️⭐️⭐️⭐️⭐️"
                    }
                    
        elif 46 <= minute <= 60:
            # Início do segundo tempo
            if "Dupla Chance X2" in odds_values and odds_values["Dupla Chance X2"] > 2.2:
                favorable_odds["Dupla Chance X2"] = {
                    "odd": odds_values["Dupla Chance X2"],
                    "reason": "Segundo tempo equilibrado",
                    "rating": "⭐️⭐️⭐️"
                }
                
        elif minute >= 61:
            # Fase final - proteções
            if "Mais 0,5 Gols Azarão" in odds_values and odds_values["Mais 0,5 Gols Azarão"] < 1.5:
                favorable_odds["Mais 0,5 Gols Azarão"] = {
                    "odd": odds_values["Mais 0,5 Gols Azarão"],
                    "reason": "Proteção essencial no final",
                    "rating": "⭐️⭐️⭐️⭐️⭐️"
                }
        
        # Sempre incluir Mais 0,5 Gols Azarão se a odd for favorável
        if "Mais 0,5 Gols Azarão" in odds_values and odds_values["Mais 0,5 Gols Azarão"] <= 2.1:
            favorable_odds["Mais 0,5 Gols Azarão"] = {
                "odd": odds_values["Mais 0,5 Gols Azarão"],
                "reason": "Proteção fundamental em qualquer momento",
                "rating": "⭐️⭐️⭐️⭐️⭐️"
            }
        
        return {
            "minute_range": range_key,
            "range_description": range_info["description"],
            "focus": range_info["focus"],
            "favorable_odds": favorable_odds
        }
    
    def _get_minute_range(self, minute: int) -> str:
        """Determina a faixa de minutos"""
        if minute <= 15: return "0-15"
        elif minute <= 30: return "16-30"
        elif minute <= 45: return "31-45"
        elif minute <= 60: return "46-60"
        elif minute <= 75: return "61-75"
        elif minute <= 90: return "76-90"
        else: return "91+"
    
    def generate_minute_analysis_prompt(self, minute: int, current_score: str, odds_values: Dict) -> str:
        """Gera prompt de análise baseado no minuto"""
        analysis = self.get_favorable_odds_by_minute(minute, current_score, odds_values)
        
        prompt = f"""
## ⏰ ANÁLISE POR MINUTO - SISTEMA DINÂMICO

### 📊 CONTEXTO TEMPORAL
- **Minuto Atual:** {minute}'
- **Faixa de Minutos:** {analysis['minute_range']} - {analysis['range_description']}
- **Foco Recomendado:** {analysis['focus']}
- **Placar Atual:** {current_score}

### 🎯 ODDS FAVORÁVEIS IDENTIFICADAS
"""
        
        if analysis['favorable_odds']:
            for market, info in analysis['favorable_odds'].items():
                prompt += f"- **{market}:** Odd {info['odd']:.2f} - {info['rating']}\n"
                prompt += f"  *Motivo:* {info['reason']}\n\n"
        else:
            prompt += "⚠️ *Nenhuma odd considerada favorável no momento*\n\n"
        
        prompt += f"""
### 🧠 SOLICITAÇÃO DE ANÁLISE

Baseado no minuto {minute}' e placar {current_score}, analise:

1. **OPORTUNIDADES POR TEMPO:**
   - Quais mercados têm melhor valor neste momento?
   - Como o minuto atual impacta as probabilidades?
   - Timing ideal para entrada

2. **PROTEÇÃO MAIS 0,5 GOLS AZARÃO:**
   - Viabilidade baseada no tempo decorrido
   - Ajustes necessários na estratégia
   - Momento ideal para proteção

3. **ESTRATÉGIA TEMPORAL:**
   - Alocação por faixa de minutos
   - Gerenciamento de risco temporal
   - Preparação para próximos minutos

**Forneça recomendações específicas considerando o minuto {minute}' de jogo.**
"""
        
        return prompt

# =============================
# SISTEMA DE RETORNO PÓS-GOL
# =============================

class PostGoalAnalyzer:
    """Analisa os retornos financeiros após gols marcados"""
    
    def __init__(self):
        self.scenario_analysis = {
            "1x0_FAV": {
                "description": "Vitória do Favorito 1x0",
                "protected_by": ["Mais 0,5 Gols Azarão", "Dupla Chance X2"],
                "risk": "Médio",
                "recommendation": "Manter proteção azarão"
            },
            "1x1_FAV": {
                "description": "Empate 1x1 com gol do favorito primeiro", 
                "protected_by": ["Mais 0,5 Gols Azarão"],
                "risk": "Baixo",
                "recommendation": "Proteção ativa - considerar cashout"
            },
            "2x0_FAV": {
                "description": "Vitória convincente do favorito",
                "protected_by": ["Mais 0,5 Gols Azarão", "Ambas Marcam - Não"],
                "risk": "Alto", 
                "recommendation": "Reforçar proteção azarão"
            },
            "0x1_AZA": {
                "description": "Vitória do azarão 0x1",
                "protected_by": ["Mais 0,5 Gols Azarão", "Dupla Chance X2"],
                "risk": "Baixo",
                "recommendation": "Proteção funcionando - avaliar hedge"
            },
            "1x1_AZA": {
                "description": "Empate 1x1 com gol do azarão primeiro",
                "protected_by": ["Mais 0,5 Gols Azarão"],
                "risk": "Muito Baixo", 
                "recommendation": "Proteção total - considerar realização"
            },
            "0x2_AZA": {
                "description": "Vitória convincente do azarão",
                "protected_by": ["Mais 0,5 Gols Azarão", "Dupla Chance X2"],
                "risk": "Muito Baixo",
                "recommendation": "Proteção máxima - realizar lucros"
            }
        }
    
    def calculate_post_goal_returns(self, goal_type: str, minute: int, current_profits: Dict) -> Dict:
        """Calcula retornos após gol marcado"""
        
        base_scenario = f"{goal_type}_GOL"
        scenario_key = self._get_scenario_key(goal_type, minute)
        
        returns_analysis = {
            "scenario": scenario_key,
            "description": self.scenario_analysis[scenario_key]["description"],
            "risk_level": self.scenario_analysis[scenario_key]["risk"],
            "recommendation": self.scenario_analysis[scenario_key]["recommendation"],
            "protected_markets": self.scenario_analysis[scenario_key]["protected_by"],
            "minute_impact": self._calculate_minute_impact(minute),
            "returns_breakdown": self._calculate_returns_breakdown(goal_type, current_profits)
        }
        
        return returns_analysis
    
    def _get_scenario_key(self, goal_type: str, minute: int) -> str:
        """Determina a chave do cenário baseado no tipo de gol e minuto"""
        if goal_type == "FAV":
            if minute <= 30:
                return "1x0_FAV"
            else:
                return "2x0_FAV"
        else:  # AZA goal
            if minute <= 30:
                return "0x1_AZA" 
            else:
                return "0x2_AZA"
    
    def _calculate_minute_impact(self, minute: int) -> str:
        """Calcula o impacto do minuto no cenário"""
        if minute <= 25:
            return "Alto impacto - jogo ainda aberto"
        elif minute <= 45:
            return "Médio impacto - fim do primeiro tempo próximo"
        elif minute <= 70:
            return "Impacto moderado - segundo tempo em andamento"
        else:
            return "Baixo impacto - final de jogo"
    
    def _calculate_returns_breakdown(self, goal_type: str, current_profits: Dict) -> Dict:
        """Calcula detalhamento dos retornos"""
        if goal_type == "FAV":
            return {
                "current_profit": current_profits.get("1x1_FAV", 0),
                "protected_profit": current_profits.get("1x1_FAV", 0) * 0.7,  # 70% protegido
                "max_risk": current_profits.get("0x1_AZA", 0),
                "recommended_action": "Manter proteção azarão"
            }
        else:  # AZA goal
            return {
                "current_profit": current_profits.get("1x1_AZA", 0), 
                "protected_profit": current_profits.get("1x1_AZA", 0) * 0.9,  # 90% protegido
                "max_risk": current_profits.get("1x0_FAV", 0),
                "recommended_action": "Avaliar realização parcial"
            }
    
    def generate_post_goal_prompt(self, goal_type: str, minute: int, current_score: str, current_profits: Dict, odds_values: Dict) -> str:
        """Gera prompt completo pós-gol - VERSÃO CORRIGIDA (5 parâmetros)"""
        analysis = self.calculate_post_goal_returns(goal_type, minute, current_profits)
        
        prompt = f"""
## ⚽ ANÁLISE PÓS-GOL - SISTEMA DINÂMICO

### 🎉 GOL REGISTRADO
- **Time:** {'FAVORITO' if goal_type == 'FAV' else 'AZARÃO'} 
- **Minuto:** {minute}'
- **Placar Atual:** {current_score}
- **Cenário Atual:** {analysis['scenario']}
- **Descrição:** {analysis['description']}

### 📊 IMPACTO FINANCEIRO
- **Retorno Atual:** R$ {analysis['returns_breakdown']['current_profit']:.2f}
- **Retorno Protegido:** R$ {analysis['returns_breakdown']['protected_profit']:.2f}
- **Nível de Risco:** {analysis['risk_level']}
- **Impacto Temporal:** {analysis['minute_impact']}

### 🛡️ PROTEÇÕES ATIVAS
"""
        
        for market in analysis['protected_markets']:
            if market in odds_values:
                prompt += f"- ✅ **{market}:** Odd {odds_values[market]:.2f} (Proteção Ativa)\n"
        
        prompt += f"""
### 🧠 SOLICITAÇÃO DE ANÁLISE PÓS-GOL

Baseado no gol do { 'FAVORITO' if goal_type == 'FAV' else 'AZARÃO'} aos {minute}' (Placar: {current_score}), analise:

1. **REAVALIAÇÃO DE RISCO:**
   - Como o gol impacta a estratégia atual?
   - Necessidade de ajustes nas proteções?
   - Exposição residual

2. **OPORTUNIDADES EMERGENTES:**
   - Novos mercados com valor após o gol
   - Ajustes na alocação
   - Timing para novas entradas

3. **PROTEÇÃO MAIS 0,5 GOLS AZARÃO:**
   - Viabilidade atualizada
   - Ajustes necessários
   - Momento ideal para realização

**Forneça plano de ação específico para os próximos 15 minutos.**
"""
        
        return prompt

# =============================
# SISTEMA DE PROTEÇÕES DINÂMICAS
# =============================

class DynamicProtectionSystem:
    """Sistema de proteções dinâmicas baseadas em eventos"""
    
    def __init__(self):
        self.protection_strategies = {
            "MAIS_25_GOLS": {
                "name": "Mais 2,5 Gols Partida",
                "description": "Foco em jogos abertos com muitos gols",
                "conditions": ["jogo aberto", "ambas equipes atacando", "primeiro tempo movimentado"],
                "recommended_odds": 2.0,
                "risk": "Alto"
            },
            "PROTECAO_HEDGE_AZARAO": {
                "name": "Proteção Dinâmica com Hedge Azarão", 
                "description": "Proteção máxima com foco no azarão marcar",
                "conditions": ["azarão criando chances", "favorito defensivo", "jogo equilibrado"],
                "recommended_odds": 1.8,
                "risk": "Médio"
            },
            "MENOS_25_GOLS": {
                "name": "Menos 2,5 Gols Partida",
                "description": "Proteção para jogos fechados",
                "conditions": ["jogo truncado", "poucas finalizações", "equilíbrio defensivo"],
                "recommended_odds": 1.6,
                "risk": "Baixo"
            }
        }
    
    def recommend_protection_strategy(self, match_context: MatchContext, current_profits: Dict, odds_values: Dict) -> Dict:
        """Recomenda estratégia de proteção baseada no contexto"""
        
        strategies = []
        
        # Analisar contexto para recomendações
        stats = match_context.statistics
        
        # Estratégia 1: Mais 2,5 Gols
        if (stats.shots_fav + stats.shots_aza) > 10 and match_context.minute <= 60:
            strategies.append({
                "strategy": "MAIS_25_GOLS",
                "name": self.protection_strategies["MAIS_25_GOLS"]["name"],
                "reason": "Jogo movimentado com muitas finalizações",
                "confidence": 0.7,
                "recommended_markets": ["Mais 2,5 Gols", "Ambas Marcam - Sim"],
                "expected_impact": "Alto potencial, risco elevado"
            })
        
        # Estratégia 2: Proteção Hedge Azarão (SEMPRE RECOMENDADA)
        if stats.shots_aza >= 2 or stats.dangerous_attacks_aza >= 3:
            strategies.append({
                "strategy": "PROTECAO_HEDGE_AZARAO", 
                "name": self.protection_strategies["PROTECAO_HEDGE_AZARAO"]["name"],
                "reason": "Azarão criando oportunidades consistentes",
                "confidence": 0.9,
                "recommended_markets": ["Mais 0,5 Gols Azarão", "Dupla Chance X2"],
                "expected_impact": "Proteção sólida com bom potencial"
            })
        
        # Estratégia 3: Menos 2,5 Gols
        if (stats.shots_fav + stats.shots_aza) < 6 and match_context.minute >= 60:
            strategies.append({
                "strategy": "MENOS_25_GOLS",
                "name": self.protection_strategies["MENOS_25_GOLS"]["name"], 
                "reason": "Jogo fechado com poucas chances",
                "confidence": 0.8,
                "recommended_markets": ["Menos 2,5 Gols", "Ambas Marcam - Não"],
                "expected_impact": "Proteção conservadora"
            })
        
        # Ordenar por confiança
        strategies.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "recommended_strategies": strategies,
            "top_recommendation": strategies[0] if strategies else None,
            "analysis_timestamp": datetime.now()
        }
    
    def generate_protection_prompt(self, match_context: MatchContext, current_profits: Dict, odds_values: Dict) -> str:
        """Gera prompt para análise de proteções dinâmicas"""
        
        recommendation = self.recommend_protection_strategy(match_context, current_profits, odds_values)
        top_strategy = recommendation["top_recommendation"]
        
        prompt = f"""
## 🛡️ ANÁLISE DE PROTEÇÕES DINÂMICAS

### 📊 CONTEXTO PARA PROTEÇÃO
- **Minuto:** {match_context.minute}'
- **Placar:** {match_context.current_score}
- **Evento:** {match_context.event_type.value}
- **Momentum:** {match_context.momentum}

### 🎯 ESTRATÉGIA RECOMENDADA
**{top_strategy['name']}**
- *Motivo:* {top_strategy['reason']}
- *Confiança:* {top_strategy['confidence']:.0%}
- *Impacto Esperado:* {top_strategy['expected_impact']}

### 💰 MERCADOS RECOMENDADOS
"""
        
        for market in top_strategy["recommended_markets"]:
            if market in odds_values:
                prompt += f"- **{market}:** Odd {odds_values[market]:.2f}\n"
        
        prompt += f"""
### 🧠 SOLICITAÇÃO DE ANÁLISE DE PROTEÇÃO

Baseado no contexto atual (minuto {match_context.minute}', placar {match_context.current_score}), analise:

1. **VIABILIDADE DA ESTRATÉGIA {top_strategy['name']}:**
   - Adequação ao momento do jogo
   - Relação risco-retorno
   - Timing de implementação

2. **ALOCAÇÃO OTIMIZADA:**
   - Distribuição por mercado
   - Tamanho ideal das posições
   - Proteções complementares

3. **PLANO DE CONTINGÊNCIA:**
   - Gatilhos para ajustes
   - Condições de saída
   - Gerenciamento de cenários adversos

**Forneça plano detalhado de implementação da proteção dinâmica.**
"""
        
        return prompt

# =============================
# SISTEMA DE PROMPT PADRÃO PARA IA
# =============================

class IAPromptGenerator:
    """Gera prompts padronizados para análise da IA"""
    
    @staticmethod
    def generate_standard_protection_prompt(zero_profit: float, fav_profit: float, aza_profit: float, 
                                          odds_values: Dict, minute: int, current_score: str,
                                          statistics: Dict) -> str:
        """Gera prompt padrão para análise de proteção"""
        
        prompt = f"""
## 🎯 ANÁLISE DE PROTEÇÃO DINÂMICA - SISTEMA CONQUISTADOR

### 📊 CONTEXTO ATUAL DA PARTIDA
- **Minuto:** {minute}'
- **Placar:** {current_score}
- **Momento do Jogo:** {'Primeiro Tempo' if minute <= 45 else 'Segundo Tempo'}

### 📈 ESTATÍSTICAS DO AZARÃO
- **Finalizações:** {statistics.get('shots_aza', 0)} ({statistics.get('shots_on_target_aza', 0)} no alvo)
- **Ataques Perigosos:** {statistics.get('dangerous_attacks_aza', 0)}
- **Escanteios:** {statistics.get('corners_aza', 0)}

### 💰 SITUAÇÃO FINANCEIRA ATUAL
- **Lucro 0x0:** R$ {zero_profit:.2f}
- **Lucro 1x1 FAV:** R$ {fav_profit:.2f}
- **Lucro 1x1 AZA:** R$ {aza_profit:.2f}

### 🎰 ODDS DISPONÍVEIS PARA PROTEÇÃO
"""
        
        # Adicionar odds disponíveis
        for market, odd in odds_values.items():
            if "Mais 0,5 Gols Azarão" in market:
                prompt += f"- **🎯 {market}:** {odd:.2f} ⭐\n"
            else:
                prompt += f"- **{market}:** {odd:.2f}\n"
        
        prompt += f"""
### 🧠 SOLICITAÇÃO DE ANÁLISE COMPLETA

Baseado no contexto acima, forneça uma análise detalhada considerando:

1. **ANÁLISE DE RISCO ATUAL:**
   - Qual o nível de exposição nos diferentes cenários?
   - Quais são os principais riscos identificados?
   - Como o minuto {minute}' impacta a estratégia?

2. **PROTEÇÃO MAIS 0,5 GOLS AZARÃO:**
   - Viabilidade baseada nas estatísticas do azarão
   - Valor da odd atual ({odds_values.get('Mais 0,5 Gols Azarão', 0):.2f})
   - Timing ideal para implementação

3. **ESTRATÉGIA DE HEDGE RECOMENDADA:**
   - Combinação ideal de mercados
   - Alocação de capital por proteção
   - Sequência de implementação

4. **PLANO DE CONTINGÊNCIA:**
   - Gatilhos para ajustes
   - Condições de saída
   - Gerenciamento de cenários adversos

**Forneça recomendações específicas e acionáveis para os próximos 15-20 minutos de jogo.**
"""
        
        return prompt
    
    @staticmethod
    def generate_goal_analysis_prompt(goal_type: str, minute: int, current_score: str, 
                                    current_profits: Dict, odds_values: Dict) -> str:
        """Gera prompt para análise pós-gol - VERSÃO ESPECÍFICA POR TIPO DE GOL"""
        
        # 🔥 CORREÇÃO: GARANTIR que o placar está atualizado
        if current_score == "0x0":
            # Se ainda está 0x0, atualizar baseado no gol
            if goal_type == "FAV":
                current_score = "1x0"
            else:
                current_score = "0x1"
        
        # 🔥 PROMPT ESPECÍFICO PARA GOL DO AZARÃO
        if goal_type == "AZA":
            return IAPromptGenerator._generate_azarao_goal_prompt(minute, current_score, current_profits, odds_values)
        else:
            return IAPromptGenerator._generate_favorito_goal_prompt(minute, current_score, current_profits, odds_values)
    
    @staticmethod
    def _generate_azarao_goal_prompt(minute: int, current_score: str, current_profits: Dict, odds_values: Dict) -> str:
        """Gera prompt ESPECÍFICO para gol do azarão"""
        
        prompt = f"""
## ⚽ ANÁLISE PÓS-GOL DO AZARÃO - SISTEMA DINÂMICO

### 🎉 GOL DO AZARÃO REGISTRADO!
- **⏰ Minuto:** {minute}'
- **📊 Placar Atual:** {current_score}
- **🎯 Situação:** Azarão abriu o placar

### 💰 IMPACTO FINANCEIRO IMEDIATO - GOL AZARÃO
- **📉 Lucro 0x0:** R$ {current_profits.get('0x0', 0):.2f}
- **📉 Lucro 1x1 FAV:** R$ {current_profits.get('1x1_FAV', 0):.2f}
- **📈 Lucro 1x1 AZA:** R$ {current_profits.get('1x1_AZA', 0):.2f}

### 🛡️ PROTEÇÕES ATIVAS APÓS GOL AZARÃO
"""
        
        # Destaque específico para proteções relevantes pós-gol azarão
        protection_marks = {
            "Mais 0,5 Gols Azarão": "✅ **PROTEÇÃO ATIVADA**",
            "Dupla Chance X2": "✅ **PROTEÇÃO REFORÇADA**", 
            "Ambas Marcam - Sim": "📈 **VALOR AUMENTADO**",
            "Vitória Favorito": "📉 **RISCO ELEVADO**",
            "Menos 2,5 Gols": "⚠️ **CENÁRIO COMPROMETIDO**"
        }
        
        for market, odd in odds_values.items():
            mark = protection_marks.get(market, "")
            prompt += f"- **{market}:** {odd:.2f} {mark}\n"
        
        prompt += f"""
### 🧠 SOLICITAÇÃO DE ANÁLISE ESPECÍFICA - GOL AZARÃO

Baseado no **GOL DO AZARÃO** aos {minute}' (Placar: {current_score}), forneça análise detalhada:

## 🎯 CENÁRIOS PÓS-GOL AZARÃO:

**1. 📊 REAVALIAÇÃO DE RISCO IMEDIATA:**
- Como o gol do azarão impacta a exposição atual?
- Quais cenários se tornaram MAIS prováveis: 0x2, 1x2, 0x1?
- Quais cenários se tornaram MENOS prováveis: 2x0, 3x0, 1x0?
- Nível de urgência para ajustes (Alto/Médio/Baixo)

**2. 🛡️ EFICÁCIA DAS PROTEÇÕES:**
- A proteção "Mais 0,5 Gols Azarão" já está realizando lucro?
- "Dupla Chance X2" agora cobre empate OU vitória azarão - como aproveitar?
- Quais proteções devem ser REFORÇADAS imediatamente?
- Quais proteções podem ser REDUZIDAS?

**3. 💡 OPORTUNIDADES ESTRATÉGICAS:**
- Odds que se tornaram SUBVALORIZADAS após o gol?
- Mercados com melhor relação risco/retorno agora?
- Timing para NOVAS entradas (imediato/aguardar)?
- Alocação ideal considerando o novo contexto

**4. ⚡ PLANO DE AÇÃO PRÁTICO:**
- **PRÓXIMOS 5 MINUTOS:** Ações críticas imediatas
- **PRÓXIMOS 10-15 MINUTOS:** Estratégia de médio prazo  
- **GATILHOS** para ajustes adicionais
- **CONDIÇÕES DE SAÍDA** para realizar lucros

**5. 📈 ANÁLISE COMPORTAMENTAL:**
- Como o favorito tende a reagir após sofrer gol?
- Probabilidade de reação imediata do favorito?
- Cenários de "virada" vs. "conformação"?

## 🎲 PROBABILIDADES ESTIMADAS PÓS-GOL AZARÃO:
- Empate 1x1: ?%
- Vitória Azarão 0x2: ?% 
- Virada Favorito 2x1: ?%
- Manutenção 0x1: ?%

**Forneça recomendações ESPECÍFICAS e ACIONÁVEIS baseadas exclusivamente no CENÁRIO DE GOL DO AZARÃO.**
"""
        
        return prompt
    
    @staticmethod
    def _generate_favorito_goal_prompt(minute: int, current_score: str, current_profits: Dict, odds_values: Dict) -> str:
        """Gera prompt ESPECÍFICO para gol do favorito"""
        
        prompt = f"""
## ⚽ ANÁLISE PÓS-GOL DO FAVORITO - SISTEMA DINÂMICO

### 🎉 GOL DO FAVORITO REGISTRADO!
- **⏰ Minuto:** {minute}'
- **📊 Placar Atual:** {current_score}
- **🎯 Situação:** Favorito abriu o placar

### 💰 IMPACTO FINANCEIRO IMEDIATO - GOL FAVORITO
- **📉 Lucro 0x0:** R$ {current_profits.get('0x0', 0):.2f}
- **📈 Lucro 1x1 FAV:** R$ {current_profits.get('1x1_FAV', 0):.2f}
- **📉 Lucro 1x1 AZA:** R$ {current_profits.get('1x1_AZA', 0):.2f}

### 🛡️ PROTEÇÕES ATIVAS APÓS GOL FAVORITO
"""
        
        # Destaque específico para proteções relevantes pós-gol favorito
        protection_marks = {
            "Mais 0,5 Gols Azarão": "⚠️ **PROTEÇÃO MANTIDA**",
            "Dupla Chance 1X": "✅ **PROTEÇÃO CONSOLIDADA**",
            "Ambas Marcam - Não": "📈 **VALOR AUMENTADO**",
            "Vitória Favorito": "✅ **APOSTA ATIVADA**",
            "Mais 2,5 Gols": "📈 **POTENCIAL AUMENTADO**"
        }
        
        for market, odd in odds_values.items():
            mark = protection_marks.get(market, "")
            prompt += f"- **{market}:** {odd:.2f} {mark}\n"
        
        prompt += f"""
### 🧠 SOLICITAÇÃO DE ANÁLISE ESPECÍFICA - GOL FAVORITO

Baseado no **GOL DO FAVORITO** aos {minute}' (Placar: {current_score}), forneça análise detalhada:

## 🎯 CENÁRIOS PÓS-GOL FAVORITO:

**1. 📊 REAVALIAÇÃO DE RISCO IMEDIATA:**
- Como o gol do favorito impacta a exposição atual?
- Quais cenários se tornaram MAIS prováveis: 2x0, 3x0, 2x1?
- Quais cenários se tornaram MENOS prováveis: 0x1, 1x2, 0x0?
- Nível de urgência para ajustes (Alto/Médio/Baixo)

**2. 🛡️ EFICÁCIA DAS PROTEÇÕES:**
- A proteção "Mais 0,5 Gols Azarão" ainda é necessária?
- "Dupla Chance 1X" agora cobre vitória OU empate - como otimizar?
- Quais proteções devem ser MANTIDAS?
- Quais proteções podem ser AJUSTADAS?

**3. 💡 OPORTUNIDADES ESTRATÉGICAS:**
- Odds que se tornaram SOBREVALORIZADAS após o gol?
- Mercados com melhor valor para hedge?
- Timing para realizar lucros parciais?
- Alocação ideal considerando dominância do favorito

**4. ⚡ PLANO DE AÇÃO PRÁTICO:**
- **PRÓXIMOS 5 MINUTOS:** Ações recomendadas
- **PRÓXIMOS 10-15 MINUTOS:** Estratégia consolidada
- **GATILHOS** para proteções adicionais
- **CONDIÇÕES** para cashout parcial

**5. 📈 ANÁLISE COMPORTAMENTAL:**
- Como o azarão tende a reagir após sofrer gol?
- Probabilidade de reação do azarão?
- Cenários de "expansão" vs. "contensão"?

## 🎲 PROBABILIDADES ESTIMADAS PÓS-GOL FAVORITO:
- Vitória 2x0: ?%
- Empate 1x1: ?%
- Vitória 2x1: ?%
- Manutenção 1x0: ?%

**Forneça recomendações ESPECÍFICAS e ACIONÁVEIS baseadas exclusivamente no CENÁRIO DE GOL DO FAVORITO.**
"""
        
        return prompt

# =============================
# ANALISADOR DE IA SINCRONIZADO
# =============================

class IAAnalyzer:
    def __init__(self):
        self.risk_profiles = {
            RiskProfile.CONSERVATIVE: {"max_risk": 0.2, "protection_focus": 0.7},
            RiskProfile.MODERATE: {"max_risk": 0.3, "protection_focus": 0.5},
            RiskProfile.AGGRESSIVE: {"max_risk": 0.4, "protection_focus": 0.3}
        }
        self.minute_analyzer = MinuteOddsAnalyzer()
        self.protection_system = DynamicProtectionSystem()
        self.prompt_generator = IAPromptGenerator()
    
    def analyze_current_situation(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                                total_investment: float = 100, match_context: MatchContext = None,
                                odds_values: Dict = None) -> IAAnalysis:
        """Analisa a situação atual com foco em sincronização"""
        
        profits = [zero_profit, fav_profit, aza_profit]
        max_profit = max(profits)
        min_profit = min(profits)
        volatility = abs(max_profit - min_profit)
        
        # Ajustar análise baseado no contexto
        context_adjustment = self._adjust_for_match_context(match_context, volatility)
        adjusted_volatility = volatility * context_adjustment['volatility_multiplier']
        
        # Determinar perfil de risco
        if adjusted_volatility < 5:
            profile = RiskProfile.CONSERVATIVE
            strategy = "Proteção Máxima com Mais 0,5 Gols Azarão"
            insights = ["Baixa volatilidade entre cenários", "Risco controlado", "Foco em proteção"] + context_adjustment['insights']
            action_plan = self._generate_conservative_actions(zero_profit, fav_profit, aza_profit, total_investment, match_context)
            expected_outcome = "Proteção de 70% do lucro máximo com risco mínimo"
            
        elif adjusted_volatility < 15:
            profile = RiskProfile.MODERATE
            strategy = "Hedge Balanceado com Proteção Azarão"
            insights = ["Volatilidade moderada", "Oportunidade de hedge equilibrado", "Risco calculado"] + context_adjustment['insights']
            action_plan = self._generate_moderate_actions(zero_profit, fav_profit, aza_profit, total_investment, match_context)
            expected_outcome = "Balanceamento entre proteção e oportunidade (50/50)"
            
        else:
            profile = RiskProfile.AGGRESSIVE
            strategy = "Hedge Oportunista com Foco Azarão"
            insights = ["Alta volatilidade", "Potencial para ganhos significativos", "Risco elevado"] + context_adjustment['insights']
            action_plan = self._generate_aggressive_actions(zero_profit, fav_profit, aza_profit, total_investment, match_context)
            expected_outcome = "Busca por maximização de lucros com aceitação de risco"
        
        # Calcular confiança
        positive_profits = sum(1 for p in profits if p > 0)
        confidence = min(0.95, 0.5 + (positive_profits * 0.15) * context_adjustment['confidence_multiplier'])
        
        # Gerar prompts
        prompt_suggestions = self._generate_prompt_suggestions(profile, match_context, profits, odds_values)
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
        """Ajusta análise baseado no contexto atual da partida"""
        if not match_context:
            return {
                'volatility_multiplier': 1.0,
                'confidence_multiplier': 1.0,
                'insights': ["Partida ainda não iniciada"]
            }
        
        insights = []
        volatility_multiplier = 1.0
        confidence_multiplier = 1.0
        
        # Análise temporal
        if match_context.minute <= 45:
            insights.append(f"⏰ Primeiro tempo em andamento ({match_context.minute}')")
            if match_context.minute < 25:
                volatility_multiplier *= 0.8
            else:
                volatility_multiplier *= 1.2
        else:
            insights.append(f"⏰ Segundo tempo em andamento ({match_context.minute}')")
            volatility_multiplier *= 1.5
        
        # Análise de placar
        if match_context.current_score == "0x0":
            insights.append("📊 Placar 0x0 - Alta incerteza")
            volatility_multiplier *= 1.3
        else:
            insights.append(f"📊 Placar {match_context.current_score} - Cenário definido")
            confidence_multiplier *= 1.2
        
        # Análise de momentum
        if match_context.momentum == 'FAV':
            insights.append("📈 Momentum do favorito")
            confidence_multiplier *= 1.1
        elif match_context.momentum == 'AZA':
            insights.append("📉 Momentum do azarão")
            volatility_multiplier *= 1.4
        
        # Análise de eventos específicos para Mais 0,5 Gols Azarão
        if match_context.event_type in [MatchEvent.AZA_DANGEROUS_ATTACK, MatchEvent.AZA_CORNER, MatchEvent.AZA_SHOT_ON_TARGET]:
            insights.append("🎯 Azarão criando oportunidades - Forte candidato para Mais 0,5 Gols")
            volatility_multiplier *= 1.2
            confidence_multiplier *= 1.1
        
        # Análise estatística para Mais 0,5 Gols Azarão
        if match_context.statistics:
            stats = match_context.statistics
            if stats.shots_aza > 3 or stats.shots_on_target_aza > 1:
                insights.append("🎯 Azarão com finalizações - Bom cenário para Mais 0,5 Gols")
                volatility_multiplier *= 1.1
            if stats.dangerous_attacks_aza > 5:
                insights.append("⚡ Azarão com ataques perigosos - Probabilidade aumentada para gol")
                volatility_multiplier *= 1.15
        
        return {
            'volatility_multiplier': volatility_multiplier,
            'confidence_multiplier': confidence_multiplier,
            'insights': insights
        }
    
    def _generate_comprehensive_prompt(self, profile: RiskProfile, match_context: MatchContext, 
                                     profits: List[float], odds_values: Dict, action_plan: List[str]) -> str:
        """Gera prompt completo para análise da IA"""
        
        if not match_context:
            return self._generate_pre_match_prompt(profile, profits, odds_values, action_plan)
        
        stats = match_context.statistics
        
        # Gerar análise de minuto
        minute_analysis = self.minute_analyzer.get_favorable_odds_by_minute(
            match_context.minute, match_context.current_score, odds_values
        )
        
        prompt = f"""
## 🎯 ANÁLISE DINÂMICA SINCRONIZADA - SISTEMA CONQUISTADOR

### ⏰ CONTEXTO TEMPORAL
- **Minuto:** {match_context.minute}' ({minute_analysis['minute_range']})
- **Fase do Jogo:** {minute_analysis['range_description']}
- **Foco Recomendado:** {minute_analysis['focus']}

### ⚽ SITUAÇÃO DA PARTIDA
- **Placar Atual:** {match_context.current_score}
- **Evento Recente:** {match_context.event_type.value}
- **Momentum:** {match_context.momentum}

### 📈 ESTATÍSTICAS DETALHADAS:
- **POSSE DE BOLA:** Favorito {stats.possession_fav}% - Azarão {stats.possession_aza}%
- **FINALIZAÇÕES:** Favorito {stats.shots_fav} ({stats.shots_on_target_fav} no alvo) - Azarão {stats.shots_aza} ({stats.shots_on_target_aza} no alvo)
- **ATAQUES PERIGOSOS:** Favorito {stats.dangerous_attacks_fav} - Azarão {stats.dangerous_attacks_aza}
- **ESCANTEIOS:** Favorito {stats.corners_fav} - Azarão {stats.corners_aza}

### 🎯 ODDS FAVORÁVEIS POR MINUTO
"""
        
        if minute_analysis['favorable_odds']:
            for market, info in minute_analysis['favorable_odds'].items():
                prompt += f"- **{market}:** {info['odd']:.2f} {info['rating']} - {info['reason']}\n"
        else:
            prompt += "⚠️ *Nenhuma odd identificada como favorável no momento*\n"

        prompt += f"""
### 🛡️ ANÁLISE ESPECÍFICA PARA MAIS 0,5 GOLS AZARÃO
**INDICADORES FAVORÁVEIS:**
- Finalizações do Azarão: {stats.shots_aza} (No alvo: {stats.shots_on_target_aza})
- Ataques Perigosos Azarão: {stats.dangerous_attacks_aza}
- Escanteios Azarão: {stats.corners_aza}
- **PROBABILIDADE ESTIMADA:** {self._calculate_azarao_goal_probability(stats, match_context.minute):.1f}%

### 💰 SITUAÇÃO FINANCEIRA ATUAL
**LUCROS POR CENÁRIO:**
- **0x0:** R$ {profits[0]:.2f}
- **1x1 FAV:** R$ {profits[1]:.2f}
- **1x1 AZA:** R$ {profits[2]:.2f}

**PERFIL E ESTRATÉGIA:**
- **Perfil de Risco:** {profile.value}
- **Estratégia Recomendada:** {profile.value}
"""
        
        # Adicionar odds disponíveis
        if odds_values:
            prompt += "\n### 🎰 ODDS ATUAIS DISPONÍVEIS\n"
            for market, odd in odds_values.items():
                if "Mais 0,5 Gols Azarão" in market:
                    prompt += f"- **🎯 {market}:** {odd:.2f} ⭐\n"
                else:
                    prompt += f"- **{market}:** {odd:.2f}\n"
        
        prompt += f"""
### 🧠 SOLICITAÇÃO DE ANÁLISE COMPLETA:

Baseado no contexto completo da partida (minuto {match_context.minute}', placar {match_context.current_score}), forneça:

1. **ANÁLISE TÁTICA DO JOGO:**
   - Equilíbrio das equipes baseado nas estatísticas
   - Dominância real vs. resultado
   - Fatores que podem influenciar o restante da partida

2. **PROBABILIDADES ATUALIZADAS - ESPECIALMENTE MAIS 0,5 GOLS AZARÃO:**
   - Probabilidade real do azarão marcar baseado nas estatísticas
   - Valor da odd atual para Mais 0,5 Gols Azarão
   - Cenários mais prováveis considerando o andamento

3. **ESTRATÉGIA DE INVESTIMENTO COM PROTEÇÃO AZARÃO:**
   - Distribuição ideal considerando a proteção do azarão
   - Oportunidades de value bet em Mais 0,5 Gols Azarão
   - Proteções necessárias e hedge natural

**Forneça recomendações específicas e acionáveis para a estratégia de Mais 0,5 Gols Azarão.**
"""
        
        return prompt
    
    def _calculate_azarao_goal_probability(self, stats: MatchStatistics, minute: int) -> float:
        """Calcula probabilidade estimada do azarão marcar"""
        base_prob = 35.0
        
        # Ajustes baseados em estatísticas
        if stats.shots_on_target_aza > 0:
            base_prob += stats.shots_on_target_aza * 8
        
        if stats.dangerous_attacks_aza > 5:
            base_prob += (stats.dangerous_attacks_aza - 5) * 2
        
        if stats.corners_aza > 2:
            base_prob += (stats.corners_aza - 2) * 3
        
        # Ajuste temporal
        if minute > 60:
            base_prob += 15
        elif minute > 30:
            base_prob += 8
        
        return min(85.0, base_prob)
    
    def _generate_pre_match_prompt(self, profile: RiskProfile, profits: List[float], odds_values: Dict, action_plan: List[str]) -> str:
        """Gera prompt para análise pré-partida"""
        prompt = f"""
## 🎯 ANÁLISE PRÉ-PARTIDA - SISTEMA CONQUISTADOR

### 💰 SITUAÇÃO FINANCEIRA INICIAL
**LUCROS POR CENÁRIO:**
- **0x0:** R$ {profits[0]:.2f}
- **1x1 FAV:** R$ {profits[1]:.2f}
- **1x1 AZA:** R$ {profits[2]:.2f}

**PERFIL E ESTRATÉGIA:**
- **Perfil de Risco:** {profile.value}
- **Plano de Ação:** {', '.join(action_plan)}

### 🛡️ ESTRATÉGIA MAIS 0,5 GOLS AZARÃO
**PROTEÇÃO IMPLEMENTADA:** 
- ✅ Empates 1x1 onde azarão marca
- ✅ Vitórias 2x1 do favorito com gol de honra
- ✅ Qualquer resultado com gol do azarão
"""
        
        return prompt
    
    def _generate_prompt_suggestions(self, profile: RiskProfile, match_context: MatchContext, 
                                   profits: List[float], odds_values: Dict) -> List[str]:
        """Gera sugestões de prompt específicas"""
        suggestions = []
        
        if match_context and match_context.event_type == MatchEvent.FIRST_HALF_END:
            suggestions.append(self._generate_halftime_prompt(profile, match_context, profits, odds_values))
        
        if match_context and match_context.event_type in [MatchEvent.FAV_GOAL, MatchEvent.AZA_GOAL]:
            suggestions.append(self._generate_goal_prompt(profile, match_context, profits, odds_values))
        
        if match_context and match_context.event_type in [MatchEvent.AZA_DANGEROUS_ATTACK, MatchEvent.AZA_CORNER, MatchEvent.AZA_SHOT_ON_TARGET]:
            suggestions.append(self._generate_azarao_opportunity_prompt(profile, match_context, profits, odds_values))
        
        suggestions.append(self._generate_general_analysis_prompt(profile, match_context, profits, odds_values))
        
        return suggestions
    
    def _generate_azarao_opportunity_prompt(self, profile: RiskProfile, match_context: MatchContext, 
                                          profits: List[float], odds_values: Dict) -> str:
        """Gera prompt específico para oportunidades do azarão"""
        stats = match_context.statistics
        
        return f"""
## 🎯 OPORTUNIDADE MAIS 0,5 GOLS AZARÃO

### ⚡ EVENTO FAVORÁVEL DETECTADO
**Evento:** {match_context.event_type.value}
**Minuto:** {match_context.minute}' | **Placar:** {match_context.current_score}

### 📊 ESTATÍSTICAS DO AZARÃO
- Finalizações: {stats.shots_aza} ({stats.shots_on_target_aza} no alvo)
- Ataques Perigosos: {stats.dangerous_attacks_aza}
- Escanteios: {stats.corners_aza}
- **Probabilidade Estimada de Gol:** {self._calculate_azarao_goal_probability(stats, match_context.minute):.1f}%

Analise a oportunidade emergente para Mais 0,5 Gols Azarão considerando o contexto atual.
"""
    
    def _generate_halftime_prompt(self, profile: RiskProfile, match_context: MatchContext, 
                                profits: List[float], odds_values: Dict) -> str:
        """Gera prompt específico para análise do intervalo"""
        stats = match_context.statistics
        
        return f"""
## 🔄 ANÁLISE DO INTERVALO

### ⚽ RESUMO DO PRIMEIRO TEMPO
**Placar:** {match_context.current_score} | **Estatísticas Chave:**
- Posse: {stats.possession_fav}% vs {stats.possession_aza}%
- Finalizações: {stats.shots_fav}({stats.shots_on_target_fav}) vs {stats.shots_aza}({stats.shots_on_target_aza})

### 🛡️ ANÁLISE MAIS 0,5 GOLS AZARÃO - INTERVALO
**Performance do Azarão:**
- Finalizações: {stats.shots_aza} (No alvo: {stats.shots_on_target_aza})
- Ataques Perigosos: {stats.dangerous_attacks_aza}
- **Probabilidade 2º Tempo:** {min(70, self._calculate_azarao_goal_probability(stats, match_context.minute) + 15):.1f}%

Analise o primeiro tempo e forneça previsões para o segundo tempo com FOCO EM MAIS 0,5 GOLS AZARÃO.
"""
    
    def _generate_goal_prompt(self, profile: RiskProfile, match_context: MatchContext, 
                            profits: List[float], odds_values: Dict) -> str:
        """Gera prompt específico para análise pós-gol"""
        goal_team = "FAVORITO" if match_context.event_type == MatchEvent.FAV_GOAL else "AZARÃO"
        
        return f"""
## ⚽ ANÁLISE PÓS-GOL

### 🎉 GOL MARCADO
**Time:** {goal_team} | **Placar:** {match_context.current_score} | **Minuto:** {match_context.minute}'

Analise o impacto imediato do gol na estratégia Mais 0,5 Gols Azarão.
"""
    
    def _generate_general_analysis_prompt(self, profile: RiskProfile, match_context: MatchContext, 
                                        profits: List[float], odds_values: Dict) -> str:
        """Gera prompt geral para análise em tempo real"""
        return f"""
## 📊 ANÁLISE EM TEMPO REAL

### ⚽ CONTEXTO ATUAL
**Placar:** {match_context.current_score if match_context else '0x0'} | **Minuto:** {match_context.minute if match_context else '0'}'

Forneça uma análise completa do momento atual com FOCO EM MAIS 0,5 GOLS AZARÃO.
"""
    
    def _generate_conservative_actions(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                                     total_investment: float, match_context: MatchContext) -> List[str]:
        """Gera instruções para perfil conservador"""
        max_profit = max(zero_profit, fav_profit, aza_profit)
        actions = [
            f"🎯 OBJETIVO: Proteger {max_profit:.2f} de lucro máximo",
            f"💰 INVESTIR: Máximo 20% do bankroll (R$ {total_investment * 0.2:.2f})",
            f"🛡️ ESTRATÉGIA: 70% em proteção, 30% em oportunidades seguras",
            f"🎯 MAIS 0,5 AZARÃO: Alocar 40% do hedge nesta proteção",
            f"⏰ TIMING: Aplicar hedge imediatamente",
            f"📊 META: Garantir pelo menos 70% do lucro máximo ({max_profit * 0.7:.2f})"
        ]
        
        if match_context and match_context.minute > 40:
            actions.append("🔔 ATENÇÃO: Fim do primeiro tempo próximo - considerar esperar para melhor odds")
        
        return actions
    
    def _generate_moderate_actions(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                                 total_investment: float, match_context: MatchContext) -> List[str]:
        """Gera instruções para perfil moderado"""
        max_profit = max(zero_profit, fav_profit, aza_profit)
        actions = [
            f"🎯 OBJETIVO: Balancear proteção e oportunidade",
            f"💰 INVESTIR: Até 30% do bankroll (R$ {total_investment * 0.3:.2f})",
            f"⚖️ ESTRATÉGIA: 50% proteção, 50% oportunidades",
            f"🎯 MAIS 0,5 AZARÃO: Alocar 50% do hedge nesta proteção",
            f"⏰ TIMING: Aplicar hedge nos próximos 10-15 minutos",
            f"📊 META: Lucro líquido mínimo de {max_profit * 0.5:.2f}"
        ]
        
        return actions
    
    def _generate_aggressive_actions(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                                   total_investment: float, match_context: MatchContext) -> List[str]:
        """Gera instruções para perfil agressivo"""
        max_profit = max(zero_profit, fav_profit, aza_profit)
        actions = [
            f"🎯 OBJETIVO: Maximizar lucro aproveitando volatilidade",
            f"💰 INVESTIR: Até 40% do bankroll (R$ {total_investment * 0.4:.2f})",
            f"🎲 ESTRATÉGIA: 30% proteção, 70% oportunidades agressivas",
            f"🎯 MAIS 0,5 AZARÃO: Alocar 60% do hedge nesta proteção agressiva",
            f"⏰ TIMING: Aplicar hedge durante picos de odds",
            f"📊 META: Potencial de lucro > {max_profit * 1.2:.2f}"
        ]
        
        return actions

# =============================
# GERENCIADOR DINÂMICO ATUALIZADO
# =============================

class DynamicHedgeManager:
    def __init__(self):
        self.current_hedge_bets: List[HedgeBet] = []
        self.applied_strategy = None
        self.ia_analyzer = IAAnalyzer()
        self.memory_manager = OperationMemoryManager()
        # NOVOS COMPONENTES
        self.minute_analyzer = MinuteOddsAnalyzer()
        self.post_goal_analyzer = PostGoalAnalyzer()
        self.protection_system = DynamicProtectionSystem()
        self.prompt_generator = IAPromptGenerator()
        self.match_events = []
        
    def generate_automatic_protection_prompt(self, zero_profit: float, fav_profit: float, aza_profit: float,
                                           odds_values: Dict, minute: int, current_score: str,
                                           statistics: Dict, use_analise_conquistador: bool = False) -> str:
        """Gera prompt automático de proteção usando a nova função"""
        return gerar_prompt_automatico_protecao(
            zero_profit, fav_profit, aza_profit, odds_values, minute, current_score,
            statistics, use_analise_conquistador
        )
    
    def register_goal_event(self, goal_type: str, minute: int, current_profits: Dict):
        """Registra evento de gol e gera análise - VERSÃO COMPATÍVEL COM AMBOS OS SISTEMAS"""
        try:
            event_id = f"GOL_{goal_type}_{minute}_{datetime.now().strftime('%H%M%S')}"
            
            # Calcular novo placar
            current_score = st.session_state.get('current_score_dyn', '0x0')
            home_goals, away_goals = map(int, current_score.split('x'))
            
            if goal_type == "FAV":
                new_score = f"{home_goals + 1}x{away_goals}"
            else:  # AZA
                new_score = f"{home_goals}x{away_goals + 1}"
            
            # 🔥 USAR AMBOS OS SISTEMAS DE FORMA COMPATÍVEL
            
            # 1. PostGoalAnalyzer (para outras partes do sistema)
            post_goal_analysis = self.post_goal_analyzer.calculate_post_goal_returns(goal_type, minute, current_profits)
            post_goal_prompt = self.post_goal_analyzer.generate_post_goal_prompt(
                goal_type, minute, new_score, current_profits, {}
            )
            
            # 2. IAPromptGenerator (para interface - mais específico)
            ia_prompt = self.prompt_generator.generate_goal_analysis_prompt(
                goal_type, minute, new_score, current_profits, {}
            )
            
            # Registrar evento com ambos os prompts
            event = {
                "event_id": event_id,
                "type": "GOAL",
                "goal_type": goal_type,
                "minute": minute,
                "current_score": new_score,
                "timestamp": datetime.now(),
                "analysis": post_goal_analysis,
                "post_goal_prompt": post_goal_prompt,  # Para outras partes do sistema
                "ia_prompt": ia_prompt  # Para a interface
            }
            
            self.match_events.append(event)
            
            # 🔥 USAR O PROMPT DO IAPromptGenerator NA INTERFACE (mais específico)
            st.session_state.current_prompt = ia_prompt
            st.session_state.mostrar_prompt = True
            
            return event
            
        except Exception as e:
            st.error(f"❌ Erro ao registrar gol: {e}")
            return None

    def _trigger_interface_update(self, goal_type: str, minute: int, current_score: str):
        """Dispara atualização da interface sem modificar session_state diretamente"""
        # Marcar que precisa atualizar a interface
        st.session_state.need_interface_refresh = True
        st.session_state.pending_score_update = current_score
        st.session_state.pending_goal_type = goal_type
        st.session_state.pending_goal_minute = minute

    def _get_updated_score(self, goal_type: str) -> str:
        """Atualiza o placar baseado no tipo de gol - VERSÃO CORRIGIDA"""
        try:
            # Obter placar atual do session_state SEM usar o widget diretamente
            current_score = st.session_state.get('current_score_dyn', '0x0')
            
            # Se não existe no session_state, usar valor padrão
            if not current_score:
                current_score = "0x0"
                
            home_goals, away_goals = map(int, current_score.split('x'))
            
            # Atualizar placar
            if goal_type == "FAV":
                home_goals += 1
            else:  # AZA
                away_goals += 1
                
            new_score = f"{home_goals}x{away_goals}"
            
            # 🔥 CORREÇÃO: Usar approach diferente para atualizar
            # Em vez de modificar diretamente, usar callback ou recriar contexto
            return new_score
            
        except Exception as e:
            st.error(f"❌ Erro ao atualizar placar: {e}")
            return "0x0"

    def _update_match_context_after_goal(self, goal_type: str, minute: int, current_score: str):
        """Atualiza o contexto da partida após gol"""
        try:
            if hasattr(self, 'current_match_context'):
                self.current_match_context.current_score = current_score
                self.current_match_context.minute = minute
                self.current_match_context.event_type = MatchEvent.FAV_GOAL if goal_type == "FAV" else MatchEvent.AZA_GOAL
                self.current_match_context.momentum = "FAV" if goal_type == "FAV" else "AZA"
                self.current_match_context.additional_notes = f"Gol do {'FAVORITO' if goal_type == 'FAV' else 'AZARÃO'} aos {minute}' - Placar: {current_score}"
        except Exception as e:
            st.warning(f"⚠️ Não foi possível atualizar contexto: {e}")
    
    def get_minute_analysis(self, minute: int, current_score: str, odds_values: Dict):
        """Obtém análise baseada no minuto atual"""
        return self.minute_analyzer.get_favorable_odds_by_minute(minute, current_score, odds_values)
    
    def get_protection_recommendations(self, match_context: MatchContext, current_profits: Dict, odds_values: Dict):
        """Obtém recomendações de proteção dinâmica"""
        return self.protection_system.recommend_protection_strategy(match_context, current_profits, odds_values)
    
    def generate_protection_prompt(self, zero_profit: float, fav_profit: float, aza_profit: float,
                                 odds_values: Dict, minute: int, current_score: str, statistics: Dict) -> str:
        """Gera prompt para análise de proteção"""
        return self.prompt_generator.generate_standard_protection_prompt(
            zero_profit, fav_profit, aza_profit, odds_values, minute, current_score, statistics
        )
    
    def generate_goal_analysis_prompt(self, goal_type: str, minute: int, current_score: str,
                                    current_profits: Dict, odds_values: Dict) -> str:
        """Gera prompt para análise pós-gol - VERSÃO CORRIGIDA"""
        
        # 🔥 GARANTIR que o placar está atualizado
        if current_score == "0x0":
            # Se ainda está 0x0, atualizar baseado no gol
            if goal_type == "FAV":
                current_score = "1x0"
            else:
                current_score = "0x1"
        
        return self.prompt_generator.generate_goal_analysis_prompt(
            goal_type, minute, current_score, current_profits, odds_values
        )
    
    def apply_ia_strategy(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                         odds_values: Dict, total_investment: float = 100, 
                         match_context: MatchContext = None) -> Tuple[float, List[HedgeBet], IAAnalysis]:
        """Aplica estratégia da IA com sincronização completa"""
        
        # Iniciar nova operação
        profits = {"0x0": zero_profit, "1x1_FAV": fav_profit, "1x1_AZA": aza_profit}
        operation_id = self.memory_manager.start_new_operation(
            "Hedge Dinâmico IA", profits, total_investment, match_context
        )
        
        # Obter análise da IA
        ia_analysis = self.ia_analyzer.analyze_current_situation(
            zero_profit, fav_profit, aza_profit, total_investment, match_context, odds_values
        )
        self.memory_manager.save_ia_analysis(ia_analysis)
        
        # Salvar prompts
        for prompt in ia_analysis.prompt_suggestions:
            self.memory_manager.add_generated_prompt(prompt)
        self.memory_manager.add_generated_prompt(ia_analysis.comprehensive_prompt)
        
        # Aplicar estratégia baseada no perfil
        if ia_analysis.profile == RiskProfile.MODERATE:
            kept_profit, hedge_bets = self._apply_moderate_strategy(zero_profit, fav_profit, aza_profit, odds_values, total_investment, match_context)
        elif ia_analysis.profile == RiskProfile.CONSERVATIVE:
            kept_profit, hedge_bets = self._apply_conservative_strategy(zero_profit, fav_profit, aza_profit, odds_values, total_investment, match_context)
        else:
            kept_profit, hedge_bets = self._apply_aggressive_strategy(zero_profit, fav_profit, aza_profit, odds_values, total_investment, match_context)
        
        # Salvar operação
        self.memory_manager.save_hedge_bets(hedge_bets)
        self.memory_manager.add_learning_note(f"Estratégia {ia_analysis.profile.value} aplicada")
        self.memory_manager.add_learning_note("Proteção Mais 0,5 Gols Azarão implementada")
        
        self.current_hedge_bets = hedge_bets
        self.applied_strategy = f"IA_{ia_analysis.profile.value}"
        
        return kept_profit, hedge_bets, ia_analysis
    
    def _apply_moderate_strategy(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                               odds_values: Dict, total_investment: float, match_context: MatchContext) -> Tuple[float, List[HedgeBet]]:
        """Estratégia moderada"""
        bets = []
        max_hedge = total_investment * 0.3
        
        # Aposta principal: Mais 0,5 Gols Azarão
        main_bet = HedgeBet(
            "Proteção Mais 0,5 Gols Azarão",
            max_hedge * 0.5,
            odds_values.get("Mais 0,5 Gols Azarão", 2.1),
            "Proteção principal - cobre empates 1x1, vitórias 2x1, qualquer gol azarão",
            "Mais 0,5 Gols Azarão",
            0.5
        )
        bets.append(main_bet)
        
        # Proteção adicional
        protection_bet = HedgeBet(
            "Proteção Balanceada",
            max_hedge * 0.3,
            odds_values.get("Dupla Chance 1X", 1.8),
            "Proteção adicional do investimento",
            "Dupla Chance",
            0.3
        )
        bets.append(protection_bet)
        
        # Oportunidade
        opportunity_bet = HedgeBet(
            "Oportunidade Moderada",
            max_hedge * 0.2,
            odds_values.get("Ambas Marcam - Não", 2.0),
            "Aproveitamento de valor moderado",
            "Ambas Marcam",
            0.2
        )
        bets.append(opportunity_bet)
        
        kept_profit = max(zero_profit, fav_profit, aza_profit, 0) * 0.5
        return kept_profit, bets
    
    def _apply_conservative_strategy(self, zero_profit: float, fav_profit: float, aza_profit: float, 
                                   odds_values: Dict, total_investment: float, match_context: MatchContext) -> Tuple[float, List[HedgeBet]]:
        """Estratégia conservadora"""
        bets = []
        max_hedge = total_investment * 0.2
        
        # Aposta principal
        main_bet = HedgeBet(
            "Proteção Máxima Mais 0,5 Gols Azarão",
            max_hedge * 0.7,
            odds_values.get("Mais 0,5 Gols Azarão", 2.1),
            "Proteção conservadora principal",
            "Mais 0,5 Gols Azarão",
            0.7
        )
        bets.append(main_bet)
        
        # Backup
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
        """Estratégia agressiva"""
        bets = []
        max_hedge = total_investment * 0.4
        
        # Aposta agressiva
        aggressive_bet = HedgeBet(
            "Oportunidade Agressiva Mais 0,5 Gols Azarão",
            max_hedge * 0.6,
            odds_values.get("Mais 0,5 Gols Azarão", 2.1),
            "Busca por maximização agressiva",
            "Mais 0,5 Gols Azarão",
            0.6
        )
        bets.append(aggressive_bet)
        
        # Valor médio
        medium_bet = HedgeBet(
            "Valor Médio",
            max_hedge * 0.25,
            odds_values.get("Dupla Chance X2", 2.5),
            "Aproveitamento de valor médio",
            "Dupla Chance",
            0.25
        )
        bets.append(medium_bet)
        
        # Proteção mínima
        small_protection = HedgeBet(
            "Proteção Mínima",
            max_hedge * 0.15,
            odds_values.get("Não Sair Gols", 3.0),
            "Proteção básica",
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
        
        azarao_investment = sum(b.amount for b in self.current_hedge_bets if "Mais 0,5 Gols Azarão" in b.bet_type)
        azarao_percentage = (azarao_investment / total_invested * 100) if total_invested > 0 else 0
        
        return {
            "strategy": self.applied_strategy or "Nenhuma",
            "total_hedge_investment": total_invested,
            "expected_return": expected_return,
            "expected_profit": expected_return - total_invested,
            "azarao_protection_investment": azarao_investment,
            "azarao_protection_percentage": azarao_percentage,
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
        return self.memory_manager.current_operation_id
    
    def get_operation_summary(self, operation_id: str) -> Optional[Dict]:
        operation = self.memory_manager.get_operation_by_id(operation_id)
        if not operation:
            return None
        
        total_hedge_investment = sum(b.amount for b in operation.hedge_bets) if operation.hedge_bets else 0
        expected_return = sum(b.amount * b.odds for b in operation.hedge_bets) if operation.hedge_bets else 0
        
        azarao_investment = sum(b.amount for b in operation.hedge_bets if "Mais 0,5 Gols Azarão" in b.bet_type) if operation.hedge_bets else 0
        azarao_percentage = (azarao_investment / total_hedge_investment * 100) if total_hedge_investment > 0 else 0
        
        return {
            "operation_id": operation.operation_id,
            "timestamp": operation.timestamp,
            "scenario": operation.scenario,
            "status": operation.status.value,
            "total_investment": operation.total_investment,
            "total_hedge_investment": total_hedge_investment,
            "expected_profit": expected_return - total_hedge_investment,
            "azarao_protection_investment": azarao_investment,
            "azarao_protection_percentage": azarao_percentage,
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
# FUNÇÃO PARA COPIAR TEXTO - VERSÃO SIMPLIFICADA
# =============================

def copy_to_clipboard(text: str):
    """Copia texto para área de transferência - Versão Simplificada"""
    try:
        # Tenta usar pyperclip primeiro
        import pyperclip
        pyperclip.copy(text)
        st.toast("✅ Prompt copiado para a área de transferência!")
        st.success("📋 **Texto copiado com sucesso!**")
        return True
    except:
        # Fallback: mostra o texto com opção de copiar
        st.warning("🔧 **Instale o pyperclip para copiar automaticamente**")
        st.info("💡 **Comando no terminal:** `pip install pyperclip`")
        
        # Cria uma área de texto editável para facilitar a cópia
        st.text_area("📋 **Copie o prompt abaixo:**", value=text, height=300)
        
        # Botão para recarregar após instalação
        if st.button("🔄 Recarregar após instalação", key="reload_after_install"):
            st.rerun()
        
        return False
    
# =============================
# INTERFACE APRIMORADA
# =============================

def init_hedge_state():
    """Inicializa o estado do hedge manager"""
    if "hedge_manager" not in st.session_state:
        st.session_state.hedge_manager = DynamicHedgeManager()
    if "hedge_applied" not in st.session_state:
        st.session_state.hedge_applied = False
    if "current_operation_id" not in st.session_state:
        st.session_state.current_operation_id = None
    if "match_context" not in st.session_state:
        st.session_state.match_context = None
    if "goal_events" not in st.session_state:
        st.session_state.goal_events = []
    if "current_prompt" not in st.session_state:
        st.session_state.current_prompt = ""

def render_enhanced_hedge_controls(zero_profit: float, fav_profit: float, aza_profit: float, odds_values: Dict):
    """Interface aprimorada com análise de minutos e proteções dinâmicas"""
    
    st.info("""
    **🎯 INSTRUÇÕES APRIMORADAS:**
    1. Configure as odds principais na aba 'Configuração'
    2. Aplique as estratégias desejadas  
    3. Use esta aba para proteções dinâmicas durante a partida
    4. **NOVO:** Análise automática por minuto e proteções inteligentes
    """)
    
    # Métricas principais
    st.subheader("📊 Situação Atual")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lucro 0x0", f"R$ {zero_profit:.2f}")
    with col2:
        st.metric("Lucro 1x1 FAV", f"R$ {fav_profit:.2f}")
    with col3:
        st.metric("Lucro 1x1 AZA", f"R$ {aza_profit:.2f}")

    total_investment = abs(zero_profit) + abs(fav_profit) + abs(aza_profit)
    
    # ✅ VERSÃO CORRIGIDA - SEM DUPLICAÇÃO
    st.subheader("⏰ Configuração do Momento da Partida")

    col_placar = st.columns([2, 1])
    with col_placar[0]:
        minute = st.number_input("Minuto da Partida:", min_value=1, max_value=120, value=1, key="current_minute_dyn")
        current_score = st.selectbox("Placar Atual:", ["0x0", "1x0", "0x1", "1x1", "2x0", "0x2", "2x1", "1x2", "2x2"], key="current_score_dyn")

    with col_placar[1]:
        current_score_display = st.session_state.get('current_score_dyn', '0x0')
        st.info(f"🏆 **PLACAR ATUAL:** {current_score_display}")
        
        if st.button("🔄 Resetar Placar", key="reset_placar"):
            st.session_state.current_score_dyn = "0x0"
            st.rerun()

    # ✅ REMOVA ESTE BLOCO DUPLICADO COMPLETAMENTE:
    # col1, col2, col3 = st.columns(3)
    # with col1:
    #     minute = st.number_input("Minuto da Partida:", min_value=1, max_value=120, value=1, key="current_minute_dyn")
    #     current_score = st.selectbox("Placar Atual:", ["0x0", "1x0", "0x1", "1x1", "2x0", "0x2", "2x1", "1x2", "2x2"], key="current_score_dyn")

    # ✅ MANTENHA APENAS AS ESTATÍSTICAS (col2 e col3 originais)
    col2, col3 = st.columns(2)

    with col2:
        st.markdown("**📈 Estatísticas do Azarão**")
        shots_aza = st.number_input("Finalizações Azarão:", min_value=0, value=0, key="shots_aza_dyn")
        shots_on_target_aza = st.number_input("Finalizações no Alvo:", min_value=0, value=0, key="shots_target_aza_dyn")
        dangerous_attacks_aza = st.number_input("Ataques Perigosos:", min_value=0, value=0, key="attacks_aza_dyn")

    with col3:
        st.markdown("**🎯 Análise por Minuto**")
        if st.button("🔍 Analisar Odds por Minuto", use_container_width=True, key="analisar_minuto"):
            if "hedge_manager" in st.session_state:
                analysis = st.session_state.hedge_manager.get_minute_analysis(minute, current_score, odds_values)
                
                st.success(f"**Faixa {analysis['minute_range']}:** {analysis['range_description']}")
                st.info(f"**Foco:** {analysis['focus']}")
                
                if analysis['favorable_odds']:
                    for market, info in analysis['favorable_odds'].items():
                        st.write(f"{info['rating']} **{market}:** {info['odd']:.2f} - {info['reason']}")
                else:
                    st.warning("Nenhuma odd favorável identificada neste minuto")

    # Configuração de Odds para Hedge
    st.subheader("⚙️ Odds para Proteção")
    
    default_odds = {
        "Mais 0,5 Gols Azarão": 2.10,
        "Dupla Chance 1X": 1.80,
        "Dupla Chance X2": 1.91,
        "Ambas Marcam - Não": 2.00,
        "Não Sair Gols": 3.00,
        "Mais 2,5 Gols": 2.20,
        "Menos 2,5 Gols": 1.65
    }
    
    final_odds = odds_values.copy() if odds_values else {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🛡️ Proteções Principais**")
        for bet_type in ["Mais 0,5 Gols Azarão", "Dupla Chance 1X", "Dupla Chance X2"]:
            default_odd = default_odds.get(bet_type, 2.0)
            current_odd = final_odds.get(bet_type, default_odd)
            
            final_odds[bet_type] = st.number_input(
                f"{bet_type}", 
                value=float(current_odd), 
                min_value=1.1, 
                max_value=10.0, 
                step=0.1,
                key=f"hedge_odd_{bet_type}",
                help="Protege empates 1x1, vitórias 2x1, qualquer cenário com gol do azarão" if "Azarão" in bet_type else ""
            )
    
    with col2:
        st.markdown("**🎯 Proteções Adicionais**")
        for bet_type in ["Ambas Marcam - Não", "Não Sair Gols", "Mais 2,5 Gols", "Menos 2,5 Gols"]:
            default_odd = default_odds.get(bet_type, 2.0)
            current_odd = final_odds.get(bet_type, default_odd)
            
            final_odds[bet_type] = st.number_input(
                f"{bet_type}", 
                value=float(current_odd), 
                min_value=1.1, 
                max_value=10.0, 
                step=0.1,
                key=f"hedge_odd_{bet_type}"
            )

    # NOVO: Eventos em Tempo Real com Análise de Retorno
    st.subheader("⚽ Eventos da Partida com Análise de Retorno")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🥅 Gol do FAVORITO", use_container_width=True, type="secondary", key="gol_fav_corrigido"):
            tempo_gol = st.number_input("Minuto do gol:", min_value=1, max_value=120, value=25, key="tempo_gol_fav_corrigido")
            
            # Registrar evento e mostrar análise
            current_profits = {"0x0": zero_profit, "1x1_FAV": fav_profit, "1x1_AZA": aza_profit}
            event = st.session_state.hedge_manager.register_goal_event("FAV", tempo_gol, current_profits)
            
            if event:
                st.success(f"✅ Gol do FAVORITO registrado aos {tempo_gol} minutos")
                st.info(f"📊 **Placar Atualizado:** {event['current_score']}")
                
                # Gerar prompt para IA
                prompt = st.session_state.hedge_manager.generate_goal_analysis_prompt(
                    "FAV", tempo_gol, event['current_score'], current_profits, final_odds
                )
                st.session_state.current_prompt = prompt
                
                # Mostrar análise de retorno
                analysis = event['analysis']
                st.info(f"""
                **📊 Análise Pós-Gol:**
                - **Cenário:** {analysis['scenario']}
                - **Retorno Protegido:** R$ {analysis['returns_breakdown']['protected_profit']:.2f}
                - **Risco:** {analysis['risk_level']}
                - **Recomendação:** {analysis['recommendation']}
                """)
    
    with col2:
        if st.button("🥅 Gol do AZARÃO", use_container_width=True, type="secondary", key="gol_aza_corrigido"):
            tempo_gol = st.number_input("Minuto do gol:", min_value=1, max_value=120, value=25, key="tempo_gol_aza_corrigido")
            
            # Registrar evento e mostrar análise
            current_profits = {"0x0": zero_profit, "1x1_FAV": fav_profit, "1x1_AZA": aza_profit}
            event = st.session_state.hedge_manager.register_goal_event("AZA", tempo_gol, current_profits)
            
            if event:
                st.success(f"✅ Gol do AZARÃO registrado aos {tempo_gol} minutos")
                st.info(f"📊 **Placar Atualizado:** {event['current_score']}")
                
                # Gerar prompt para IA
                prompt = st.session_state.hedge_manager.generate_goal_analysis_prompt(
                    "AZA", tempo_gol, event['current_score'], current_profits, final_odds
                )
                st.session_state.current_prompt = prompt
                
                # Mostrar análise de retorno
                analysis = event['analysis']
                st.info(f"""
                **📊 Análise Pós-Gol:**
                - **Cenário:** {analysis['scenario']}
                - **Retorno Protegido:** R$ {analysis['returns_breakdown']['protected_profit']:.2f}
                - **Risco:** {analysis['risk_level']}
                - **Recomendação:** {analysis['recommendation']}
                """)

    # NOVO: Sistema de Proteções Dinâmicas - CORREÇÃO CRÍTICA
    st.subheader("🛡️ Sistema de Proteções Dinâmicas")
    
    # Criar contexto de partida para análise
    match_stats = MatchStatistics(
        possession_fav=55, possession_aza=45,
        shots_fav=8, shots_aza=shots_aza,
        shots_on_target_fav=3, shots_on_target_aza=shots_on_target_aza,
        dangerous_attacks_fav=12, dangerous_attacks_aza=dangerous_attacks_aza,
        corners_fav=5, corners_aza=3,
        fouls_fav=8, fouls_aza=10,
        offsides_fav=2, offsides_aza=1,
        yellow_cards_fav=1, yellow_cards_aza=2,
        red_cards_fav=0, red_cards_aza=0
    )
    
    match_context = MatchContext(
        current_score=current_score,
        minute=minute,
        statistics=match_stats,
        event_type=MatchEvent.MATCH_START,
        momentum="EQUILIBRADO",
        additional_notes=f"Análise em tempo real - Minuto {minute}"
    )
    
    current_profits = {"0x0": zero_profit, "1x1_FAV": fav_profit, "1x1_AZA": aza_profit}
    
    # 🔥 CORREÇÃO: BOTÃO DE RECOMENDAÇÕES SEMPRE GERA PROMPT
    if st.button("🎯 Obter Recomendações de Proteção", use_container_width=True, key="obter_recomendacoes_protecao"):
        
        # 🔥 SEMPRE GERAR PROMPT DE PROTEÇÃO (INDEPENDENTE DE GOL)
        statistics_dict = {
            'shots_aza': shots_aza,
            'shots_on_target_aza': shots_on_target_aza,
            'dangerous_attacks_aza': dangerous_attacks_aza,
            'corners_aza': 3
        }
        
        # Verificar se está usando análise do Conquistador
        use_analise_conquistador = st.session_state.get('usar_analise_conquistador', False)
        
        # Gerar prompt de proteção automático
        prompt = st.session_state.hedge_manager.generate_automatic_protection_prompt(
            zero_profit, fav_profit, aza_profit, final_odds, minute, current_score, 
            statistics_dict, use_analise_conquistador
        )
        
        # Armazenar prompt no session_state
        st.session_state.current_prompt = prompt
        
        # Obter recomendações (se disponíveis)
        try:
            recommendations = st.session_state.hedge_manager.get_protection_recommendations(
                match_context, current_profits, final_odds
            )
            
            if recommendations and recommendations['top_recommendation']:
                top_rec = recommendations['top_recommendation']
                st.success(f"**🎯 Estratégia Recomendada:** {top_rec['name']}")
                st.info(f"**📊 Confiança:** {top_rec['confidence']:.0%} | **Motivo:** {top_rec['reason']}")
                
                st.markdown("**💡 Mercados Recomendados:**")
                for market in top_rec['recommended_markets']:
                    if market in final_odds:
                        st.write(f"- {market}: Odd {final_odds[market]:.2f}")
            else:
                st.info("ℹ️ **Recomendação Padrão:** Proteção com Mais 0,5 Gols Azarão + Dupla Chance X2")
                st.write("- **🎯 Mais 0,5 Gols Azarão:** Proteção principal para cenários com gol do azarão")
                st.write("- **🛡️ Dupla Chance X2:** Proteção adicional para empates e vitórias do azarão")
                
        except Exception as e:
            st.info("ℹ️ **Recomendação Automática Ativada:**")
            st.write("- **🎯 Foco em Mais 0,5 Gols Azarão** para proteger cenários com gol do azarão")
            st.write("- **🛡️ Dupla Chance X2** como proteção secundária")
            st.write(f"- **⏰ Minuto {minute}':** Timing adequado para proteções dinâmicas")
        
        # 🔥 MENSAGEM DE SUCESSO DO PROMPT
        st.success("✅ **Prompt de proteção gerado automaticamente!**")
        st.info("📋 Role para baixo para visualizar e copiar o prompt completo para IA")
        
        # Forçar exibição do prompt
        st.session_state.mostrar_prompt = True
        
    # Aplicação da Estratégia
    st.subheader("🚀 Aplicar Proteção Dinâmica")
    
    if st.button("✅ APLICAR HEDGE COM PROTEÇÃO AZARÃO", type="primary", use_container_width=True):
        with st.spinner("Executando estratégia de proteção dinâmica..."):
            try:
                kept_profit, hedge_bets, ia_analysis = st.session_state.hedge_manager.apply_ia_strategy(
                    zero_profit, fav_profit, aza_profit, final_odds, total_investment, match_context
                )
                
                st.session_state.hedge_applied = True
                st.session_state.current_operation_id = st.session_state.hedge_manager.get_current_operation_id()
                
                st.success("🎉 **PROTEÇÃO APLICADA COM SUCESSO!**")
                
                azarao_investment = sum(b.amount for b in hedge_bets if "Mais 0,5 Gols Azarão" in b.bet_type)
                total_hedge = sum(b.amount for b in hedge_bets)
                azarao_percentage = (azarao_investment / total_hedge * 100) if total_hedge > 0 else 0
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Lucro Garantido", f"R$ {kept_profit:.2f}")
                with col2:
                    st.metric("Total Hedge", f"R$ {total_hedge:.2f}")
                with col3:
                    st.metric("Proteção Azarão", f"R$ {azarao_investment:.2f}")
                with col4:
                    st.metric("% Proteção", f"{azarao_percentage:.1f}%")
                
                # Mostrar análise da IA
                st.markdown("### 🧠 Análise da IA Aplicada")
                st.write(f"**Perfil:** {ia_analysis.profile.value}")
                st.write(f"**Confiança:** {ia_analysis.confidence:.0%}")
                st.write(f"**Estratégia:** {ia_analysis.recommended_strategy}")
                
                st.markdown("**📋 Plano de Ação:**")
                for action in ia_analysis.action_plan:
                    st.write(f"- {action}")
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao aplicar proteção: {e}")

    # 🔥 MELHORIA: EXIBIÇÃO AUTOMÁTICA DO PROMPT GERADO
    if st.session_state.get('current_prompt') and st.session_state.get('mostrar_prompt', False):
        st.markdown("---")
        st.subheader("🤖 Prompt Gerado para IA")
        
        with st.expander("📋 Visualizar Prompt Completo", expanded=True):
            st.markdown(st.session_state.current_prompt)
        
        # Botão para copiar prompt
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Copiar Prompt para IA", use_container_width=True, key="copiar_prompt_geral"):
                copy_to_clipboard(st.session_state.current_prompt)
        with col2:
            if st.button("💾 Salvar Prompt", use_container_width=True, key="salvar_prompt_geral"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"prompt_ia_{timestamp}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(st.session_state.current_prompt)
                st.success(f"Prompt salvo como {filename}")
        with col3:
            if st.button("🔄 Gerar Novo Prompt", use_container_width=True, key="gerar_novo_prompt"):
                # Limpar prompt atual para forçar nova geração
                st.session_state.current_prompt = None
                st.session_state.mostrar_prompt = False
                st.rerun()
                
# =============================
# 🆕 FUNÇÃO PARA GERAR PROMPT AUTOMÁTICO DE PROTEÇÃO
# =============================

# =============================
# 🆕 FUNÇÕES AUXILIARES PARA GERAÇÃO AUTOMÁTICA DE PROMPTS
# =============================

def gerar_prompt_automatico_protecao(zero_profit: float, fav_profit: float, aza_profit: float,
                                   odds_values: Dict, minute: int, current_score: str,
                                   statistics: Dict, use_analise_conquistador: bool = False) -> str:
    """Gera prompt automático de proteção baseado na situação atual"""
    
    # Calcular métricas de risco
    profits = [zero_profit, fav_profit, aza_profit]
    max_profit = max(profits)
    min_profit = min(profits)
    volatilidade = abs(max_profit - min_profit)
    
    # Determinar nível de risco
    if volatilidade < 5:
        nivel_risco = "BAIXO"
        estrategia_base = "Proteção Conservadora"
    elif volatilidade < 15:
        nivel_risco = "MODERADO" 
        estrategia_base = "Hedge Balanceado"
    else:
        nivel_risco = "ALTO"
        estrategia_base = "Proteção Agressiva"
    
    # Verificar se há análise do Sistema Conquistador disponível
    info_analise = {}
    if use_analise_conquistador and hasattr(st.session_state, 'ultima_analise_transmitida'):
        info_analise = st.session_state.ultima_analise_transmitida['informacoes_extraidas']
    
    prompt = f"""
## 🛡️ ANÁLISE DE PROTEÇÃO DINÂMICA - GERADO AUTOMATICAMENTE

### 📊 CONTEXTO DA PARTIDA
- **Minuto:** {minute}'
- **Placar:** {current_score}
- **Momento:** {'Primeiro Tempo' if minute <= 45 else 'Segundo Tempo'}
- **Nível de Risco Identificado:** {nivel_risco}

### 💰 SITUAÇÃO FINANCEIRA
- **Lucro 0x0:** R$ {zero_profit:.2f}
- **Lucro 1x1 FAV:** R$ {fav_profit:.2f} 
- **Lucro 1x1 AZA:** R$ {aza_profit:.2f}
- **Volatilidade:** R$ {volatilidade:.2f} ({nivel_risco})

### 📈 ESTATÍSTICAS DO AZARÃO
- **Finalizações:** {statistics.get('shots_aza', 0)}
- **Finalizações no Alvo:** {statistics.get('shots_on_target_aza', 0)}
- **Ataques Perigosos:** {statistics.get('dangerous_attacks_aza', 0)}
- **Probabilidade Estimada de Gol:** {calcular_probabilidade_azarao(statistics, minute):.1f}%

### 🎰 ODDS DISPONÍVEIS
"""
    
    # Adicionar odds com destaque para proteção azarão
    for market, odd in odds_values.items():
        if "Mais 0,5 Gols Azarão" in market:
            prompt += f"- **🎯 {market}:** {odd:.2f} ⭐ (PROTEÇÃO PRINCIPAL)\n"
        elif any(prot in market for prot in ["Dupla Chance", "Ambas Marcam - Não"]):
            prompt += f"- **🛡️ {market}:** {odd:.2f} (PROTEÇÃO SECUNDÁRIA)\n"
        else:
            prompt += f"- **{market}:** {odd:.2f}\n"
    
    # Adicionar informações da análise do Conquistador se disponível
    if info_analise:
        prompt += f"""
### 📋 ANÁLISE DO SISTEMA CONQUISTADOR
- **Cenário Principal:** {info_analise.get('cenario_principal', 'Não identificado')}
- **Confiança:** {info_analise.get('confianca_cenario', 'Moderada')}
- **Estilo do Favorito:** {info_analise.get('estilo_jogo_favorito', 'Equilibrado')}
- **Probabilidade Azarão Marcar:** {info_analise.get('probabilidade_azarao_marcar', 50.0)}%
"""
    
    prompt += f"""
### 🧠 SOLICITAÇÃO DE ANÁLISE DE PROTEÇÃO

Baseado no contexto acima (minuto {minute}', placar {current_score}, risco {nivel_risco}), forneça:

1. **ESTRATÉGIA DE PROTEÇÃO {estrategia_base.upper()}:**
   - Alocação ideal para Mais 0,5 Gols Azarão
   - Proteções complementares necessárias
   - Proporção de hedge vs. exposição

2. **ANÁLISE DE VALOR:**
   - Odds com melhor relação risco-retorno
   - Timing ideal para implementação
   - Tamanho de posição recomendado

3. **PLANO DE PROTEÇÃO POR CENÁRIO:**
   - Proteção para empates 1x1
   - Proteção para vitórias 2x1 do favorito  
   - Proteção para qualquer gol do azarão
   - Exposição residual aceitável

4. **GESTÃO TEMPORAL:**
   - Ajustes baseados no minuto {minute}'
   - Gatilhos para modificações
   - Condições de saída

**Forneça recomendações específicas e acionáveis para proteção proporcional aos valores distribuídos.**
"""
    
    return prompt

def calcular_probabilidade_azarao(statistics: Dict, minute: int) -> float:
    """Calcula probabilidade estimada do azarão marcar"""
    base_prob = 35.0
    
    # Ajustes baseados em estatísticas
    shots_aza = statistics.get('shots_aza', 0)
    shots_on_target_aza = statistics.get('shots_on_target_aza', 0)
    dangerous_attacks_aza = statistics.get('dangerous_attacks_aza', 0)
    
    if shots_on_target_aza > 0:
        base_prob += shots_on_target_aza * 8
    
    if dangerous_attacks_aza > 5:
        base_prob += (dangerous_attacks_aza - 5) * 2
    
    # Ajuste temporal
    if minute > 60:
        base_prob += 15
    elif minute > 30:
        base_prob += 8
    
    return min(85.0, base_prob)

def render_hedge_results():
    """Mostra resultados das operações de hedge aplicadas"""
    if not st.session_state.hedge_applied:
        return

    st.subheader("📊 Resultados da Proteção Aplicada")
    
    current_op_id = st.session_state.current_operation_id
    if not current_op_id:
        st.info("Nenhuma operação de proteção ativa")
        return
        
    operation_summary = st.session_state.hedge_manager.get_operation_summary(current_op_id)
    
    if not operation_summary:
        st.info("Operação não encontrada")
        return

    # Detalhes da operação
    st.markdown(f"**Operação:** {operation_summary['operation_id']}")
    st.markdown(f"**Início:** {operation_summary['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Resumo
    summary = st.session_state.hedge_manager.get_strategy_summary()
    
    if summary:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Estratégia", summary['strategy'])
        with col2:
            st.metric("Total Investido", f"R$ {summary['total_hedge_investment']:.2f}")
        with col3:
            st.metric("Lucro Esperado", f"R$ {summary['expected_profit']:.2f}")
        with col4:
            st.metric("Proteção Azarão", f"{summary['azarao_protection_percentage']:.1f}%")

    # Instruções da IA
    if operation_summary['ia_analysis']:
        st.markdown("### 📋 Plano de Ação da IA")
        for instruction in operation_summary['ia_analysis']['action_plan']:
            if "Mais 0,5 Gols Azarão" in instruction:
                st.write(f"🎯 **{instruction}**")
            else:
                st.write(f"📍 {instruction}")

    # Apostas aplicadas
    if operation_summary['hedge_bets']:
        st.markdown("### 💰 Apostas de Proteção Aplicadas")
        
        bets_data = []
        for bet in operation_summary['hedge_bets']:
            highlight = "🎯" if "Mais 0,5 Gols Azarão" in bet['type'] else ""
            bets_data.append({
                'Mercado': f"{highlight} {bet['market']}",
                'Tipo': bet['type'],
                'Valor': f"R$ {bet['amount']:.2f}",
                'Odd': bet['odds'],
                'Retorno': f"R$ {bet['amount'] * bet['odds']:.2f}",
                'Descrição': bet['description']
            })
        
        df = pd.DataFrame(bets_data)
        st.dataframe(df, use_container_width=True)

# =============================
# FUNÇÕES DE INTEGRAÇÃO
# =============================

def get_current_operation_info() -> Optional[Dict]:
    """Retorna informações da operação atual para integração"""
    if "hedge_manager" not in st.session_state:
        return None
    
    current_op_id = st.session_state.hedge_manager.get_current_operation_id()
    if not current_op_id:
        return None
    
    return st.session_state.hedge_manager.get_operation_summary(current_op_id)

def continue_operation_from_id(operation_id: str) -> bool:
    """Continua uma operação existente"""
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

def render_hedge_controls(zero_profit: float, fav_profit: float, aza_profit: float, odds_values: Dict):
    """Função principal para renderizar controles de hedge"""
    init_hedge_state()
    render_enhanced_hedge_controls(zero_profit, fav_profit, aza_profit, odds_values)
    
    if st.session_state.hedge_applied:
        render_hedge_results()

def main_hedge_module():
    """Função principal para teste do módulo"""
    st.set_page_config(page_title="Hedge Dinâmico", page_icon="🛡️", layout="wide")
    st.title("🛡️ HEDGE DINÂMICO - SISTEMA CONQUISTADOR")
    
    init_hedge_state()
    
    st.sidebar.header("📊 Dados de Entrada")
    zero_profit = st.sidebar.number_input("Lucro 0x0", value=2.27, step=0.1)
    fav_profit = st.sidebar.number_input("Lucro 1x1 FAV", value=-0.98, step=0.1)
    aza_profit = st.sidebar.number_input("Lucro 1x1 AZA", value=-0.98, step=0.1)
    
    render_hedge_controls(zero_profit, fav_profit, aza_profit, {})

if __name__ == "__main__":
    main_hedge_module()
