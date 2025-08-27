"""
Agente de Supervisão Humana
Função: Interface para revisão e aprovação humana final
Especialização: Facilitação da supervisão obrigatória
"""
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

from src.agents.base_agent import BaseAgent
from src.workflows.state import DocumentState, ProcessingStatus

logger = structlog.get_logger()

class ReviewFeedback(BaseModel):
    reviewer_id: str
    reviewer_name: str
    review_date: datetime
    approval_status: str  # approved, rejected, needs_revision
    feedback: str
    suggested_changes: List[str]
    confidence_level: float
    review_time_minutes: int

class HumanSupervisionAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.logger = logger.bind(agent="HumanSupervision")
        self.output_parser = JsonOutputParser(pydantic_object=ReviewFeedback)

    def execute(self, state: DocumentState) -> DocumentState:
        """Facilita a supervisão humana do documento"""
        try:
            state["current_status"] = ProcessingStatus.PROCESSING
            state["current_step"] = "Human Supervision"
            
            # Preparar documento para revisão humana
            review_package = self._prepare_review_package(state)
            
            # Simular ou aguardar revisão humana
            feedback = self._process_human_review(state, review_package)
            
            # Atualizar estado com feedback
            state["human_reviewer"] = feedback.reviewer_name
            state["human_feedback"] = feedback.feedback
            state["human_approval"] = feedback.approval_status == "approved"
            state["approval_date"] = feedback.review_date
            
            # Determinar próximo status baseado na aprovação
            if feedback.approval_status == "approved":
                state["current_status"] = ProcessingStatus.APPROVED
                state["is_approved"] = True
                state["can_be_delivered"] = True
                self.log_action(state, f"Documento aprovado por {feedback.reviewer_name}")
            elif feedback.approval_status == "needs_revision":
                state["current_status"] = ProcessingStatus.HUMAN_REVIEW
                state["revision_attempts"] = state.get("revision_attempts", 0) + 1
                self.log_action(state, f"Documento requer revisão. Feedback: {feedback.feedback[:100]}...")
            else:  # rejected
                state["current_status"] = ProcessingStatus.REJECTED
                state["is_approved"] = False
                self.log_action(state, f"Documento rejeitado por {feedback.reviewer_name}")
            
        except Exception as e:
            self.log_action(state, f"Erro na supervisão humana: {str(e)}")
            state["error_messages"].append(f"Human Supervision Error: {str(e)}")
            state["current_status"] = ProcessingStatus.ERROR
        
        return state

    def _prepare_review_package(self, state: DocumentState) -> Dict[str, Any]:
        """Prepara pacote completo para revisão humana"""
        review_package = {
            "document_id": state["document_id"],
            "document_type": state["document_type"].value,
            "company_name": state["company_name"],
            "content": state.get("generated_content", ""),
            "quality_assessment": {
                "overall_score": state.get("quality_score", 0.0),
                "issues": state.get("quality_issues", []),
                "recommendations": []
            },
            "compliance_assessment": {
                "overall_score": state.get("compliance_score", 0.0),
                "gaps": state.get("compliance_issues", []),
                "risk_level": state.get("regulatory_validation", {}).get("risk_assessment", "unknown")
            },
            "processing_metadata": {
                "total_sections": len(state.get("content_sections", {})),
                "legal_clauses": len(state.get("legal_clauses", [])),
                "processing_time": state.get("processing_time", 0.0),
                "revision_attempts": state.get("revision_attempts", 0)
            },
            "review_checklist": self._create_review_checklist(state)
        }
        
        return review_package

    def _create_review_checklist(self, state: DocumentState) -> Dict[str, Any]:
        """Cria checklist específico para revisão humana"""
        checklist = {
            "legal_compliance": {
                "lgpd_requirements_met": state.get("compliance_checklist", {}).get("lgpd_compliant", False),
                "anpd_requirements_met": state.get("compliance_checklist", {}).get("anpd_compliant", False),
                "industry_requirements_met": state.get("compliance_checklist", {}).get("industry_compliant", False),
                "no_critical_gaps": state.get("compliance_checklist", {}).get("no_critical_risks", False)
            },
            "quality_standards": {
                "grammar_acceptable": state.get("quality_checklist", {}).get("grammar_acceptable", False),
                "structure_acceptable": state.get("quality_checklist", {}).get("structure_acceptable", False),
                "completeness_acceptable": state.get("quality_checklist", {}).get("completeness_acceptable", False),
                "no_critical_issues": state.get("quality_checklist", {}).get("no_critical_issues", False)
            },
            "content_accuracy": {
                "company_info_correct": state["company_name"] in state.get("generated_content", ""),
                "document_type_appropriate": True,  # Já validado pelo classificador
                "sections_complete": len(state.get("required_sections", [])) == len(state.get("content_sections", {})),
                "legal_basis_accurate": len(state.get("legal_basis", [])) > 0
            },
            "business_context": {
                "industry_specific_content": self._check_industry_specific_content(state),
                "activity_alignment": self._check_activity_alignment(state),
                "risk_appropriate": self._assess_risk_appropriateness(state)
            }
        }
        
        return checklist

    def _process_human_review(self, state: DocumentState, review_package: Dict[str, Any]) -> ReviewFeedback:
        """Processa revisão humana (simulada ou real)"""
        # Em produção, isso seria uma interface real para o revisor humano
        # Por enquanto, simulamos baseado nos scores de qualidade e conformidade
        
        quality_score = state.get("quality_score", 0.0)
        compliance_score = state.get("compliance_score", 0.0)
        revision_attempts = state.get("revision_attempts", 0)
        
        # Lógica de simulação de aprovação
        if quality_score >= 0.85 and compliance_score >= 0.85:
            approval_status = "approved"
            feedback = "Documento aprovado. Conformidade e qualidade adequadas."
            suggested_changes = []
        elif revision_attempts < 2 and (quality_score < 0.8 or compliance_score < 0.8):
            approval_status = "needs_revision"
            feedback = self._generate_revision_feedback(state)
            suggested_changes = self._generate_suggested_changes(state)
        else:
            approval_status = "rejected"
            feedback = "Documento rejeitado. Múltiplas tentativas de revisão sem sucesso."
            suggested_changes = []
        
        return ReviewFeedback(
            reviewer_id="simulated_reviewer_001",
            reviewer_name="Revisor Simulado",
            review_date=datetime.now(),
            approval_status=approval_status,
            feedback=feedback,
            suggested_changes=suggested_changes,
            confidence_level=min(quality_score, compliance_score),
            review_time_minutes=5  # Simulado
        )

    def _generate_revision_feedback(self, state: DocumentState) -> str:
        """Gera feedback específico para revisão"""
        feedback_parts = []
        
        quality_score = state.get("quality_score", 0.0)
        compliance_score = state.get("compliance_score", 0.0)
        
        if quality_score < 0.8:
            feedback_parts.append("Revisar qualidade do conteúdo")
        
        if compliance_score < 0.8:
            feedback_parts.append("Melhorar conformidade legal")
        
        quality_issues = state.get("quality_issues", [])
        compliance_gaps = state.get("compliance_issues", [])
        
        if quality_issues:
            critical_issues = [i for i in quality_issues if i.get("severity") == "critical"]
            if critical_issues:
                feedback_parts.append(f"Corrigir {len(critical_issues)} issues críticos de qualidade")
        
        if compliance_gaps:
            feedback_parts.append(f"Resolver {len(compliance_gaps)} gaps de conformidade")
        
        return ". ".join(feedback_parts) + "."

    def _generate_suggested_changes(self, state: DocumentState) -> List[str]:
        """Gera sugestões específicas de mudanças"""
        suggestions = []
        
        # Sugestões baseadas em issues de qualidade
        quality_issues = state.get("quality_issues", [])
        for issue in quality_issues[:3]:  # Limitar a 3 sugestões
            if issue.get("severity") in ["high", "critical"]:
                suggestions.append(issue.get("suggestion", ""))
        
        # Sugestões baseadas em gaps de conformidade
        compliance_gaps = state.get("compliance_issues", [])
        for gap in compliance_gaps[:2]:  # Limitar a 2 sugestões
            suggestions.append(f"Implementar: {gap}")
        
        # Sugestões gerais baseadas no tipo de documento
        document_type = state["document_type"].value
        if document_type == "politica_privacidade":
            suggestions.append("Verificar se todos os direitos do titular estão claramente explicados")
        elif document_type == "termo_consentimento":
            suggestions.append("Confirmar se o processo de revogação está claramente explicado")
        
        return suggestions[:5]  # Limitar total de sugestões

    def _check_industry_specific_content(self, state: DocumentState) -> bool:
        """Verifica se o conteúdo é específico para o setor"""
        industry_sector = state.get("industry_sector", "")
        content = state.get("generated_content", "")
        
        if not industry_sector or industry_sector == "geral":
            return True
        
        # Verificar se há conteúdo específico do setor
        industry_keywords = {
            "saúde": ["médico", "tratamento", "diagnóstico", "paciente"],
            "financeiro": ["financeiro", "bancário", "crédito", "investimento"],
            "e-commerce": ["consumidor", "cliente", "compra", "venda"],
            "educação": ["educação", "aluno", "professor", "curso"]
        }
        
        keywords = industry_keywords.get(industry_sector.lower(), [])
        return any(keyword in content.lower() for keyword in keywords)

    def _check_activity_alignment(self, state: DocumentState) -> bool:
        """Verifica se o documento está alinhado com a atividade da empresa"""
        activity = state.get("activity_description", "")
        content = state.get("generated_content", "")
        
        if not activity:
            return True
        
        # Verificar se a atividade é mencionada ou refletida no conteúdo
        activity_words = activity.lower().split()
        content_lower = content.lower()
        
        return any(word in content_lower for word in activity_words if len(word) > 3)

    def _assess_risk_appropriateness(self, state: DocumentState) -> bool:
        """Avalia se o nível de risco é apropriado para o contexto"""
        industry_sector = state.get("industry_sector", "")
        risk_assessment = state.get("regulatory_validation", {}).get("risk_assessment", "low")
        
        # Setores de alto risco devem ter avaliação de risco apropriada
        high_risk_sectors = ["saúde", "financeiro", "bancário", "seguros"]
        
        if industry_sector.lower() in high_risk_sectors:
            return risk_assessment in ["medium", "high"]  # Deve ter avaliação de risco adequada
        else:
            return True  # Setores de baixo risco podem ter qualquer avaliação

    def create_review_interface_data(self, state: DocumentState) -> Dict[str, Any]:
        """Cria dados para interface de revisão humana"""
        return {
            "document_summary": {
                "id": state["document_id"],
                "type": state["document_type"].value,
                "company": state["company_name"],
                "created_at": state["created_at"],
                "processing_time": state.get("processing_time", 0.0)
            },
            "quality_metrics": {
                "overall_score": state.get("quality_score", 0.0),
                "grammar_score": state.get("quality_checklist", {}).get("grammar_acceptable", False),
                "structure_score": state.get("quality_checklist", {}).get("structure_acceptable", False),
                "completeness_score": state.get("quality_checklist", {}).get("completeness_acceptable", False)
            },
            "compliance_metrics": {
                "overall_score": state.get("compliance_score", 0.0),
                "lgpd_compliant": state.get("compliance_checklist", {}).get("lgpd_compliant", False),
                "anpd_compliant": state.get("compliance_checklist", {}).get("anpd_compliant", False),
                "industry_compliant": state.get("compliance_checklist", {}).get("industry_compliant", False)
            },
            "content_preview": {
                "sections": list(state.get("content_sections", {}).keys()),
                "legal_clauses": state.get("legal_clauses", []),
                "total_length": len(state.get("generated_content", ""))
            },
            "issues_summary": {
                "quality_issues": len(state.get("quality_issues", [])),
                "compliance_gaps": len(state.get("compliance_issues", [])),
                "critical_issues": len([i for i in state.get("quality_issues", []) if i.get("severity") == "critical"])
            },
            "review_actions": {
                "can_approve": state.get("quality_score", 0.0) >= 0.8 and state.get("compliance_score", 0.0) >= 0.8,
                "can_request_revision": True,
                "can_reject": True,
                "revision_attempts": state.get("revision_attempts", 0)
            }
        }

    def process_review_decision(self, state: DocumentState, decision: str, reviewer_info: Dict[str, Any], feedback: str) -> DocumentState:
        """Processa decisão de revisão humana"""
        review_feedback = ReviewFeedback(
            reviewer_id=reviewer_info.get("reviewer_id", "unknown"),
            reviewer_name=reviewer_info.get("reviewer_name", "Unknown Reviewer"),
            review_date=datetime.now(),
            approval_status=decision,
            feedback=feedback,
            suggested_changes=[],
            confidence_level=reviewer_info.get("confidence_level", 0.8),
            review_time_minutes=reviewer_info.get("review_time_minutes", 0)
        )
        
        # Atualizar estado com feedback
        state["human_reviewer"] = review_feedback.reviewer_name
        state["human_feedback"] = review_feedback.feedback
        state["human_approval"] = review_feedback.approval_status == "approved"
        state["approval_date"] = review_feedback.review_date
        
        # Determinar status final
        if decision == "approved":
            state["current_status"] = ProcessingStatus.APPROVED
            state["is_approved"] = True
            state["can_be_delivered"] = True
        elif decision == "needs_revision":
            state["current_status"] = ProcessingStatus.HUMAN_REVIEW
            state["revision_attempts"] = state.get("revision_attempts", 0) + 1
        else:  # rejected
            state["current_status"] = ProcessingStatus.REJECTED
            state["is_approved"] = False
        
        return state
