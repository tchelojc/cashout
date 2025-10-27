# ao_vivo.py (VERSÃO COMPLETA COM SISTEMA CONQUISTADOR INTEGRADO + MAIS 0,5 GOLS AZARÃO)
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
    # NOVA APOSTA IMPLEMENTADA
    OVER_05_AZARAO = "Mais 0,5 Gols Azarão"

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
# 🔄 SISTEMA DE DISTRIBUIÇÕES OTIMIZADAS
# =============================================

class DistribuicaoManager:
    """Gerenciador de distribuições integrado com o Sistema Conquistador"""
    
    def __init__(self):
        self.distribuicoes = self._criar_distribuicoes_conquistador()
        self.distribuicao_ativa = None
    
    def _criar_distribuicoes_conquistador(self) -> Dict[str, Dict]:
        """Cria distribuições alinhadas com o Sistema Conquistador"""
        return {
            "REFERENCIA_OTIMIZADA": self._criar_referencia_otimizada(),
            "ALTO_LUCRO_2W1L": self._criar_alto_lucro_2w1l(),
            "PROTEGIDA_CONSERVADORA": self._criar_protegida_conservadora(),
            "AGGRESSIVE_3W1L": self._criar_aggressive_3w1l()
        }
    
    def _criar_referencia_otimizada(self) -> Dict[str, Dict]:
        """Distribuição base completa do Sistema Conquistador"""
        return {
            "0x0": {"nome": "Empate sem gols", "tipo": "PREJUIZO", "retorno": -1.50, "roi": -12.5, "valor_sugerido": 1.00, "protecao": True},
            "1x0": {"nome": "Vitória do favorito 1x0", "tipo": "LUCRO", "retorno": 2.00, "roi": 16.7, "valor_sugerido": 3.00, "protecao": False},
            "2x0": {"nome": "Vitória convincente do favorito", "tipo": "LUCRO", "retorno": 6.00, "roi": 50.0, "valor_sugerido": 4.00, "protecao": False},
            "0x1": {"nome": "Vitória do azarão 0x1", "tipo": "PREJUIZO", "retorno": -0.50, "roi": -4.2, "valor_sugerido": 1.50, "protecao": True},
            "1x1": {"nome": "Empate 1x1", "tipo": "PREJUIZO", "retorno": -2.00, "roi": -16.7, "valor_sugerido": 1.00, "protecao": True},
            "2x1": {"nome": "Vitória do favorito com gol do azarão", "tipo": "LUCRO", "retorno": 2.50, "roi": 20.8, "valor_sugerido": 3.50, "protecao": True},
            "1x2": {"nome": "Vitória do azarão com gol do favorito", "tipo": "LUCRO", "retorno": 3.00, "roi": 25.0, "valor_sugerido": 3.50, "protecao": True},
            "2x2": {"nome": "Empate com muitos gols", "tipo": "PREJUIZO", "retorno": -2.00, "roi": -16.7, "valor_sugerido": 1.00, "protecao": True},
            "3x0": {"nome": "Goleada do favorito", "tipo": "LUCRO", "retorno": 6.00, "roi": 50.0, "valor_sugerido": 4.00, "protecao": False},
            "0x2": {"nome": "Vitória convincente do azarão", "tipo": "LUCRO", "retorno": 4.50, "roi": 37.5, "valor_sugerido": 3.50, "protecao": True},
        }

    def _criar_alto_lucro_2w1l(self) -> Dict[str, Dict]:
        """Distribuição Alto Lucro 2W1L - Foco em retornos altos"""
        return {
            "2x0": {"nome": "Vitória convincente do favorito", "tipo": "LUCRO", "retorno": 8.50, "roi": 70.8, "valor_sugerido": 4.50, "protecao": False},
            "3x0": {"nome": "Goleada do favorito", "tipo": "LUCRO", "retorno": 8.50, "roi": 70.8, "valor_sugerido": 4.50, "protecao": False},
            "0x2": {"nome": "Vitória do azarão", "tipo": "LUCRO", "retorno": 6.20, "roi": 51.7, "valor_sugerido": 4.00, "protecao": True},
            "1x0": {"nome": "Vitória simples do favorito", "tipo": "LUCRO", "retorno": 3.20, "roi": 26.7, "valor_sugerido": 3.00, "protecao": False},
            "2x1": {"nome": "Vitória favorito com gol contra", "tipo": "LUCRO", "retorno": 4.50, "roi": 37.5, "valor_sugerido": 4.00, "protecao": True},
            "0x0": {"nome": "Empate sem gols", "tipo": "PREJUIZO", "retorno": -4.50, "roi": -37.5, "valor_sugerido": 1.00, "protecao": True},
            "1x1": {"nome": "Empate 1x1", "tipo": "PREJUIZO", "retorno": -6.00, "roi": -50.0, "valor_sugerido": 1.00, "protecao": True},
        }

    def _criar_protegida_conservadora(self) -> Dict[str, Dict]:
        """Distribuição Protegida Conservadora - Minimizar riscos"""
        return {
            "1x0": {"nome": "Vitória simples do favorito", "tipo": "LUCRO", "retorno": 2.50, "roi": 20.8, "valor_sugerido": 4.00, "protecao": False},
            "2x0": {"nome": "Vitória do favorito", "tipo": "LUCRO", "retorno": 4.00, "roi": 33.3, "valor_sugerido": 4.00, "protecao": False},
            "2x1": {"nome": "Vitória favorito com gol contra", "tipo": "LUCRO", "retorno": 3.00, "roi": 25.0, "valor_sugerido": 4.00, "protecao": True},
            "0x1": {"nome": "Vitória do azarão", "tipo": "LUCRO", "retorno": 3.00, "roi": 25.0, "valor_sugerido": 3.00, "protecao": True},
            "0x0": {"nome": "Empate sem gols", "tipo": "PREJUIZO", "retorno": -2.50, "roi": -20.8, "valor_sugerido": 2.00, "protecao": True},
            "1x1": {"nome": "Empate 1x1", "tipo": "PREJUIZO", "retorno": -3.00, "roi": -25.0, "valor_sugerido": 2.00, "protecao": True},
        }

    def _criar_aggressive_3w1l(self) -> Dict[str, Dict]:
        """Distribuição Aggressive 3W1L - Máximo potencial"""
        return {
            "2x0": {"nome": "Vitória do favorito", "tipo": "LUCRO", "retorno": 10.00, "roi": 83.3, "valor_sugerido": 4.00, "protecao": False},
            "3x0": {"nome": "Goleada do favorito", "tipo": "LUCRO", "retorno": 10.00, "roi": 83.3, "valor_sugerido": 4.00, "protecao": False},
            "0x2": {"nome": "Vitória do azarão", "tipo": "LUCRO", "retorno": 8.00, "roi": 66.7, "valor_sugerido": 4.00, "protecao": True},
            "1x0": {"nome": "Vitória simples favorito", "tipo": "LUCRO", "retorno": 5.00, "roi": 41.7, "valor_sugerido": 4.00, "protecao": False},
            "0x0": {"nome": "Empate sem gols", "tipo": "PREJUIZO", "retorno": -8.00, "roi": -66.7, "valor_sugerido": 2.00, "protecao": True},
            "1x1": {"nome": "Empate 1x1", "tipo": "PREJUIZO", "retorno": -10.00, "roi": -83.3, "valor_sugerido": 2.00, "protecao": True},
        }
    
    def aplicar_distribuicao(self, nome_distribuicao: str, capital_total: float = 20.0) -> Dict[str, Dict]:
        """Aplica distribuição perfeitamente"""
        if nome_distribuicao not in self.distribuicoes:
            raise ValueError(f"Distribuição {nome_distribuicao} não encontrada")
        
        distribuicao_base = self.distribuicoes[nome_distribuicao]
        distribuicao_ajustada = {}
        
        # Calcular fator de ajuste
        total_sugerido = sum(dist['valor_sugerido'] for dist in distribuicao_base.values())
        fator_ajuste = capital_total / total_sugerido
        
        for cenario, dados in distribuicao_base.items():
            valor_ajustado = dados['valor_sugerido'] * fator_ajuste
            retorno_ajustado = dados['retorno'] * fator_ajuste
            
            distribuicao_ajustada[cenario] = {
                **dados,
                'valor_ajustado': round(valor_ajustado, 2),
                'retorno_ajustado': round(retorno_ajustado, 2),
                'odd_calculada': round((retorno_ajustado + valor_ajustado) / valor_ajustado, 2) if valor_ajustado > 0 else 1.0
            }
        
        self.distribuicao_ativa = nome_distribuicao
        return distribuicao_ajustada

