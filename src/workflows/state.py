from typing import TypedDict, Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum

class DocumentType(Enum):
    PRIVACY_POLICY = "politica_privacidade"
    CONSENT_FORM = "termo_consentimento"
    CONTRACT_CLAUSE = "clausula_contratual"
    COMMITTEE_MINUTES = "ata_comite"
    CODE_OF_CONDUCT = "codigo_conduta"
    DATA_PROCESSING_AGREEMENT = "acordo_tratamento_dados"
    BREACH_NOTIFICATION = "notificacao_violacao"
    IMPACT_ASSESSMENT = "avaliacao_impacto"

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    OCR_COMPLETE = "ocr_complete"
    CLASSIFIED = "classified"
    RESEARCHED = "researched"
    STRUCTURED = "structured"
    GENERATED = "generated"
    QUALITY_CHECKED = "quality_checked"
    COMPLIANCE_VALIDATED = "compliance_validated"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ERROR = "error"

class DocumentState(TypedDict):
    # Identificação
    document_id: str
    document_type: DocumentType
    company_name: str
    activity_description: str
    created_at: datetime
    updated_at: datetime
    
    # Status e controle
    current_status: ProcessingStatus
    current_step: str
    processing_log: List[str]
    error_messages: List[str]
    
    # Dados de entrada
    uploaded_file: Optional[bytes]
    file_name: Optional[str]
    file_type: Optional[str]
    original_text: Optional[str]
    
    # OCR e extração
    ocr_text: Optional[str]
    ocr_confidence: float
    extracted_data: Dict[str, Any]
    document_classification: Optional[str]
    
    # Pesquisa regulatória
    applicable_laws: List[str]
    legal_basis: List[str]
    regulatory_requirements: List[str]
    compliance_gaps: List[str]
    
    # Estruturação
    document_structure: Optional[Dict[str, Any]]
    required_sections: List[str]
    content_outline: Optional[str]
    
    # Geração de conteúdo
    generated_content: Optional[str]
    content_sections: Dict[str, str]
    legal_clauses: List[str]
    
    # Controle de qualidade
    quality_score: float
    quality_issues: List[str]
    revision_attempts: int
    quality_checklist: Dict[str, bool]
    
    # Conformidade
    compliance_score: float
    compliance_issues: List[str]
    compliance_checklist: Dict[str, bool]
    regulatory_validation: Dict[str, Any]
    
    # Supervisão humana
    human_reviewer: Optional[str]
    human_feedback: Optional[str]
    human_approval: Optional[bool]
    approval_date: Optional[datetime]
    
    # Metadados
    processing_time: float
    agent_performance: Dict[str, float]
    final_document_path: Optional[str]
    
    # Integração
    external_system_id: Optional[str]
    webhook_url: Optional[str]
    notification_sent: bool
    
    # Configurações específicas
    language: str
    jurisdiction: str
    industry_sector: Optional[str]
    data_processing_activities: List[str]
    
    # Status final
    is_complete: bool
    is_approved: bool
    can_be_delivered: bool

class WorkflowContext(TypedDict):
    """Contexto compartilhado entre agentes"""
    workflow_id: str
    user_id: Optional[str]
    session_id: str
    priority: str  # low, medium, high, urgent
    deadline: Optional[datetime]
    custom_requirements: Dict[str, Any]
    template_preferences: Dict[str, Any]
    quality_threshold: float
    compliance_level: str  # basic, standard, strict
