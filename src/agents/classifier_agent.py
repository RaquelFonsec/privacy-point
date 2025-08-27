"""
Agente Classificador de Contexto
Função: Analisa a solicitação e identifica o tipo de documento necessário
Especialização: Classificação de documentos LGPD/ANPD (físicos e digitais)
"""
from typing import Dict, Any, List
import structlog
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

from src.agents.base_agent import BaseAgent
from src.workflows.state import DocumentState, ProcessingStatus, DocumentType

logger = structlog.get_logger()

class DocumentClassification(BaseModel):
    document_type: str
    complexity: str  # low, medium, high
    urgency: str  # low, medium, high, urgent
    required_sections: List[str]
    legal_requirements: List[str]
    estimated_pages: int
    confidence: float

class ClassifierAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.logger = logger.bind(agent="Classifier")
        self.output_parser = JsonOutputParser(pydantic_object=DocumentClassification)

    def execute(self, state: DocumentState) -> DocumentState:
        """Analisa o contexto e classifica o documento necessário"""
        try:
            state["current_status"] = ProcessingStatus.PROCESSING
            state["current_step"] = "Document Classification"
            
            # Se temos texto OCR, usar para classificação
            if state.get("ocr_text"):
                classification = self._classify_from_content(state["ocr_text"])
            else:
                # Classificar baseado na solicitação
                classification = self._classify_from_request(state)
            
            # Para testes, garantir que temos valores padrão
            if not hasattr(classification, 'document_type'):
                classification.document_type = state.get("document_type", "politica_privacidade")
            if not hasattr(classification, 'complexity'):
                classification.complexity = "medium"
            if not hasattr(classification, 'confidence'):
                classification.confidence = 0.85
            
            # Atualizar estado com classificação
            state["document_type"] = DocumentType(classification.document_type)
            state["required_sections"] = classification.required_sections
            state["current_status"] = ProcessingStatus.CLASSIFIED
            
            # Adicionar metadados de complexidade
            state["complexity"] = classification.complexity
            state["urgency"] = classification.urgency
            state["estimated_pages"] = classification.estimated_pages
            
            self.log_action(state, f"Documento classificado como: {classification.document_type} "
                                 f"(complexidade: {classification.complexity}, "
                                 f"confiança: {classification.confidence:.2f})")
            
        except Exception as e:
            self.log_action(state, f"Erro na classificação: {str(e)}")
            state["error_messages"].append(f"Classification Error: {str(e)}")
            state["current_status"] = ProcessingStatus.ERROR
        
        return state

    def _classify_from_content(self, content: str) -> DocumentClassification:
        """Classifica documento baseado no conteúdo extraído"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um especialista em classificação de documentos regulatórios LGPD/ANPD.
            
            Analise o conteúdo fornecido e classifique o tipo de documento, complexidade e requisitos.
            
            Tipos de documento possíveis:
            - politica_privacidade: Política de Privacidade
            - termo_consentimento: Termo de Consentimento
            - clausula_contratual: Cláusula Contratual
            - ata_comite: Ata de Comitê
            - codigo_conduta: Código de Conduta
            - acordo_tratamento_dados: Acordo de Tratamento de Dados
            - notificacao_violacao: Notificação de Violação
            - avaliacao_impacto: Avaliação de Impacto
            
            Retorne um JSON com:
            - document_type: tipo do documento
            - complexity: low, medium, high
            - urgency: low, medium, high, urgent
            - required_sections: lista de seções necessárias
            - legal_requirements: requisitos legais específicos
            - estimated_pages: número estimado de páginas
            - confidence: confiança da classificação (0.0-1.0)
            """),
            ("human", "Conteúdo do documento:\n{content}")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        result = chain.invoke({"content": content[:2000]})  # Limitar tamanho
        return DocumentClassification(**result)

    def _classify_from_request(self, state: DocumentState) -> DocumentClassification:
        """Classifica documento baseado na solicitação"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um especialista em classificação de documentos regulatórios LGPD/ANPD.
            
            Analise a solicitação e classifique o tipo de documento necessário.
            
            Contexto da empresa: {company_name} - {activity_description}
            Tipo solicitado: {document_type}
            
            Retorne um JSON com:
            - document_type: tipo do documento
            - complexity: low, medium, high
            - urgency: low, medium, high, urgent
            - required_sections: lista de seções necessárias
            - legal_requirements: requisitos legais específicos
            - estimated_pages: número estimado de páginas
            - confidence: confiança da classificação (0.0-1.0)
            """),
            ("human", "Classifique esta solicitação de documento.")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        result = chain.invoke({
            "company_name": state["company_name"],
            "activity_description": state["activity_description"],
            "document_type": state.get("document_type", "documento_geral")
        })
        
        return DocumentClassification(**result)

    def _get_required_sections(self, document_type: str) -> List[str]:
        """Retorna seções obrigatórias baseadas no tipo de documento"""
        sections_map = {
            "politica_privacidade": [
                "Cabeçalho e Identificação",
                "Objetivo e Escopo",
                "Base Legal",
                "Tipos de Dados Coletados",
                "Finalidade do Tratamento",
                "Compartilhamento de Dados",
                "Direitos do Titular",
                "Segurança dos Dados",
                "Retenção de Dados",
                "Cookies e Tecnologias",
                "Transferências Internacionais",
                "Alterações na Política",
                "Contato do DPO",
                "Data de Vigência"
            ],
            "termo_consentimento": [
                "Identificação da Empresa",
                "Finalidade do Consentimento",
                "Tipos de Dados",
                "Base Legal",
                "Direitos do Titular",
                "Revogação do Consentimento",
                "Consequências da Negativa",
                "Transferências",
                "Retenção",
                "Contato",
                "Aceite Expresso"
            ],
            "clausula_contratual": [
                "Identificação das Partes",
                "Objeto do Contrato",
                "Tratamento de Dados",
                "Obrigações das Partes",
                "Medidas de Segurança",
                "Responsabilidades",
                "Prazo e Rescisão",
                "Foro"
            ],
            "ata_comite": [
                "Cabeçalho da Ata",
                "Participantes",
                "Pauta",
                "Deliberações",
                "Votações",
                "Próxima Reunião",
                "Assinaturas"
            ],
            "codigo_conduta": [
                "Preâmbulo",
                "Princípios Éticos",
                "Tratamento de Dados",
                "Confidencialidade",
                "Conflitos de Interesse",
                "Relacionamento com Terceiros",
                "Conformidade",
                "Disciplina",
                "Disposições Finais"
            ]
        }
        
        return sections_map.get(document_type, ["Seção Geral"])

    def _assess_complexity(self, document_type: str, company_activity: str) -> str:
        """Avalia a complexidade baseada no tipo e atividade da empresa"""
        high_complexity_keywords = [
            "saúde", "financeiro", "bancário", "seguros", "telecomunicações",
            "tecnologia", "e-commerce", "educação", "governo"
        ]
        
        if any(keyword in company_activity.lower() for keyword in high_complexity_keywords):
            return "high"
        elif document_type in ["avaliacao_impacto", "acordo_tratamento_dados"]:
            return "high"
        elif document_type in ["politica_privacidade", "codigo_conduta"]:
            return "medium"
        else:
            return "low"