# =============================================
# 🎯 SISTEMA DE APLICAÇÕES COMBINADAS
# =============================================

class SistemaAplicacoes:
    def __init__(self):
        self.aplicacoes_predefinidas = self._criar_aplicacoes()
    
    def _criar_aplicacoes(self):
        return [
            {
                "nome": "MAIS 1,5 GOLS + AMBAS NÃO",
                "mercados": ["Mais 1.5 Gols", "Ambas Marcam - Não"],
                "descricao": "✅ Cobre vitórias 2x0, 3x0, 4x0, 5x0 (qualquer vitória convincente sem gol do azarão)",
                "peso_padrao": 0.30
            },
            {
                "nome": "MAIS 2,5 GOLS + FAVORITO", 
                "mercados": ["Mais 2.5 Gols", "Vitória Favorito"],
                "descricao": "✅ Cobre vitórias 3x0, 3x1, 4x0, 4x1, 5x0 (vitórias com muitos gols do favorito)",
                "peso_padrao": 0.35
            },
            {
                "nome": "PROTEÇÃO AZARÃO COMPLETA",
                "mercados": ["Mais 0,5 Gols Azarão", "Dupla Chance X2"],
                "descricao": "✅ Cobre empates 1x1, 2x2 e vitórias do azarão 1x0, 2x0, 2x1 (qualquer cenário com azarão marcando ou não perdendo)",
                "peso_padrao": 0.35
            }
        ]
    
    def calcular_valores_sugeridos(self, distribuicao_detalhes: Dict, distribuicao_nome: str) -> Dict[str, float]:
        """Calcula valores sugeridos baseados na distribuição"""
        if not distribuicao_detalhes:
            return {app["nome"]: 0.0 for app in self.aplicacoes_predefinidas}
        
        capital_total = sum(dados['valor_ajustado'] for dados in distribuicao_detalhes.values())
        
        # DEFINIR PESOS POR ESTRATÉGIA
        pesos = {
            "REFERENCIA_OTIMIZADA": [0.30, 0.35, 0.35],
            "ALTO_LUCRO_2W1L": [0.35, 0.40, 0.25],
            "PROTEGIDA_CONSERVADORA": [0.25, 0.30, 0.45],
            "AGGRESSIVE_3W1L": [0.40, 0.45, 0.15]
        }
        
        pesos_estrategia = pesos.get(distribuicao_nome, [0.30, 0.35, 0.35])
        
        valores_sugeridos = {}
        for i, aplicacao in enumerate(self.aplicacoes_predefinidas):
            valor = capital_total * pesos_estrategia[i]
            valores_sugeridos[aplicacao["nome"]] = round(valor, 2)
        
        return valores_sugeridos

# =============================================
# 🔧 FUNÇÃO INIT_STATE CORRIGIDA COM SISTEMA CONQUISTADOR
# =============================================

def init_state():
    """Inicializa o estado da aplicação com Sistema Conquistador integrado"""
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
            "Vitória Favorito": 1.80,
            "Mais 0,5 Gols Azarão": 2.10
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
            "Vitória Favorito": 1.00,
            "Mais 0,5 Gols Azarão": 1.50
        }
        
        initial_bankroll = sum(default_investments.values())
        
        # ✅ ADICIONAR NOVOS ESTADOS DO SISTEMA CONQUISTADOR
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
            'gols_sofridos_azarao': 10,
            # ✅ NOVOS ESTADOS DO SISTEMA CONQUISTADOR
            'distribuicao_manager': DistribuicaoManager(),
            'sistema_aplicacoes': SistemaAplicacoes(),
            'distribuicao_ativa': None,
            'distribuicao_detalhes': None,
            'etapa_atual': 1,
            'time_casa': "Favorito",
            'time_fora': "Azarao", 
            'odd_casa': 1.80,
            'odd_fora': 4.50,
            'favorito': "Favorito",
            'azarao': "Azarao"
        }
        update_proportions_from_investments()
    
    # 🔥 INICIALIZAÇÃO ROBUSTA DO MÓDULO DINÂMICO
    try:
        # Verificar se o módulo existe
        import importlib.util
        spec = importlib.util.find_spec("dinamico")
        
        if spec is not None:
            from dinamico import init_hedge_state
            if 'hedge_manager' not in st.session_state:
                init_hedge_state()
                st.success("✅ Módulo Dinâmico conectado com sucesso!")
        else:
            st.session_state.dinamico_available = False
            st.warning("⚠️ Módulo dinamico.py não encontrado. Funcionalidades de hedge estarão limitadas.")
            
    except ImportError as e:
        st.session_state.dinamico_available = False
        st.warning(f"⚠️ Módulo dinamico não disponível: {e}")

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

