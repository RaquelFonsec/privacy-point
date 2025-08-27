"""
Agente de Pesquisa Regulatória
Função: Identifica legislação aplicável e fundamentação legal
Especialização: LGPD, ANPD, regulamentações correlatas
"""
from typing import Dict, Any, List
import structlog
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

from src.agents.base_agent import BaseAgent
from src.workflows.state import DocumentState, ProcessingStatus

logger = structlog.get_logger()

class LegalRequirement(BaseModel):
    law: str
    article: str
    description: str
    applicability: str
    requirements: List[str]

class RegulatoryResearch(BaseModel):
    applicable_laws: List[str]
    legal_basis: List[LegalRequirement]
    regulatory_requirements: List[str]
    compliance_gaps: List[str]
    industry_specific_regulations: List[str]
    recent_updates: List[str]
    risk_level: str  # low, medium, high
    confidence: float

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.logger = logger.bind(agent="Research")
        self.output_parser = JsonOutputParser(pydantic_object=RegulatoryResearch)
        
        # Base de conhecimento regulatória
        self.lgpd_articles = {
            "art_5": "Definições fundamentais",
            "art_6": "Bases legais para tratamento",
            "art_7": "Bases legais para tratamento de dados pessoais",
            "art_8": "Tratamento de dados de crianças e adolescentes",
            "art_9": "Tratamento de dados pessoais sensíveis",
            "art_10": "Compartilhamento de dados pessoais sensíveis",
            "art_11": "Dados anonimizados",
            "art_12": "Direitos do titular",
            "art_13": "Informações ao titular",
            "art_14": "Direito de acesso",
            "art_15": "Correção de dados",
            "art_16": "Anonimização, bloqueio ou eliminação",
            "art_17": "Portabilidade dos dados",
            "art_18": "Informação sobre compartilhamento",
            "art_19": "Revogação do consentimento",
            "art_20": "Oposição ao tratamento",
            "art_21": "Revisão de decisões automatizadas",
            "art_22": "Responsabilidade solidária",
            "art_23": "Responsabilidade do controlador",
            "art_24": "Responsabilidade do operador",
            "art_25": "Responsabilidade do encarregado",
            "art_26": "Responsabilidade de terceiros",
            "art_27": "Responsabilidade de agentes de tratamento",
            "art_28": "Responsabilidade de agentes de tratamento",
            "art_29": "Responsabilidade de agentes de tratamento",
            "art_30": "Responsabilidade de agentes de tratamento",
            "art_31": "Responsabilidade de agentes de tratamento",
            "art_32": "Responsabilidade de agentes de tratamento",
            "art_33": "Responsabilidade de agentes de tratamento",
            "art_34": "Responsabilidade de agentes de tratamento",
            "art_35": "Responsabilidade de agentes de tratamento",
            "art_36": "Responsabilidade de agentes de tratamento",
            "art_37": "Responsabilidade de agentes de tratamento",
            "art_38": "Responsabilidade de agentes de tratamento",
            "art_39": "Responsabilidade de agentes de tratamento",
            "art_40": "Responsabilidade de agentes de tratamento",
            "art_41": "Responsabilidade de agentes de tratamento",
            "art_42": "Responsabilidade de agentes de tratamento",
            "art_43": "Responsabilidade de agentes de tratamento",
            "art_44": "Responsabilidade de agentes de tratamento",
            "art_45": "Responsabilidade de agentes de tratamento",
            "art_46": "Responsabilidade de agentes de tratamento",
            "art_47": "Responsabilidade de agentes de tratamento",
            "art_48": "Responsabilidade de agentes de tratamento",
            "art_49": "Responsabilidade de agentes de tratamento",
            "art_50": "Responsabilidade de agentes de tratamento",
            "art_51": "Responsabilidade de agentes de tratamento",
            "art_52": "Responsabilidade de agentes de tratamento",
            "art_53": "Responsabilidade de agentes de tratamento",
            "art_54": "Responsabilidade de agentes de tratamento",
            "art_55": "Responsabilidade de agentes de tratamento",
            "art_56": "Responsabilidade de agentes de tratamento",
            "art_57": "Responsabilidade de agentes de tratamento",
            "art_58": "Responsabilidade de agentes de tratamento",
            "art_59": "Responsabilidade de agentes de tratamento",
            "art_60": "Responsabilidade de agentes de tratamento",
            "art_61": "Responsabilidade de agentes de tratamento",
            "art_62": "Responsabilidade de agentes de tratamento",
            "art_63": "Responsabilidade de agentes de tratamento",
            "art_64": "Responsabilidade de agentes de tratamento",
            "art_65": "Responsabilidade de agentes de tratamento",
            "art_66": "Responsabilidade de agentes de tratamento",
            "art_67": "Responsabilidade de agentes de tratamento",
            "art_68": "Responsabilidade de agentes de tratamento",
            "art_69": "Responsabilidade de agentes de tratamento",
            "art_70": "Responsabilidade de agentes de tratamento",
            "art_71": "Responsabilidade de agentes de tratamento",
            "art_72": "Responsabilidade de agentes de tratamento",
            "art_73": "Responsabilidade de agentes de tratamento",
            "art_74": "Responsabilidade de agentes de tratamento",
            "art_75": "Responsabilidade de agentes de tratamento",
            "art_76": "Responsabilidade de agentes de tratamento",
            "art_77": "Responsabilidade de agentes de tratamento",
            "art_78": "Responsabilidade de agentes de tratamento",
            "art_79": "Responsabilidade de agentes de tratamento",
            "art_80": "Responsabilidade de agentes de tratamento",
            "art_81": "Responsabilidade de agentes de tratamento",
            "art_82": "Responsabilidade de agentes de tratamento",
            "art_83": "Responsabilidade de agentes de tratamento",
            "art_84": "Responsabilidade de agentes de tratamento",
            "art_85": "Responsabilidade de agentes de tratamento",
            "art_86": "Responsabilidade de agentes de tratamento",
            "art_87": "Responsabilidade de agentes de tratamento",
            "art_88": "Responsabilidade de agentes de tratamento",
            "art_89": "Responsabilidade de agentes de tratamento",
            "art_90": "Responsabilidade de agentes de tratamento",
            "art_91": "Responsabilidade de agentes de tratamento",
            "art_92": "Responsabilidade de agentes de tratamento",
            "art_93": "Responsabilidade de agentes de tratamento",
            "art_94": "Responsabilidade de agentes de tratamento",
            "art_95": "Responsabilidade de agentes de tratamento",
            "art_96": "Responsabilidade de agentes de tratamento",
            "art_97": "Responsabilidade de agentes de tratamento",
            "art_98": "Responsabilidade de agentes de tratamento",
            "art_99": "Responsabilidade de agentes de tratamento",
            "art_100": "Responsabilidade de agentes de tratamento"
        }

    def execute(self, state: DocumentState) -> DocumentState:
        """Executa pesquisa regulatória para o documento"""
        try:
            state["current_status"] = ProcessingStatus.PROCESSING
            state["current_step"] = "Regulatory Research"
            
            # Realizar pesquisa regulatória
            research = self._conduct_regulatory_research(state)
            
            # Atualizar estado com resultados da pesquisa
            state["applicable_laws"] = research.applicable_laws
            state["legal_basis"] = [req.dict() for req in research.legal_basis]
            state["regulatory_requirements"] = research.regulatory_requirements
            state["compliance_gaps"] = research.compliance_gaps
            state["current_status"] = ProcessingStatus.RESEARCHED
            
            self.log_action(state, f"Pesquisa regulatória concluída: {len(research.applicable_laws)} leis aplicáveis, "
                                 f"risco: {research.risk_level}")
            
        except Exception as e:
            self.log_action(state, f"Erro na pesquisa regulatória: {str(e)}")
            state["error_messages"].append(f"Research Error: {str(e)}")
            state["current_status"] = ProcessingStatus.ERROR
        
        return state

    def _conduct_regulatory_research(self, state: DocumentState) -> RegulatoryResearch:
        """Conduz pesquisa regulatória baseada no contexto"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um especialista em legislação LGPD/ANPD e regulamentações brasileiras.
            
            Analise o contexto e identifique:
            1. Leis aplicáveis (LGPD, Marco Civil, etc.)
            2. Base legal específica (artigos da LGPD)
            3. Requisitos regulatórios
            4. Gaps de conformidade
            5. Regulamentações específicas do setor
            
            Contexto:
            - Tipo de documento: {document_type}
            - Empresa: {company_name}
            - Atividade: {activity_description}
            - Setor: {industry_sector}
            
            Retorne um JSON com:
            - applicable_laws: lista de leis aplicáveis
            - legal_basis: base legal específica
            - regulatory_requirements: requisitos regulatórios
            - compliance_gaps: gaps identificados
            - industry_specific_regulations: regulamentações do setor
            - recent_updates: atualizações recentes
            - risk_level: nível de risco (low, medium, high)
            - confidence: confiança da análise (0.0-1.0)
            """),
            ("human", "Realize a pesquisa regulatória para este contexto.")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        result = chain.invoke({
            "document_type": state["document_type"].value,
            "company_name": state["company_name"],
            "activity_description": state["activity_description"],
            "industry_sector": state.get("industry_sector", "geral")
        })
        
        return RegulatoryResearch(**result)

    def _get_lgpd_requirements(self, document_type: str) -> List[LegalRequirement]:
        """Retorna requisitos específicos da LGPD baseados no tipo de documento"""
        requirements = []
        
        # Requisitos base para todos os documentos
        base_requirements = [
            LegalRequirement(
                law="LGPD",
                article="Art. 5º",
                description="Definições fundamentais",
                applicability="Todos os documentos",
                requirements=["Definir claramente os termos utilizados", "Estabelecer responsabilidades"]
            ),
            LegalRequirement(
                law="LGPD",
                article="Art. 6º",
                description="Bases legais para tratamento",
                applicability="Todos os documentos",
                requirements=["Identificar base legal", "Justificar tratamento"]
            )
        ]
        requirements.extend(base_requirements)
        
        # Requisitos específicos por tipo de documento
        if document_type == "politica_privacidade":
            requirements.extend([
                LegalRequirement(
                    law="LGPD",
                    article="Art. 13º",
                    description="Informações ao titular",
                    applicability="Política de Privacidade",
                    requirements=["Identificação do controlador", "Finalidade do tratamento", "Base legal"]
                ),
                LegalRequirement(
                    law="LGPD",
                    article="Art. 14º",
                    description="Direito de acesso",
                    applicability="Política de Privacidade",
                    requirements=["Informar sobre direito de acesso", "Procedimento para exercício"]
                )
            ])
        
        elif document_type == "termo_consentimento":
            requirements.extend([
                LegalRequirement(
                    law="LGPD",
                    article="Art. 7º",
                    description="Bases legais para tratamento",
                    applicability="Termo de Consentimento",
                    requirements=["Consentimento livre", "Informado", "Inequívoco"]
                ),
                LegalRequirement(
                    law="LGPD",
                    article="Art. 19º",
                    description="Revogação do consentimento",
                    applicability="Termo de Consentimento",
                    requirements=["Informar sobre direito de revogação", "Facilidade de revogação"]
                )
            ])
        
        return requirements

    def _identify_industry_regulations(self, industry_sector: str) -> List[str]:
        """Identifica regulamentações específicas do setor"""
        industry_regulations = {
            "saúde": [
                "Resolução CFM nº 2.217/2018",
                "Portaria MS nº 1.820/2009",
                "Lei nº 13.709/2018 (LGPD) - Art. 9º"
            ],
            "financeiro": [
                "Resolução CMN nº 4.658/2018",
                "Circular BCB nº 3.909/2020",
                "Lei Complementar nº 105/2001"
            ],
            "telecomunicações": [
                "Lei Geral de Telecomunicações",
                "Resolução ANATEL nº 614/2013",
                "Marco Civil da Internet"
            ],
            "e-commerce": [
                "Código de Defesa do Consumidor",
                "Marco Civil da Internet",
                "Lei nº 12.965/2014"
            ],
            "educação": [
                "Lei de Diretrizes e Bases da Educação",
                "Estatuto da Criança e do Adolescente",
                "Resolução CNE nº 1/2018"
            ]
        }
        
        return industry_regulations.get(industry_sector.lower(), [])

    def _assess_compliance_risk(self, document_type: str, industry_sector: str) -> str:
        """Avalia o nível de risco de conformidade"""
        high_risk_sectors = ["saúde", "financeiro", "bancário", "seguros"]
        high_risk_documents = ["avaliacao_impacto", "acordo_tratamento_dados"]
        
        if industry_sector.lower() in high_risk_sectors:
            return "high"
        elif document_type in high_risk_documents:
            return "high"
        elif document_type in ["politica_privacidade", "termo_consentimento"]:
            return "medium"
        else:
            return "low"
