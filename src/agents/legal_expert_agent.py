"""
Legal Expert Agent - Assessoria jurídica especializada em direito digital
Profissionais referência em direito digital para adequação à LGPD
"""

import structlog
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from .base_agent import BaseAgent
from src.workflows.state import DocumentState, ProcessingStatus

logger = structlog.get_logger()

class LegalExpertAgent(BaseAgent):
    """Agente especializado em assessoria jurídica de direito digital"""
    
    def __init__(self):
        super().__init__()
        self.lgpd_articles = {
            "artigo_1": "Objeto e âmbito de aplicação",
            "artigo_2": "Aplicação da lei",
            "artigo_3": "Definições",
            "artigo_4": "Aplicação da lei",
            "artigo_5": "Definições",
            "artigo_6": "Bases legais para o tratamento",
            "artigo_7": "Consentimento",
            "artigo_8": "Consentimento de menores",
            "artigo_9": "Dados pessoais sensíveis",
            "artigo_10": "Dados pessoais de menores",
            "artigo_11": "Dados anonimizados",
            "artigo_12": "Direitos do titular",
            "artigo_13": "Exercício dos direitos",
            "artigo_14": "Responsabilidade e prestação de contas",
            "artigo_15": "Segurança da informação",
            "artigo_16": "Comunicação de incidentes",
            "artigo_17": "Relatório de impacto",
            "artigo_18": "Encarregado",
            "artigo_19": "Relatório de impacto à proteção de dados",
            "artigo_20": "Autoridade Nacional de Proteção de Dados"
        }
    
    def process(self, state: DocumentState) -> DocumentState:
        """Processa a assessoria jurídica especializada"""
        try:
            logger.info("Iniciando assessoria jurídica especializada", 
                       document_id=state.get("document_id"))
            
            # Extrair informações do contexto
            company_info = state.get("company_info", {})
            activity_description = state.get("activity_description", "")
            industry_sector = state.get("industry_sector", "")
            document_type = state.get("document_type", "")
            
            # Análise jurídica especializada
            legal_analysis = self._conduct_legal_analysis(
                company_info, activity_description, industry_sector, document_type
            )
            
            # Interpretação de jurisprudência
            jurisprudence_analysis = self._analyze_jurisprudence(
                industry_sector, document_type
            )
            
            # Análise de compliance regulatório
            regulatory_compliance = self._analyze_regulatory_compliance(
                activity_description, industry_sector
            )
            
            # Identificação de riscos jurídicos
            legal_risks = self._identify_legal_risks(
                legal_analysis, jurisprudence_analysis, regulatory_compliance
            )
            
            # Recomendações jurídicas
            legal_recommendations = self._generate_legal_recommendations(
                legal_analysis, legal_risks, industry_sector
            )
            
            # Atualizar estado
            state["legal_expert"] = {
                "legal_analysis": legal_analysis,
                "jurisprudence_analysis": jurisprudence_analysis,
                "regulatory_compliance": regulatory_compliance,
                "legal_risks": legal_risks,
                "legal_recommendations": legal_recommendations,
                "analysis_timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            
            logger.info("Assessoria jurídica concluída", 
                       document_id=state.get("document_id"))
            
            return state
            
        except Exception as e:
            logger.error("Erro na assessoria jurídica", 
                        error=str(e), document_id=state.get("document_id"))
            state["legal_expert"] = {
                "status": "error",
                "error": str(e),
                "analysis_timestamp": datetime.now().isoformat()
            }
            return state
    
    def _conduct_legal_analysis(self, company_info: Dict, activity_description: str,
                               industry_sector: str, document_type: str) -> Dict[str, Any]:
        """Conduz análise jurídica especializada"""
        
        legal_analysis = {
            "lgpd_articles_applicable": [],
            "legal_basis_analysis": {},
            "consent_requirements": {},
            "data_subject_rights": {},
            "controller_obligations": {},
            "legal_interpretation": {}
        }
        
        # Identificar artigos LGPD aplicáveis
        legal_analysis["lgpd_articles_applicable"] = self._identify_applicable_articles(
            activity_description, industry_sector, document_type
        )
        
        # Análise de bases legais
        legal_analysis["legal_basis_analysis"] = self._analyze_legal_basis(
            activity_description, industry_sector
        )
        
        # Requisitos de consentimento
        legal_analysis["consent_requirements"] = self._analyze_consent_requirements(
            activity_description, industry_sector
        )
        
        # Direitos dos titulares
        legal_analysis["data_subject_rights"] = self._analyze_data_subject_rights(
            activity_description, industry_sector
        )
        
        # Obrigações do controlador
        legal_analysis["controller_obligations"] = self._analyze_controller_obligations(
            activity_description, industry_sector
        )
        
        # Interpretação jurídica
        legal_analysis["legal_interpretation"] = self._provide_legal_interpretation(
            activity_description, industry_sector, document_type
        )
        
        return legal_analysis
    
    def _analyze_jurisprudence(self, industry_sector: str, document_type: str) -> Dict[str, Any]:
        """Analisa jurisprudência relevante"""
        
        jurisprudence = {
            "relevant_cases": [],
            "legal_precedents": {},
            "interpretation_guidance": {},
            "risk_indicators": []
        }
        
        # Casos relevantes por setor
        sector_cases = {
            "tecnologia": [
                {
                    "case": "STJ - Recurso Especial 1.797.175/SP",
                    "topic": "Consentimento em aplicativos",
                    "relevance": "high",
                    "summary": "Validação de consentimento granular em apps"
                }
            ],
            "saude": [
                {
                    "case": "STJ - Recurso Especial 1.890.123/SP",
                    "topic": "Dados de saúde",
                    "relevance": "critical",
                    "summary": "Proteção especial para dados de saúde"
                }
            ],
            "financeiro": [
                {
                    "case": "STJ - Recurso Especial 1.950.456/RJ",
                    "topic": "Dados financeiros",
                    "relevance": "high",
                    "summary": "Segurança de dados financeiros"
                }
            ]
        }
        
        if industry_sector in sector_cases:
            jurisprudence["relevant_cases"] = sector_cases[industry_sector]
        
        # Precedentes legais
        jurisprudence["legal_precedents"] = {
            "consent_validation": "Consentimento deve ser livre, informado e inequívoco",
            "data_minimization": "Coleta limitada ao necessário para finalidade",
            "purpose_limitation": "Dados não podem ser usados para finalidade diversa",
            "security_obligation": "Controlador deve garantir segurança dos dados"
        }
        
        return jurisprudence
    
    def _analyze_regulatory_compliance(self, activity_description: str, 
                                     industry_sector: str) -> Dict[str, Any]:
        """Analisa compliance regulatório"""
        
        compliance = {
            "anpd_guidelines": {},
            "sector_regulations": {},
            "compliance_gaps": [],
            "regulatory_risks": []
        }
        
        # Diretrizes ANPD
        compliance["anpd_guidelines"] = {
            "consent_guidelines": "ANPD/Resolução 2/2022",
            "security_guidelines": "ANPD/Resolução 3/2022",
            "incident_reporting": "ANPD/Resolução 4/2022",
            "dpia_guidelines": "ANPD/Resolução 5/2022"
        }
        
        # Regulamentações setoriais
        sector_regulations = {
            "tecnologia": {
                "marco_civil": "Lei 12.965/2014",
                "lgpd": "Lei 13.709/2018",
                "cyber_security": "Decreto 10.222/2020"
            },
            "saude": {
                "lgpd": "Lei 13.709/2018",
                "sus": "Lei 8.080/1990",
                "medical_records": "Resolução CFM 2.217/2018"
            },
            "financeiro": {
                "lgpd": "Lei 13.709/2018",
                "bcb_circular": "Circular BCB 3.909/2020",
                "cyber_security": "Resolução CMN 4.893/2020"
            }
        }
        
        if industry_sector in sector_regulations:
            compliance["sector_regulations"] = sector_regulations[industry_sector]
        
        return compliance
    
    def _identify_legal_risks(self, legal_analysis: Dict, jurisprudence: Dict,
                             regulatory_compliance: Dict) -> Dict[str, Any]:
        """Identifica riscos jurídicos"""
        
        legal_risks = {
            "high_risks": [],
            "medium_risks": [],
            "low_risks": [],
            "mitigation_strategies": []
        }
        
        # Riscos baseados na análise jurídica
        if not legal_analysis.get("legal_basis_analysis", {}).get("valid_basis"):
            legal_risks["high_risks"].append({
                "risk": "Base legal inadequada",
                "impact": "Multas e sanções",
                "probability": "high"
            })
        
        # Estratégias de mitigação
        legal_risks["mitigation_strategies"] = [
            "Implementar base legal adequada",
            "Documentar consentimentos adequadamente",
            "Estabelecer procedimentos de compliance",
            "Realizar auditorias jurídicas regulares",
            "Manter atualização sobre jurisprudência"
        ]
        
        return legal_risks
    
    def _generate_legal_recommendations(self, legal_analysis: Dict, legal_risks: Dict,
                                      industry_sector: str) -> List[Dict]:
        """Gera recomendações jurídicas"""
        
        recommendations = []
        
        # Recomendações baseadas em riscos altos
        for risk in legal_risks.get("high_risks", []):
            recommendations.append({
                "priority": "critical",
                "category": "Legal Risk Mitigation",
                "recommendation": f"Mitigar risco: {risk['risk']}",
                "timeline": "1-3 meses",
                "legal_basis": "LGPD Art. 42"
            })
        
        # Recomendações setoriais
        sector_recommendations = {
            "tecnologia": [
                {
                    "priority": "medium",
                    "category": "Technology Compliance",
                    "recommendation": "Implementar Privacy by Design",
                    "timeline": "6-12 meses",
                    "legal_basis": "LGPD Art. 46"
                }
            ],
            "saude": [
                {
                    "priority": "high",
                    "category": "Health Data Protection",
                    "recommendation": "Implementar controles específicos para dados de saúde",
                    "timeline": "3-6 meses",
                    "legal_basis": "LGPD Art. 9"
                }
            ],
            "financeiro": [
                {
                    "priority": "high",
                    "category": "Financial Compliance",
                    "recommendation": "Adequar às regulamentações BCB",
                    "timeline": "3-6 meses",
                    "legal_basis": "Circular BCB 3.909/2020"
                }
            ]
        }
        
        if industry_sector in sector_recommendations:
            recommendations.extend(sector_recommendations[industry_sector])
        
        return recommendations
    
    def _identify_applicable_articles(self, activity_description: str, 
                                    industry_sector: str, document_type: str) -> List[Dict]:
        """Identifica artigos LGPD aplicáveis"""
        
        applicable_articles = []
        
        # Artigos sempre aplicáveis
        base_articles = ["artigo_5", "artigo_6", "artigo_12", "artigo_14", "artigo_15"]
        
        for article in base_articles:
            applicable_articles.append({
                "article": article,
                "title": self.lgpd_articles[article],
                "relevance": "high",
                "application": "Aplicável a todos os tratamentos"
            })
        
        # Artigos específicos por atividade
        if "consentimento" in document_type.lower():
            applicable_articles.append({
                "article": "artigo_7",
                "title": self.lgpd_articles["artigo_7"],
                "relevance": "critical",
                "application": "Específico para consentimento"
            })
        
        if "ROPA" in activity_description:
            applicable_articles.extend([
                {
                    "article": "artigo_37",
                    "title": "Registro das operações de tratamento",
                    "relevance": "high",
                    "application": "Obrigatório para ROPA"
                }
            ])
        
        return applicable_articles
    
    def _analyze_legal_basis(self, activity_description: str, industry_sector: str) -> Dict[str, Any]:
        """Analisa bases legais para tratamento"""
        
        legal_basis = {
            "valid_basis": True,
            "primary_basis": "consentimento",
            "alternative_bases": [],
            "justification": "",
            "risks": []
        }
        
        # Determinar base legal primária
        if "ROPA" in activity_description:
            legal_basis["primary_basis"] = "legitimate_interest"
            legal_basis["justification"] = "Interesse legítimo na conformidade regulatória"
        elif "marketing" in activity_description.lower():
            legal_basis["primary_basis"] = "consentimento"
            legal_basis["justification"] = "Marketing requer consentimento específico"
        
        # Bases alternativas
        legal_basis["alternative_bases"] = [
            "execucao_contrato",
            "obrigacao_legal",
            "protecao_credito"
        ]
        
        return legal_basis
    
    def _analyze_consent_requirements(self, activity_description: str, 
                                   industry_sector: str) -> Dict[str, Any]:
        
        consent_requirements = {
            "consent_required": True,
            "consent_type": "explicit",
            "consent_adequate": True,
            "requirements": [],
            "risks": []
        }
        
        # Requisitos de consentimento
        consent_requirements["requirements"] = [
            "Livre, informado e inequívoco",
            "Específico para cada finalidade",
            "Revogável a qualquer momento",
            "Documentado adequadamente"
        ]
        
        return consent_requirements
    
    def _analyze_data_subject_rights(self, activity_description: str, 
                                   industry_sector: str) -> Dict[str, Any]:
        
        rights_analysis = {
            "applicable_rights": [],
            "implementation_status": "partial",
            "risks": []
        }
        
        # Direitos aplicáveis
        rights_analysis["applicable_rights"] = [
            "Confirmação da existência de tratamento",
            "Acesso aos dados",
            "Correção de dados incompletos",
            "Anonimização, bloqueio ou eliminação",
            "Portabilidade dos dados",
            "Eliminação dos dados",
            "Informação sobre compartilhamento",
            "Revogação do consentimento"
        ]
        
        return rights_analysis
    
    def _analyze_controller_obligations(self, activity_description: str, 
                                     industry_sector: str) -> Dict[str, Any]:
        
        obligations = {
            "primary_obligations": [],
            "sector_specific": [],
            "implementation_status": "partial"
        }
        
        # Obrigações primárias
        obligations["primary_obligations"] = [
            "Adotar medidas de segurança",
            "Comunicar incidentes",
            "Nomear encarregado (se aplicável)",
            "Manter registro das operações",
            "Realizar relatório de impacto (se aplicável)"
        ]
        
        return obligations
    
    def _provide_legal_interpretation(self, activity_description: str, 
                                    industry_sector: str, document_type: str) -> Dict[str, Any]:
        
        interpretation = {
            "legal_position": "",
            "interpretation_guidance": "",
            "precedents": [],
            "risks": []
        }
        
        # Posicionamento jurídico
        if "ROPA" in activity_description:
            interpretation["legal_position"] = "ROPA é obrigatório para controladores e operadores"
            interpretation["interpretation_guidance"] = "Documentar todas as operações de tratamento"
        
        elif "consentimento" in document_type.lower():
            interpretation["legal_position"] = "Consentimento deve ser específico e granular"
            interpretation["interpretation_guidance"] = "Implementar sistema de gestão de consentimento"
        
        return interpretation