## 🛡️ PROTEÇÃO MAIS 0,5 GOLS AZARÃO
**ESTRATÉGIA IMPLEMENTADA:** A aposta 'Mais 0,5 Gols Azarão' protege especificamente:
- ✅ Empates 1x1 onde o azarão marca
- ✅ Vitórias 2x1 do favorito com gol de honra do azarão  
- ✅ Resultados como 1x2, 0x1, 0x2 onde azarão marca
- ✅ Cenários de virada onde azarão surpreende

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

### 1. 📊 ANÁLISE DE VALOR COM PROTEÇÃO AZARÃO
- Quais mercados apresentam melhor relação risco-retorno?
- Como a proteção 'Mais 0,5 Gols Azarão' impacta o hedge natural?
- Pontos de sobrevalorização/subvalorização

### 2. ⚖️ OTIMIZAÇÃO COM PROTEÇÃO DE EMPATES
- Distribuição ideal considerando a proteção do azarão
- Ajustes recomendados nos investimentos
- Estratégia de hedge natural aprimorada

### 3. 🛡️ GESTÃO DE RISCO COM PROTEÇÃO
- Principais riscos identificados e como a proteção ajuda
- Cenários críticos e proteções
- Limites de exposição recomendados

### 4. 📈 ESTRATÉGIA RECOMENDADA COM MAIS 0,5 AZARÃO
- Abordagem ideal para esta partida com proteção
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
        
        # NOVA PROBABILIDADE PARA MAIS 0,5 GOLS AZARÃO
        prob_azarao_marca = min(70, max(20, (gols_aza_f/5) * 15 + (gols_fav_s/5) * 10))
        
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
            "prob_proximo_gol_favorito": prob_vitoria_favorito * 0.6 + prob_empate * 0.3,
            # NOVA PROBABILIDADE
            "prob_mais_05_gols_azarao": prob_azarao_marca
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
            "Próximo Gol Favorito": "prob_proximo_gol_favorito",
            # NOVA APOSTA MAPEADA
            "Mais 0,5 Gols Azarão": "prob_mais_05_gols_azarao"
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
# 🎯 ANÁLISE DE CENÁRIOS ATUALIZADA
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
            # NOVA CONDIÇÃO PARA MAIS 0,5 GOLS AZARÃO
            elif bet_type == BetType.OVER_05_AZARAO:
                wins = away_goals > 0.5  # Azarão marca pelo menos 1 gol
            
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
# 🔧 FUNÇÕES DE SINCRONIZAÇÃO CORRIGIDAS
# =============================================

def sync_global_state():
    """SINCRONIZAÇÃO GLOBAL - ORDEM MESTRA PARA TODOS OS COMPONENTES"""
    sync_bankroll_values()
    
    st.session_state.app_state['last_analysis'] = {
        'total_invested': st.session_state.app_state['total_invested'],
        'total_bankroll': st.session_state.app_state['total_bankroll'],
        'timestamp': datetime.now().isoformat(),
        'sync_type': 'GLOBAL_COMMAND'
    }
    
    st.session_state.app_state['distribution_applied'] = True
    st.session_state.app_state['global_sync_time'] = datetime.now().isoformat()

def sync_bankroll_values():
    """Sincroniza todos os valores de bankroll e investimento - VERSÃO CORRIGIDA"""
    app_state = st.session_state.app_state
    
    # 🔥 CALCULAR TOTAL INVESTIDO DIRETO DOS VALORES
    total_invested = sum(app_state['investment_values'].values())
    
    # 🔥 ATUALIZAR O TOTAL INVESTIDO NO ESTADO
    app_state['total_invested'] = total_invested
    
    # 🔥 SE O BANKROLL FOR MENOR QUE O INVESTIDO, ATUALIZAR BANKROLL
    if app_state['total_bankroll'] < total_invested:
        app_state['total_bankroll'] = total_invested
    
    # 🔥 SE O BANKROLL FOR MUITO MAIOR QUE O INVESTIDO, MANTER O VALOR DO BANKROLL
    # (permite que o usuário tenha bankroll maior que o investido atual)
    
    # 🔥 ATUALIZAR PROPORÇÕES
    update_proportions_from_investments()
    
    # 🔥 LOG PARA VERIFICAR (opcional)
    app_state['last_sync'] = {
        'total_invested': total_invested,
        'total_bankroll': app_state['total_bankroll'],
        'timestamp': datetime.now().isoformat()
    }

# =============================================
# 🔧 FUNÇÃO PARA APLICAR VALORES AUTOMATICAMENTE
# =============================================

def aplicar_valores_distribuicao_automaticamente(distribuicao_detalhes, distribuicao_nome):
    """Aplica valores da distribuição automaticamente"""
    if not distribuicao_detalhes:
        return
    
    sistema_aplicacoes = st.session_state.app_state['sistema_aplicacoes']
    valores_sugeridos = sistema_aplicacoes.calcular_valores_sugeridos(distribuicao_detalhes, distribuicao_nome)
    
    # Limpar valores existentes
    for mercado in st.session_state.app_state['investment_values']:
        st.session_state.app_state['investment_values'][mercado] = 0.0
    
    # Aplicar valores baseados nas estratégias
    try:
        # DEFINIR PESOS POR ESTRATÉGIA
        pesos = {
            "REFERENCIA_OTIMIZADA": [0.30, 0.35, 0.35],
            "ALTO_LUCRO_2W1L": [0.35, 0.40, 0.25],
            "PROTEGIDA_CONSERVADORA": [0.25, 0.30, 0.45],
            "AGGRESSIVE_3W1L": [0.40, 0.45, 0.15]
        }
        
        pesos_estrategia = pesos.get(distribuicao_nome, [0.30, 0.35, 0.35])
        capital_total = sum(dados['valor_ajustado'] for dados in distribuicao_detalhes.values())
        
        # Aplicação 1: MAIS 1,5 + AMBAS NÃO
        valor_app1 = capital_total * pesos_estrategia[0]
        st.session_state.app_state['investment_values']["Mais 1.5 & Ambas Não"] = round(valor_app1 * 0.7, 2)
        st.session_state.app_state['investment_values']["Mais 1.5 Gols"] = round(valor_app1 * 0.3, 2)
        
        # Aplicação 2: MAIS 2,5 + FAVORITO
        valor_app2 = capital_total * pesos_estrategia[1]
        st.session_state.app_state['investment_values']["Mais 2.5 & Dupla Chance 12"] = round(valor_app2 * 0.6, 2)
        st.session_state.app_state['investment_values']["Vitória Favorito"] = round(valor_app2 * 0.4, 2)
        
        # Aplicação 3: PROTEÇÃO AZARÃO
        valor_app3 = capital_total * pesos_estrategia[2]
        st.session_state.app_state['investment_values']["Mais 0,5 Gols Azarão"] = round(valor_app3 * 0.6, 2)
        st.session_state.app_state['investment_values']["Dupla Chance X2"] = round(valor_app3 * 0.4, 2)
        
        # Ajustar bankroll
        total_investido = sum(st.session_state.app_state['investment_values'].values())
        st.session_state.app_state['total_bankroll'] = total_investido
        
        st.success("✅ Valores da distribuição aplicados automaticamente!")
        
    except Exception as e:
        st.error(f"❌ Erro ao aplicar valores: {str(e)}")

