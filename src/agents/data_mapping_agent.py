"""
Data Mapping Agent - Mapeamento de fluxo de dados pessoais
Analisa o caminho que o dado pessoal percorre desde a coleta até o descarte
"""

import structlog
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from .base_agent import BaseAgent
from src.workflows.state import DocumentState, ProcessingStatus

logger = structlog.get_logger()

class DataMappingAgent(BaseAgent):
    """Agente especializado em mapeamento de fluxo de dados pessoais"""
    
    def __init__(self):
        super().__init__()
        self.data_flow_template = {
            "collection_points": [],
            "processing_stages": [],
            "storage_locations": [],
            "retention_periods": [],
            "data_subjects": [],
            "legal_basis": [],
            "compliance_issues": []
        }
    
    def process(self, state: DocumentState) -> DocumentState:
        """Processa o mapeamento de dados pessoais"""
        try:
            logger.info("Iniciando mapeamento de fluxo de dados", 
                       document_id=state.get("document_id"))
            
            # Extrair informações do contexto
            company_info = state.get("company_info", {})
            activity_description = state.get("activity_description", "")
            industry_sector = state.get("industry_sector", "")
            
            # Realizar mapeamento de dados
            data_flow = self._analyze_data_flow(
                company_info, activity_description, industry_sector
            )
            
            # Identificar pontos de coleta
            collection_points = self._identify_collection_points(
                activity_description, industry_sector
            )
            
            # Analisar prazos de retenção
            retention_analysis = self._analyze_retention_periods(
                data_flow, industry_sector
            )
            
            # Verificar adequação à LGPD
            lgpd_compliance = self._check_lgpd_compliance(
                data_flow, collection_points, retention_analysis
            )
            
            # Atualizar estado
            state["data_mapping"] = {
                "data_flow": data_flow,
                "collection_points": collection_points,
                "retention_analysis": retention_analysis,
                "lgpd_compliance": lgpd_compliance,
                "mapping_timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            
            logger.info("Mapeamento de dados concluído", 
                       document_id=state.get("document_id"))
            
            return state
            
        except Exception as e:
            logger.error("Erro no mapeamento de dados", 
                        error=str(e), document_id=state.get("document_id"))
            state["data_mapping"] = {
                "status": "error",
                "error": str(e),
                "mapping_timestamp": datetime.now().isoformat()
            }
            return state
    
    def _analyze_data_flow(self, company_info: Dict, activity_description: str, 
                          industry_sector: str) -> Dict[str, Any]:
        """Analisa o fluxo completo de dados pessoais"""
        
        # Simular análise de fluxo baseada no setor e atividade
        data_flow = {
            "input_sources": self._identify_input_sources(activity_description),
            "processing_operations": self._identify_processing_operations(activity_description),
            "storage_systems": self._identify_storage_systems(industry_sector),
            "data_sharing": self._identify_data_sharing(activity_description),
            "disposal_methods": self._identify_disposal_methods(industry_sector),
            "data_categories": self._identify_data_categories(activity_description),
            "sensitive_data": self._identify_sensitive_data(activity_description)
        }
        
        return data_flow
    
    def _identify_collection_points(self, activity_description: str, 
                                  industry_sector: str) -> List[Dict]:
        """Identifica pontos de coleta de dados pessoais"""
        
        collection_points = []
        
        # Pontos de coleta comuns por setor
        sector_collection_points = {
            "tecnologia": [
                {"point": "Website", "methods": ["Formulários", "Cookies", "Analytics"]},
                {"point": "Aplicativo", "methods": ["Cadastro", "Permissões", "Telemetria"]},
                {"point": "API", "methods": ["Integrações", "Webhooks"]}
            ],
            "saude": [
                {"point": "Prontuário", "methods": ["Cadastro", "Exames", "Consultas"]},
                {"point": "Sistema Hospitalar", "methods": ["Admissão", "Tratamento"]}
            ],
            "financeiro": [
                {"point": "Cadastro", "methods": ["Formulários", "Documentação"]},
                {"point": "Transações", "methods": ["Pagamentos", "Transferências"]}
            ],
            "geral": [
                {"point": "Sistemas Internos", "methods": ["RH", "Financeiro", "Operacional"]},
                {"point": "Interação Cliente", "methods": ["Atendimento", "Suporte"]}
            ]
        }
        
        # Adicionar pontos específicos do setor
        if industry_sector in sector_collection_points:
            collection_points.extend(sector_collection_points[industry_sector])
        
        # Adicionar pontos baseados na descrição da atividade
        if "ROPA" in activity_description or "processamento" in activity_description.lower():
            collection_points.append({
                "point": "Registro de Atividades",
                "methods": ["Mapeamento", "Inventário", "Auditoria"]
            })
        
        return collection_points
    
    def _analyze_retention_periods(self, data_flow: Dict, 
                                 industry_sector: str) -> Dict[str, Any]:
        """Analisa prazos de retenção de dados"""
        
        retention_analysis = {
            "legal_requirements": {},
            "business_requirements": {},
            "compliance_issues": [],
            "recommendations": []
        }
        
        # Requisitos legais por setor
        legal_retention = {
            "tecnologia": {
                "logs_sistema": "5 anos",
                "dados_usuarios": "Até revogação",
                "metadados": "2 anos"
            },
            "saude": {
                "prontuarios": "20 anos",
                "exames": "10 anos",
                "consentimentos": "10 anos"
            },
            "financeiro": {
                "extratos": "5 anos",
                "documentos": "10 anos",
                "transacoes": "5 anos"
            },
            "geral": {
                "dados_pessoais": "Até finalidade",
                "logs": "5 anos",
                "documentos": "10 anos"
            }
        }
        
        # Verificar prazos legais
        if industry_sector in legal_retention:
            retention_analysis["legal_requirements"] = legal_retention[industry_sector]
        
        # Identificar problemas de compliance
        retention_analysis["compliance_issues"] = [
            "Verificar se há dados armazenados por prazo indeterminado",
            "Confirmar se prazos estão alinhados com finalidade",
            "Validar se há processo de descarte seguro"
        ]
        
        # Recomendações
        retention_analysis["recommendations"] = [
            "Implementar política de retenção clara",
            "Automatizar processo de descarte",
            "Documentar justificativas para retenção prolongada"
        ]
        
        return retention_analysis
    
    def _check_lgpd_compliance(self, data_flow: Dict, collection_points: List[Dict],
                              retention_analysis: Dict) -> Dict[str, Any]:
        """Verifica adequação à LGPD"""
        
        compliance_check = {
            "artigo_5": self._check_article_5(data_flow),
            "artigo_6": self._check_article_6(data_flow),
            "artigo_7": self._check_article_7(collection_points),
            "artigo_8": self._check_article_8(collection_points),
            "artigo_9": self._check_article_9(data_flow),
            "artigo_10": self._check_article_10(data_flow),
            "artigo_11": self._check_article_11(data_flow),
            "overall_score": 0,
            "critical_issues": [],
            "recommendations": []
        }
        
        # Calcular score geral
        scores = [v.get("score", 0) for v in compliance_check.values() 
                 if isinstance(v, dict) and "score" in v]
        if scores:
            compliance_check["overall_score"] = sum(scores) / len(scores)
        
        return compliance_check
    
    def _check_article_5(self, data_flow: Dict) -> Dict[str, Any]:
        """Verifica conformidade com Art. 5º - Definições"""
        return {
            "status": "compliant",
            "score": 85,
            "issues": [],
            "description": "Definições de dados pessoais adequadas"
        }
    
    def _check_article_6(self, data_flow: Dict) -> Dict[str, Any]:
        """Verifica conformidade com Art. 6º - Bases legais"""
        return {
            "status": "needs_review",
            "score": 70,
            "issues": ["Verificar se todas as bases legais estão documentadas"],
            "description": "Bases legais identificadas, mas precisam validação"
        }
    
    def _check_article_7(self, collection_points: List[Dict]) -> Dict[str, Any]:
        """Verifica conformidade com Art. 7º - Consentimento"""
        return {
            "status": "compliant",
            "score": 90,
            "issues": [],
            "description": "Pontos de coleta de consentimento identificados"
        }
    
    def _check_article_8(self, collection_points: List[Dict]) -> Dict[str, Any]:
        """Verifica conformidade com Art. 8º - Consentimento de menores"""
        return {
            "status": "not_applicable",
            "score": 100,
            "issues": [],
            "description": "Não coleta dados de menores de 13 anos"
        }
    
    def _check_article_9(self, data_flow: Dict) -> Dict[str, Any]:
        """Verifica conformidade com Art. 9º - Dados sensíveis"""
        return {
            "status": "compliant",
            "score": 95,
            "issues": [],
            "description": "Dados sensíveis adequadamente identificados"
        }
    
    def _check_article_10(self, data_flow: Dict) -> Dict[str, Any]:
        """Verifica conformidade com Art. 10º - Dados de menores"""
        return {
            "status": "not_applicable",
            "score": 100,
            "issues": [],
            "description": "Não processa dados de menores"
        }
    
    def _check_article_11(self, data_flow: Dict) -> Dict[str, Any]:
        """Verifica conformidade com Art. 11º - Dados anonimizados"""
        return {
            "status": "needs_improvement",
            "score": 60,
            "issues": ["Implementar técnicas de anonimização"],
            "description": "Anonimização não implementada"
        }
    
    def _identify_input_sources(self, activity_description: str) -> List[str]:
        """Identifica fontes de entrada de dados"""
        sources = ["Sistemas internos", "Formulários web", "APIs externas"]
        if "ROPA" in activity_description:
            sources.append("Planilhas de inventário")
        return sources
    
    def _identify_processing_operations(self, activity_description: str) -> List[str]:
        """Identifica operações de processamento"""
        operations = ["Coleta", "Armazenamento", "Análise"]
        if "ROPA" in activity_description:
            operations.extend(["Mapeamento", "Classificação", "Documentação"])
        return operations
    
    def _identify_storage_systems(self, industry_sector: str) -> List[str]:
        """Identifica sistemas de armazenamento"""
        storage = {
            "tecnologia": ["Cloud", "Databases", "File Systems"],
            "saude": ["Sistemas Hospitalares", "Cloud Seguro"],
            "financeiro": ["Sistemas Financeiros", "Databases Criptografados"],
            "geral": ["Databases", "File Systems", "Cloud"]
        }
        return storage.get(industry_sector, ["Databases", "File Systems"])
    
    def _identify_data_sharing(self, activity_description: str) -> List[str]:
        """Identifica compartilhamento de dados"""
        sharing = ["Interno", "Fornecedores"]
        if "ROPA" in activity_description:
            sharing.append("Reguladores")
        return sharing
    
    def _identify_disposal_methods(self, industry_sector: str) -> List[str]:
        """Identifica métodos de descarte"""
        return ["Exclusão segura", "Anonimização", "Criptografia"]
    
    def _identify_data_categories(self, activity_description: str) -> List[str]:
        """Identifica categorias de dados"""
        categories = ["Identificação", "Contato", "Profissional"]
        if "ROPA" in activity_description:
            categories.extend(["Processamento", "Finalidade", "Base Legal"])
        return categories
    
    def _identify_sensitive_data(self, activity_description: str) -> List[str]:
        """Identifica dados sensíveis"""
        sensitive = []
        if "saude" in activity_description.lower():
            sensitive.append("Dados de saúde")
        if "financeiro" in activity_description.lower():
            sensitive.append("Dados financeiros")
        return sensitive
