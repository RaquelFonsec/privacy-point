"""
Workflow principal do Privacy Point
Orquestração dos agentes especializados usando LangGraph
"""

import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from langgraph.graph import StateGraph, END

from src.agents import (
    OCRAgent, ClassifierAgent, ResearchAgent, StructureAgent, 
    GeneratorAgent, QualityAgent, ComplianceAgent, HumanSupervisionAgent,
    DataMappingAgent, CyberSecurityAgent, LegalExpertAgent
)
from .state import DocumentState, ProcessingStatus, WorkflowContext

logger = structlog.get_logger()

class DocumentWorkflow:
    """Workflow principal para geração de documentos LGPD/ANPD"""
    
    def __init__(self):
        self.agents = {
            "ocr": OCRAgent(),
            "classifier": ClassifierAgent(),
            "data_mapping": DataMappingAgent(),
            "research": ResearchAgent(),
            "legal_expert": LegalExpertAgent(),
            "cyber_security": CyberSecurityAgent(),
            "structure": StructureAgent(),
            "generator": GeneratorAgent(),
            "quality": QualityAgent(),
            "compliance": ComplianceAgent(),
            "human_supervision": HumanSupervisionAgent()
        }
        
        self.graph = self._build_graph()
    
    def create_initial_state(self, document_type: str, company_name: str, 
                           activity_description: str, uploaded_file: Optional[bytes] = None,
                           context: Optional[WorkflowContext] = None) -> DocumentState:
        """Cria o estado inicial para o workflow"""
        
        # Criar contexto padrão se não fornecido
        if context is None:
            context = WorkflowContext(
                workflow_id=str(uuid.uuid4()),
                user_id=None,
                session_id=str(uuid.uuid4()),
                priority="medium",
                deadline=None,
                custom_requirements={},
                template_preferences={},
                quality_threshold=0.8,
                compliance_level="standard"
            )
        
        # Criar estado inicial
        initial_state = DocumentState(
            document_id=str(uuid.uuid4()),
            document_type=document_type,
            company_name=company_name,
            activity_description=activity_description,
            industry_sector="geral",
            language="pt-BR",
            jurisdiction="BR",
            status=ProcessingStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            context=context,
            uploaded_file=uploaded_file,
            ocr_results={},
            classification_results={},
            data_mapping={},
            research_results={},
            legal_expert={},
            cyber_security={},
            structure_results={},
            generated_content="",
            quality_assessment={},
            compliance_validation={},
            human_supervision={},
            processing_log=[],
            error=None,
            is_complete=False,
            is_approved=False,
            quality_score=0.0,
            compliance_score=0.0,
            processing_time=0.0,
            metadata={},
            webhook_url=None,
            external_system_id=None
        )
        
        return initial_state
    
    def get_workflow_status(self, document_id: str) -> Dict[str, Any]:
        """Obtém o status de um workflow específico"""
        # Implementação simplificada - em produção, buscar do banco de dados
        return {
            "document_id": document_id,
            "current_status": "processing",
            "current_step": "ocr",
            "is_complete": False,
            "is_approved": False,
            "processing_time": 0.0,
            "quality_score": 0.0,
            "compliance_score": 0.0,
            "error_messages": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    
    def _build_graph(self) -> StateGraph:
        """Constrói o grafo do workflow"""
        
        # Criar grafo
        workflow = StateGraph(DocumentState)
        
        # Adicionar nós (agentes)
        workflow.add_node("ocr", self._run_ocr)
        workflow.add_node("classifier", self._run_classifier)
        workflow.add_node("data_mapping", self._run_data_mapping)
        workflow.add_node("research", self._run_research)
        workflow.add_node("legal_expert", self._run_legal_expert)
        workflow.add_node("cyber_security", self._run_cyber_security)
        workflow.add_node("structure", self._run_structure)
        workflow.add_node("generator", self._run_generator)
        workflow.add_node("quality", self._run_quality)
        workflow.add_node("compliance", self._run_compliance)
        workflow.add_node("human_supervision", self._run_human_supervision)
        
        # Definir ponto de entrada
        workflow.set_entry_point("ocr")
        
        # Definir fluxo condicional
        workflow.add_conditional_edges(
            "ocr",
            self._should_continue,
            {
                "classifier": "classifier",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "classifier",
            self._should_continue,
            {
                "data_mapping": "data_mapping",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "data_mapping",
            self._should_continue,
            {
                "research": "research",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "research",
            self._should_continue,
            {
                "legal_expert": "legal_expert",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "legal_expert",
            self._should_continue,
            {
                "cyber_security": "cyber_security",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "cyber_security",
            self._should_continue,
            {
                "structure": "structure",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "structure",
            self._should_continue,
            {
                "generator": "generator",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "generator",
            self._should_continue,
            {
                "quality": "quality",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "quality",
            self._should_continue,
            {
                "compliance": "compliance",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "compliance",
            self._should_continue,
            {
                "human_supervision": "human_supervision",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "human_supervision",
            self._should_continue,
            {
                "end": END,
                "error": END
            }
        )
        
        return workflow.compile()
    
    def _run_ocr(self, state: DocumentState) -> DocumentState:
        """Executa o agente OCR"""
        try:
            logger.info("Executando OCR", document_id=state.get("document_id"))
            return self.agents["ocr"].process(state)
        except Exception as e:
            logger.error("Erro no OCR", error=str(e), document_id=state.get("document_id"))
            state["status"] = ProcessingStatus.ERROR
            state["error"] = str(e)
            return state
    
    def _run_classifier(self, state: DocumentState) -> DocumentState:
        """Executa o agente classificador"""
        try:
            logger.info("Executando classificador", document_id=state.get("document_id"))
            return self.agents["classifier"].process(state)
        except Exception as e:
            logger.error("Erro no classificador", error=str(e), document_id=state.get("document_id"))
            state["status"] = ProcessingStatus.ERROR
            state["error"] = str(e)
            return state
    
    def _run_data_mapping(self, state: DocumentState) -> DocumentState:
        """Executa o agente de mapeamento de dados"""
        try:
            logger.info("Executando mapeamento de dados", document_id=state.get("document_id"))
            return self.agents["data_mapping"].process(state)
        except Exception as e:
            logger.error("Erro no mapeamento de dados", error=str(e), document_id=state.get("document_id"))
            state["status"] = ProcessingStatus.ERROR
            state["error"] = str(e)
            return state
    
    def _run_research(self, state: DocumentState) -> DocumentState:
        """Executa o agente de pesquisa"""
        try:
            logger.info("Executando pesquisa", document_id=state.get("document_id"))
            return self.agents["research"].process(state)
        except Exception as e:
            logger.error("Erro na pesquisa", error=str(e), document_id=state.get("document_id"))
            state["status"] = ProcessingStatus.ERROR
            state["error"] = str(e)
            return state
    
    def _run_legal_expert(self, state: DocumentState) -> DocumentState:
        """Executa o agente jurídico especializado"""
        try:
            logger.info("Executando assessoria jurídica", document_id=state.get("document_id"))
            return self.agents["legal_expert"].process(state)
        except Exception as e:
            logger.error("Erro na assessoria jurídica", error=str(e), document_id=state.get("document_id"))
            state["status"] = ProcessingStatus.ERROR
            state["error"] = str(e)
            return state
    
    def _run_cyber_security(self, state: DocumentState) -> DocumentState:
        """Executa o agente de segurança cibernética"""
        try:
            logger.info("Executando avaliação de segurança", document_id=state.get("document_id"))
            return self.agents["cyber_security"].process(state)
        except Exception as e:
            logger.error("Erro na avaliação de segurança", error=str(e), document_id=state.get("document_id"))
            state["status"] = ProcessingStatus.ERROR
            state["error"] = str(e)
            return state
    
    def _run_structure(self, state: DocumentState) -> DocumentState:
        """Executa o agente de estruturação"""
        try:
            logger.info("Executando estruturação", document_id=state.get("document_id"))
            return self.agents["structure"].process(state)
        except Exception as e:
            logger.error("Erro na estruturação", error=str(e), document_id=state.get("document_id"))
            state["status"] = ProcessingStatus.ERROR
            state["error"] = str(e)
            return state
    
    def _run_generator(self, state: DocumentState) -> DocumentState:
        """Executa o agente gerador"""
        try:
            logger.info("Executando geração", document_id=state.get("document_id"))
            return self.agents["generator"].process(state)
        except Exception as e:
            logger.error("Erro na geração", error=str(e), document_id=state.get("document_id"))
            state["status"] = ProcessingStatus.ERROR
            state["error"] = str(e)
            return state
    
    def _run_quality(self, state: DocumentState) -> DocumentState:
        """Executa o agente de qualidade"""
        try:
            logger.info("Executando controle de qualidade", document_id=state.get("document_id"))
            return self.agents["quality"].process(state)
        except Exception as e:
            logger.error("Erro no controle de qualidade", error=str(e), document_id=state.get("document_id"))
            state["status"] = ProcessingStatus.ERROR
            state["error"] = str(e)
            return state
    
    def _run_compliance(self, state: DocumentState) -> DocumentState:
        """Executa o agente de conformidade"""
        try:
            logger.info("Executando validação de conformidade", document_id=state.get("document_id"))
            return self.agents["compliance"].process(state)
        except Exception as e:
            logger.error("Erro na validação de conformidade", error=str(e), document_id=state.get("document_id"))
            state["status"] = ProcessingStatus.ERROR
            state["error"] = str(e)
            return state
    
    def _run_human_supervision(self, state: DocumentState) -> DocumentState:
        """Executa o agente de supervisão humana"""
        try:
            logger.info("Executando supervisão humana", document_id=state.get("document_id"))
            return self.agents["human_supervision"].process(state)
        except Exception as e:
            logger.error("Erro na supervisão humana", error=str(e), document_id=state.get("document_id"))
            state["status"] = ProcessingStatus.ERROR
            state["error"] = str(e)
            return state
    
    def _should_continue(self, state: DocumentState) -> str:
        """Determina se deve continuar ou parar"""
        if state.get("status") == ProcessingStatus.ERROR:
            return "error"
        
        # Verificar se chegou ao final
        if "human_supervision" in state:
            return "end"
        
        return "continue"
    
    def run(self, initial_state: DocumentState) -> DocumentState:
        """Executa o workflow completo"""
        try:
            start_time = datetime.now()
            logger.info("Iniciando workflow", document_id=initial_state.get("document_id"))
            
            # Executar workflow
            final_state = self.graph.invoke(initial_state)
            
            # Calcular tempo de execução
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.info("Workflow concluído", 
                       document_id=initial_state.get("document_id"),
                       status=final_state.get("status"),
                       execution_time=execution_time)
            
            return final_state
            
        except Exception as e:
            logger.error("Erro no workflow", 
                        error=str(e), document_id=initial_state.get("document_id"))
            initial_state["status"] = ProcessingStatus.ERROR
            initial_state["error"] = str(e)
            return initial_state