# =============================================
# 🎯 NOVA ABA DE DISTRIBUIÇÕES
# =============================================

def render_aba_distribuicoes():
    """Nova aba para sistema de distribuições"""
    st.header("🎯 Sistema de Distribuições - Estratégias Conquistador")
    
    distribuicao_manager = st.session_state.app_state['distribuicao_manager']
    
    st.info("""
    **📊 SISTEMA DE MÚLTIPLAS DISTRIBUIÇÕES**
    Selecione a estratégia que melhor se adapta ao seu perfil:
    - 🎯 **Referência Otimizada**: Balanceada (10 cenários)
    - 🚀 **Alto Lucro 2W1L**: Foco em retornos altos (7 cenários)  
    - 🛡️ **Protegida Conservadora**: Menor risco (6 cenários)
    - ⚡ **Aggressive 3W1L**: Máximo potencial (6 cenários)
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        distribuicao_selecionada = st.selectbox(
            "📊 Selecione a Distribuição:",
            options=list(distribuicao_manager.distribuicoes.keys()),
            format_func=lambda x: x.replace("_", " ").title(),
            index=0
        )
    
    with col2:
        capital_total = st.number_input(
            "💰 Capital Total (R$)", 
            min_value=10.0, 
            value=20.0, 
            step=1.0
        )
    
    if st.button("🎯 APLICAR DISTRIBUIÇÃO", use_container_width=True, type="primary"):
        with st.spinner("Aplicando distribuição..."):
            try:
                distribuicao = distribuicao_manager.aplicar_distribuicao(distribuicao_selecionada, capital_total)
                
                st.session_state.app_state['distribuicao_ativa'] = distribuicao_selecionada
                st.session_state.app_state['distribuicao_detalhes'] = distribuicao
                
                st.success(f"✅ **{distribuicao_selecionada.replace('_', ' ').title()}** aplicada com sucesso!")
                
                # Mostrar estatísticas
                lucros = [d for d in distribuicao.values() if d['tipo'] == 'LUCRO']
                prejuizos = [d for d in distribuicao.values() if d['tipo'] == 'PREJUIZO']
                
                st.success(f"📊 **{len(lucros)}** cenários de lucro | **{len(prejuizos)}** cenários de prejuízo")
                
                # Aplicar valores automaticamente
                aplicar_valores_distribuicao_automaticamente(distribuicao, distribuicao_selecionada)
                
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    # MOSTRAR DISTRIBUIÇÃO ATIVA
    if st.session_state.app_state['distribuicao_ativa']:
        distribuicao = st.session_state.app_state['distribuicao_detalhes']
        
        st.subheader("📋 Detalhes da Distribuição Aplicada")
        dados_tabela = []
        for cenario, dados in distribuicao.items():
            dados_tabela.append({
                "Cenário": cenario,
                "Descrição": dados['nome'],
                "Tipo": "✅ LUCRO" if dados['tipo'] == 'LUCRO' else "⚠️ PREJUÍZO",
                "Valor Investido (R$)": f"{dados['valor_ajustado']:.2f}",
                "Retorno Esperado (R$)": f"{dados['retorno_ajustado']:.2f}",
                "ROI": f"{dados['roi']}%",
                "Proteção": "✅" if dados['protecao'] else "❌"
            })
        
        df = pd.DataFrame(dados_tabela)
        st.dataframe(df, use_container_width=True)
        
# =============================================
# 🔧 FUNÇÃO AUXILIAR PARA VERIFICAR CONEXÃO
# =============================================

def check_dinamico_connection():
    """Verifica e relata o status da conexão com o módulo dinâmico"""
    try:
        from dinamico import DynamicHedgeManager
        return {
            "status": "✅ CONECTADO",
            "message": "Módulo dinâmico totalmente funcional",
            "features": [
                "Análise de minutos e odds",
                "Proteções dinâmicas", 
                "Sistema pós-gol",
                "Geração de prompts IA",
                "Memória de operações"
            ]
        }
    except ImportError:
        return {
            "status": "❌ DESCONECTADO", 
            "message": "Módulo dinamico.py não encontrado",
            "features": ["Funcionalidades básicas apenas"]
        }
    except Exception as e:
        return {
            "status": "⚠️ COM ERROS",
            "message": f"Módulo presente mas com problemas: {e}",
            "features": ["Funcionalidades limitadas"]
        }

# =============================================
# 🔧 RENDER_CONTROLS ATUALIZADO COM SISTEMA CONQUISTADOR + STATUS DINÂMICO
# =============================================

def render_controls():
    """Configuração inteligente - VERSÃO ATUALIZADA COM SISTEMA CONQUISTADOR E STATUS DINÂMICO"""
    
    # 🔥 STATUS DA CONEXÃO DINÂMICA (NOVO)
    connection_status = check_dinamico_connection()
    
    # 🔥 INDICADOR DE STATUS GLOBAL (EXISTENTE)
    if st.session_state.app_state.get('distribution_applied'):
        st.success("✅ **SISTEMA SINCRONIZADO** - Todas as abas mostram valores consistentes")
    else:
        st.warning("⚠️ **CLIQUE EM 'DISTRIBUIÇÃO AUTOMÁTICA' PARA SINCRONIZAR**")
    
    # 🔥 EXIBIR STATUS DA CONEXÃO DINÂMICA (NOVO)
    st.info(f"**Status do Módulo Dinâmico:** {connection_status['status']} - {connection_status['message']}")
    
    if connection_status['status'] != "✅ CONECTADO":
        st.warning("""
        **📋 Para funcionalidades COMPLETAS de hedge dinâmico:**
        1. Certifique-se de que `dinamico.py` está na mesma pasta
        2. Reinicie a aplicação  
        3. Todas as funcionalidades serão carregadas automaticamente
        """)
        
    sync_bankroll_values()  # CORREÇÃO GARANTIDA
    
    st.subheader("⚙️ Configuração Inteligente de Apostas - Sistema Conquistador")
    
    # 🔥 ABA ATUALIZADA COM SISTEMA CONQUISTADOR
    tab1, tab2, tab3 = st.tabs(["🎯 Distribuições", "💰 Investimentos", "💡 Recomendações"])
    
    with tab1:
        render_aba_distribuicoes()
    
    with tab2:
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
            
            # 🔥 EXIBIR TOTAIS ATUAIS DE FORMA MAIS CLARA
            current_total_invested = sum(st.session_state.app_state['investment_values'].values())
            current_bankroll = st.session_state.app_state['total_bankroll']
            
            new_bankroll = st.number_input(
                "Ajustar Bankroll (R$)",
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

            # 🔥 BOTÃO DE SINCRONIZAÇÃO FORÇADA
            if st.button("🔄 Sincronizar Valores", 
                        use_container_width=True, 
                        type="primary",
                        key="dist_auto_simple"):
                
                # 🎯 EXECUTAR SINCRONIZAÇÃO COMPLETA
                sync_global_state()
                
                # 🔥 ATUALIZAR OS VALORES EXIBIDOS
                total_atual = sum(st.session_state.app_state['investment_values'].values())
                bankroll_atual = st.session_state.app_state['total_bankroll']
                
                st.success(f"✅ Sistema sincronizado! Investido: R$ {total_atual:.2f} | Bankroll: R$ {bankroll_atual:.2f}")
                st.rerun()

    with tab3:
        # MANTER APENAS AS RECOMENDAÇÕES INTELIGENTES
        render_intelligent_recommendations()

# =============================================
# 🔧 FUNÇÕES DE RENDERIZAÇÃO PRINCIPAIS ATUALIZADAS
# =============================================

def aplicar_distribuicao_rapida(nome_distribuicao: str, capital_total: float):
    """Aplica distribuição rapidamente"""
    distribuicao_manager = st.session_state.app_state['distribuicao_manager']
    
    try:
        distribuicao = distribuicao_manager.aplicar_distribuicao(nome_distribuicao, capital_total)
        st.session_state.app_state['distribuicao_ativa'] = nome_distribuicao
        st.session_state.app_state['distribuicao_detalhes'] = distribuicao
        
        aplicar_valores_distribuicao_automaticamente(distribuicao, nome_distribuicao)
        
        st.success(f"✅ {nome_distribuicao.replace('_', ' ').title()} aplicada!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")

def render_analise_avancada_value_bets():
    """Renderiza a análise avançada de value bets ATUALIZADA"""
    st.header("🔥 Análise de Valor Avançada - Sistema Conquistador")
    
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
    
    # 🔥 NOVO: APLICAÇÕES DE DISTRIBUIÇÃO RÁPIDA
    st.subheader("⚡ Aplicação Rápida de Estratégias Conquistador")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🛡️ Conservador", use_container_width=True, key="conservador_rapido"):
            aplicar_distribuicao_rapida("PROTEGIDA_CONSERVADORA", bankroll)
    
    with col2:
        if st.button("⚖️ Balanceado", use_container_width=True, key="balanceado_rapido"):
            aplicar_distribuicao_rapida("REFERENCIA_OTIMIZADA", bankroll)
    
    with col3:
        if st.button("🚀 Agressivo", use_container_width=True, key="agressivo_rapido"):
            aplicar_distribuicao_rapida("AGGRESSIVE_3W1L", bankroll)
    
    with col4:
        if st.button("💎 Alto Lucro", use_container_width=True, key="alto_lucro_rapido"):
            aplicar_distribuicao_rapida("ALTO_LUCRO_2W1L", bankroll)
    
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
    
# =============================================
# 🔄 SISTEMA DE TRANSMISSÃO DE DADOS PARA HEDGE DINÂMICO
# =============================================

def transmitir_analise_para_hedge(relatorio_completo: str, estatisticas: Dict, odds: Dict, investments: Dict):
    """Transmite a análise completa para o módulo de hedge dinâmico"""
    try:
        # Verificar se o módulo dinâmico está disponível
        if 'hedge_manager' not in st.session_state:
            st.error("❌ Módulo de hedge dinâmico não está inicializado")
            return False
        
        # Extrair informações críticas do relatório
        informacoes_extraidas = extrair_informacoes_do_relatorio(relatorio_completo)
        
        # Criar contexto de partida para o hedge dinâmico
        match_context = criar_contexto_partida_para_hedge(informacoes_extraidas, estatisticas)
        
        # Calcular cenários críticos para hedge
        analyzer = get_analyzer()
        zero_result = analyzer.calculate_scenario_profit(0, 0, None)
        fav_result = analyzer.calculate_scenario_profit(1, 1, True)
        aza_result = analyzer.calculate_scenario_profit(1, 1, False)
        
        # Preparar dados para transmissão
        dados_transmissao = {
            'relatorio_completo': relatorio_completo,
            'informacoes_extraidas': informacoes_extraidas,
            'match_context': match_context,
            'cenarios_criticos': {
                'zero_profit': zero_result['Lucro/Prejuízo'],
                'fav_profit': fav_result['Lucro/Prejuízo'], 
                'aza_profit': aza_result['Lucro/Prejuízo']
            },
            'odds': odds,
            'investments': investments,
            'timestamp': datetime.now().isoformat()
        }
        
        # Armazenar no session_state para acesso do módulo dinâmico
        st.session_state.ultima_analise_transmitida = dados_transmissao
        st.session_state.hedge_manager.ultima_analise_recebida = dados_transmissao
        
        # Registrar operação no memory manager
        if hasattr(st.session_state.hedge_manager, 'memory_manager'):
            st.session_state.hedge_manager.memory_manager.add_learning_note(
                f"Análise recebida do Sistema Conquistador: {informacoes_extraidas['cenario_principal']}"
            )
        
        st.success("✅ **ANÁLISE TRANSMITIDA COM SUCESSO!**")
        st.info("📊 O módulo de hedge dinâmico agora tem todas as informações para fornecer recomendações precisas.")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao transmitir análise para hedge dinâmico: {e}")
        return False

def extrair_informacoes_do_relatorio(relatorio: str) -> Dict:
    """Extrai informações estruturadas do relatório de análise"""
    informacoes = {
        'liga': 'Não identificada',
        'importancia': 'Média',
        'condicoes_especiais': [],
        'motivacao_favorito': 'Média',
        'cenario_principal': 'Não identificado',
        'confianca_cenario': 'Moderada',
        'estilo_jogo_favorito': 'Equilibrado',
        'pressao_favorito': 'Média',
        'consistencia_azarao': 'Regular',
        'historico_confrontos': 'Equilibrado',
        'probabilidade_azarao_marcar': 50.0
    }
    
    try:
        linhas = relatorio.split('\n')
        
        for i, linha in enumerate(linhas):
            # Extrair liga
            if 'Liga/Campeonato:' in linha:
                informacoes['liga'] = linha.split(':')[-1].strip()
            
            # Extrair importância
            elif 'Importância:' in linha:
                informacoes['importancia'] = linha.split(':')[-1].strip()
            
            # Extrair condições especiais
            elif 'Condições Especiais:' in linha:
                condicoes = linha.split(':')[-1].strip()
                if condicoes != 'Nenhuma':
                    informacoes['condicoes_especiais'] = [c.strip() for c in condicoes.split(',')]
            
            # Extrair motivação do favorito
            elif 'Motivação do Favorito:' in linha:
                informacoes['motivacao_favorito'] = linha.split(':')[-1].strip()
            
            # Extrair cenário principal
            elif 'Cenário Mais Provável:' in linha:
                cenario_completo = linha.split(':')[-1].strip()
                if '(' in cenario_completo:
                    cenario = cenario_completo.split('(')[0].strip()
                    confianca = cenario_completo.split('(')[1].replace(')', '').strip()
                    informacoes['cenario_principal'] = cenario
                    informacoes['confianca_cenario'] = confianca
            
            # Extrair estilo de jogo
            elif 'Estilo do Favorito:' in linha:
                informacoes['estilo_jogo_favorito'] = linha.split(':')[-1].strip()
            
            # Extrair pressão
            elif 'Pressão sobre Favorito:' in linha:
                informacoes['pressao_favorito'] = linha.split(':')[-1].strip()
            
            # Extrair consistência
            elif 'Consistência do Azarão:' in linha:
                informacoes['consistencia_azarao'] = linha.split(':')[-1].strip()
            
            # Extrair histórico
            elif 'Histórico de Confrontos:' in linha:
                informacoes['historico_confrontos'] = linha.split(':')[-1].strip()
            
            # Calcular probabilidade do azarão marcar baseado no contexto
            if 'Azarão' in linha and 'marcar' in linha.lower():
                if 'Muito Irregular' in linha:
                    informacoes['probabilidade_azarao_marcar'] = 30.0
                elif 'Irregular' in linha:
                    informacoes['probabilidade_azarao_marcar'] = 40.0
                elif 'Consistente' in linha:
                    informacoes['probabilidade_azarao_marcar'] = 60.0
        
        return informacoes
        
    except Exception as e:
        st.warning(f"⚠️ Algumas informações não puderam ser extraídas automaticamente: {e}")
        return informacoes

def criar_contexto_partida_para_hedge(informacoes: Dict, estatisticas: Dict):
    """Cria contexto de partida para o módulo de hedge dinâmico"""
    try:
        from dinamico import MatchContext, MatchStatistics, MatchEvent
        
        # Criar estatísticas baseadas nas informações extraídas
        stats = MatchStatistics(
            possession_fav=55,  # Valor padrão
            possession_aza=45,
            shots_fav=estatisticas.get('gols_feitos_favorito', 8),
            shots_aza=estatisticas.get('gols_feitos_azarao', 4),
            shots_on_target_fav=max(1, estatisticas.get('gols_feitos_favorito', 8) // 2),
            shots_on_target_aza=max(1, estatisticas.get('gols_feitos_azarao', 4) // 2),
            dangerous_attacks_fav=10,
            dangerous_attacks_aza=6,
            corners_fav=5,
            corners_aza=3,
            fouls_fav=8,
            fouls_aza=10,
            offsides_fav=2,
            offsides_aza=1,
            yellow_cards_fav=1,
            yellow_cards_aza=2,
            red_cards_fav=0,
            red_cards_aza=0
        )
        
        # Ajustar baseado no cenário principal
        if 'Vitória convincente' in informacoes['cenario_principal']:
            stats.possession_fav = 65
            stats.possession_aza = 35
            stats.shots_fav += 3
        elif 'Azarão pode marcar' in informacoes['cenario_principal']:
            stats.shots_aza += 2
            stats.dangerous_attacks_aza += 3
        
        # Criar contexto da partida
        context = MatchContext(
            current_score="0x0",  # Partida não iniciada
            minute=0,
            statistics=stats,
            event_type=MatchEvent.MATCH_START,
            momentum="EQUILIBRADO",
            additional_notes=f"Análise pré-partida: {informacoes['cenario_principal']}"
        )
        
        return context
        
    except Exception as e:
        st.warning(f"⚠️ Contexto simplificado criado devido a: {e}")
        return None

def render_detailed_scenario_analysis():
    """Renderiza análise detalhada de cenários com botão de transmissão para hedge"""
    st.subheader("📈 Análise Avançada de Cenários - DETALHADA")
    
    analyzer = get_analyzer()
    total_investment = analyzer.get_total_investment()
    
    # 🔥 NOVO: BOTÃO PARA TRANSMITIR ANÁLISE PARA HEDGE DINÂMICO
    if 'generated_prompt' in st.session_state:
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.markdown("### 🔄 Transmissão para Hedge")
            if st.button("📤 ENVIAR ANÁLISE PARA HEDGE DINÂMICO", 
                        use_container_width=True,
                        type="primary",
                        key="transmitir_analise_hedge"):
                
                with st.spinner("Transmitindo análise para módulo de hedge..."):
                    # Coletar dados necessários
                    estatisticas = {
                        'vitorias_favorito': st.session_state.app_state.get('vitorias_favorito', 3),
                        'gols_feitos_favorito': st.session_state.app_state.get('gols_feitos_favorito', 8),
                        'gols_sofridos_favorito': st.session_state.app_state.get('gols_sofridos_favorito', 3),
                        'vitorias_azarao': st.session_state.app_state.get('vitorias_azarao', 1),
                        'gols_feitos_azarao': st.session_state.app_state.get('gols_feitos_azarao', 4),
                        'gols_sofridos_azarao': st.session_state.app_state.get('gols_sofridos_azarao', 10)
                    }
                    
                    odds = st.session_state.app_state['odds_values']
                    investments = st.session_state.app_state['investment_values']
                    
                    # Transmitir análise
                    sucesso = transmitir_analise_para_hedge(
                        st.session_state['generated_prompt'],
                        estatisticas,
                        odds,
                        investments
                    )
                    
                    if sucesso:
                        st.balloons()
                        st.success("""
                        ✅ **Análise transmitida com sucesso!**
                        
                        **Agora o módulo de hedge dinâmico tem:**
                        - 📊 Contexto completo da partida
                        - 🎯 Cenário principal identificado  
                        - 💰 Situação atual das apostas
                        - 🛡️ Informações de proteção
                        - 📈 Dados para recomendações precisas
                        """)
    
    # Cenários importantes para análise - INCLUINDO CENÁRIOS PROTEGIDOS PELA NOVA APOSTA
    important_scenarios = [
        ('0x0', 0, 0, None, "Empate sem gols"),
        ('1x0 FAV', 1, 0, True, "Vitória do favorito 1x0"),
        ('0x1 AZA', 0, 1, False, "Vitória do azarão 0x1"),
        ('1x1 FAV 1º', 1, 1, True, "Empate 1x1 com gol do favorito primeiro"),
        ('1x1 AZA 1º', 1, 1, False, "Empate 1x1 com gol do azarão primeiro"),
        ('2x0 FAV', 2, 0, True, "Vitória convincente do favorito"),
        ('0x2 AZA', 0, 2, False, "Vitória convincente do azarão"),
        ('2x1 FAV', 2, 1, True, "Vitória do favorito com gol do azarão - PROTEGIDO"),
        ('1x2 AZA', 1, 2, False, "Vitória do azarão com gol do favorito - PROTEGIDO"),
        ('2x2', 2, 2, None, "Empate com muitos gols - PROTEGIDO"),
        ('3x0 FAV', 3, 0, True, "Goleada do favorito"),
        ('0x3 AZA', 0, 3, False, "Goleada do azarão - PROTEGIDO"),
        ('1x3 AZA', 1, 3, False, "Goleada do azarão com gol de honra - PROTEGIDO")
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
            'Status': result['Status'],
            'Protegido': '✅' if away_goals > 0 else '❌'  # Indica se cenário é protegido pela nova aposta
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
            'Proteção Azarão': '✅ SIM' if away_goals > 0 else '❌ NÃO',
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
    
    protected_scenarios = len([s for s in detailed_scenarios if s['Proteção Azarão'] == '✅ SIM'])
    
    # 🔥 GRÁFICOS EXISTENTES
    col1, col2 = st.columns(2)
    with col1:
        fig_profit = px.bar(df_all, x='Cenário', y='Lucro/Prejuízo', color='Protegido',
                           title='Lucro/Prejuízo por Cenário - Proteção Mais 0,5 Azarão (R$)',
                           color_discrete_map={'✅': '#00FF00', '❌': '#FF0000'})
        fig_profit.update_layout(showlegend=True)
        st.plotly_chart(fig_profit, use_container_width=True, key="grafico_lucro_cenarios")
    
    with col2:
        fig_roi = px.bar(df_all, x='Cenário', y='ROI', color='Protegido',
                        title='ROI por Cenário - Proteção Mais 0,5 Azarão (%)',
                        color_discrete_map={'✅': '#00FF00', '❌': '#FF0000'})
        st.plotly_chart(fig_roi, use_container_width=True, key="grafico_roi_cenarios")
    
    # 🔥 RESUMO DA PROTEÇÃO
    st.markdown("### 🛡️ RESUMO DA PROTEÇÃO MAIS 0,5 GOLS AZARÃO")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cenários Protegidos", f"{protected_scenarios}/{len(detailed_scenarios)}")
    
    with col2:
        st.metric("Cenários Lucrativos", f"{profitable_scenarios}/{len(detailed_scenarios)}")
    
    with col3:
        # Calcular eficiência da proteção
        protected_profitable = len([s for s in detailed_scenarios if s['Proteção Azarão'] == '✅ SIM' and s['Status'] == '✅ Lucro'])
        eficiencia = (protected_profitable / protected_scenarios * 100) if protected_scenarios > 0 else 0
        st.metric("Eficiência da Proteção", f"{eficiencia:.1f}%")
    
    with col4:
        st.metric("Cenários Críticos Cobertos", "1x1, 2x1, 1x2, 2x2")
    
    # 🔥 TABELA DETALHADA COM ANÁLISE POR EXTENSO
    st.markdown("### 📋 ANÁLISE DETALHADA POR CENÁRIO")
    
    # Filtros para a tabela
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status = st.selectbox("Filtrar por Status:", 
                                   ["Todos", "✅ Lucro", "❌ Prejuízo", "⚖️ Equilíbrio"])
    with col2:
        filter_protection = st.selectbox("Filtrar por Proteção:", 
                                       ["Todos", "✅ SIM", "❌ NÃO"])
    with col3:
        sort_by = st.selectbox("Ordenar por:", 
                              ["Cenário", "Lucro/Prejuízo", "ROI", "Investimento Total"])
    
    # Aplicar filtros
    filtered_df = df_detailed.copy()
    if filter_status != "Todos":
        filtered_df = filtered_df[filtered_df['Status'] == filter_status]
    if filter_protection != "Todos":
        filtered_df = filtered_df[filtered_df['Proteção Azarão'] == filter_protection]
    
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
    display_columns = ['Cenário', 'Descrição', 'Placar', 'Proteção Azarão', 'Investimento Total', 
                      'Retorno Total', 'Lucro/Prejuízo', 'ROI', 'Status', 'Apostas Vencedoras']
    
    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        height=400
    )

    return scenario_profits

def render_dinamico_integration():
    """Renderiza a integração com o módulo dinâmico - VERSÃO ATUALIZADA COM ANÁLISE RECEBIDA"""
    st.header("🛡️ Hedge Dinâmico com IA")
    
    # 🔥 NOVO: VERIFICAR SE HÁ ANÁLISE TRANSMITIDA
    if hasattr(st.session_state, 'ultima_analise_transmitida'):
        st.success("📊 **ANÁLISE DO SISTEMA CONQUISTADOR RECEBIDA!**")
        
        with st.expander("🔍 Visualizar Análise Transmitida", expanded=False):
            info = st.session_state.ultima_analise_transmitida['informacoes_extraidas']
            st.write(f"**Liga:** {info['liga']}")
            st.write(f"**Cenário Principal:** {info['cenario_principal']}")
            st.write(f"**Confiança:** {info['confianca_cenario']}")
            st.write(f"**Prob. Azarão Marcar:** {info['probabilidade_azarao_marcar']}%")
            
            if st.button("🔄 Usar Esta Análise para Recomendações", key="usar_analise_transmitida"):
                st.session_state.usar_analise_conquistador = True
                st.rerun()
    
    # Verificar disponibilidade do módulo
    if not getattr(st.session_state, 'dinamico_available', True):
        st.error("❌ Módulo dinamico.py não encontrado!")
        st.info("""
        ### 📋 Para habilitar o Hedge Dinâmico COMPLETO:
        
        1. **Certifique-se de que o arquivo `dinamico.py` está na mesma pasta**
        2. **Reinicie a aplicação**
        3. **O sistema de hedge inteligente será carregado automaticamente**
        """)
        return
    
    try:
        from dinamico import render_hedge_controls, render_hedge_results
        
        # Obter dados necessários do sistema principal
        analyzer = get_analyzer()
        
        # 🔥 MELHORIA: Usar análise transmitida se disponível
        if (hasattr(st.session_state, 'ultima_analise_transmitida') and 
            st.session_state.get('usar_analise_conquistador', False)):
            
            cenarios = st.session_state.ultima_analise_transmitida['cenarios_criticos']
            zero_profit = cenarios['zero_profit']
            fav_profit = cenarios['fav_profit'] 
            aza_profit = cenarios['aza_profit']
            
            st.info("🎯 **Usando análise do Sistema Conquistador para recomendações**")
        else:
            # Calcular cenários críticos para o hedge (fallback)
            zero_result = analyzer.calculate_scenario_profit(0, 0, None)
            fav_result = analyzer.calculate_scenario_profit(1, 1, True)
            aza_result = analyzer.calculate_scenario_profit(1, 1, False)
            
            zero_profit = zero_result['Lucro/Prejuízo']
            fav_profit = fav_result['Lucro/Prejuízo']
            aza_profit = aza_result['Lucro/Prejuízo']
        
        # Obter odds atualizadas
        odds_values = st.session_state.app_state['odds_values']
        
        # 🔥 ADICIONAR ODDS ESPECÍFICAS PARA HEDGE
        hedge_odds = odds_values.copy()
        
        # Garantir que todas as odds necessárias para hedge existam
        required_hedge_odds = [
            "Mais 0,5 Gols Azarão", "Dupla Chance X2", "Dupla Chance 1X",
            "Ambas Marcam - Não", "Não Sair Gols", "Mais 2,5 Gols", "Menos 2,5 Gols"
        ]
        
        for required_odd in required_hedge_odds:
            if required_odd not in hedge_odds:
                default_values = {
                    "Mais 0,5 Gols Azarão": 2.10,
                    "Dupla Chance X2": 1.91,
                    "Dupla Chance 1X": 1.80,
                    "Ambas Marcam - Não": 2.00,
                    "Não Sair Gols": 3.00,
                    "Mais 2,5 Gols": 2.20,
                    "Menos 2,5 Gols": 1.65
                }
                hedge_odds[required_odd] = default_values.get(required_odd, 2.0)
        
        # Renderizar controles do hedge
        render_hedge_controls(zero_profit, fav_profit, aza_profit, hedge_odds)
        
        # Mostrar resultados se hedge foi aplicado
        if st.session_state.get('hedge_applied', False):
            render_hedge_results()
            
    except ImportError as e:
        st.error(f"❌ Erro ao importar módulo dinamico: {e}")
        st.session_state.dinamico_available = False
    except Exception as e:
        st.error(f"❌ Erro no módulo dinâmico: {e}")
        
def sync_with_dinamico_module():
    """Sincroniza dados entre os módulos principal e dinâmico"""
    try:
        if 'hedge_manager' in st.session_state and 'app_state' in st.session_state:
            # Sincronizar odds atualizadas
            app_odds = st.session_state.app_state['odds_values']
            
            # Atualizar odds específicas para hedge se necessário
            required_odds = ["Mais 0,5 Gols Azarão", "Dupla Chance X2", "Dupla Chance 1X"]
            for odd_name in required_odds:
                if odd_name not in app_odds:
                    # Adicionar odds padrão se não existirem
                    default_odds = {
                        "Mais 0,5 Gols Azarão": 2.10,
                        "Dupla Chance X2": 1.91,
                        "Dupla Chance 1X": 1.80
                    }
                    st.session_state.app_state['odds_values'][odd_name] = default_odds[odd_name]
            
            return True
    except Exception as e:
        st.warning(f"⚠️ Aviso na sincronização: {e}")
    
    return False

# =============================================
# 🔧 FUNÇÕES AUXILIARES PARA NOMES DOS TIMES
# =============================================

def get_nome_favorito() -> str:
    """Retorna o nome do time favorito"""
    return st.session_state.app_state.get('favorito', 'Favorito')

def get_nome_azarao() -> str:
    """Retorna o nome do time azarão"""
    return st.session_state.app_state.get('azarao', 'Azarão')

def substituir_nomes_texto(texto: str) -> str:
    """Substitui 'Favorito' e 'Azarão' pelos nomes reais"""
    favorito = get_nome_favorito()
    azarao = get_nome_azarao()
    
    texto = texto.replace('Favorito', favorito)
    texto = texto.replace('Azarão', azarao)
    texto = texto.replace('favorito', favorito)
    texto = texto.replace('azarão', azarao)
    
    return texto

# =============================================
# 🚀 FUNÇÃO PRINCIPAL ATUALIZADA
# =============================================

def main_optimized():
    """Função principal otimizada com Sistema Conquistador integrado"""
    st.set_page_config(
        page_title="Analisador de Apostas - Sistema Conquistador PRO",
        page_icon="🔥",
        layout="wide"
    )
    
    st.title("🎯 Analisador Inteligente - SISTEMA CONQUISTADOR PRO")
    st.markdown("### 🏆 **ESTRATÉGIAS OTIMIZADAS:** 4 Distribuições + Proteção Mais 0,5 Gols Azarão")
    
    # 🔥 INICIALIZAÇÃO ROBUSTA
    init_state()
    
    # 🔥 SINCRONIZAÇÃO ENTRE MÓDULOS
    sync_with_dinamico_module()
    
    # Abas principais
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
        render_detailed_scenario_analysis()
    
    with tab4:
        render_dinamico_integration()

# =============================================
# 🚀 EXECUÇÃO PRINCIPAL
# =============================================

if __name__ == "__main__":
    main_optimized()
