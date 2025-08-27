"""
API FastAPI principal para o sistema Privacy Point
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import structlog
from datetime import datetime
import uuid
import asyncio

from src.workflows.workflow import DocumentWorkflow
from src.workflows.state import DocumentState, WorkflowContext
from src.config import config

# Configurar logging
logger = structlog.get_logger()

# Criar aplicação FastAPI
app = FastAPI(
    title="Privacy Point API",
    description="API para automação inteligente de documentos regulatórios LGPD/ANPD",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar workflow
workflow = DocumentWorkflow()

# Modelos Pydantic para requests/responses
class DocumentRequest(BaseModel):
    document_type: str
    company_name: str
    activity_description: str
    industry_sector: Optional[str] = "geral"
    language: Optional[str] = "pt-BR"
    jurisdiction: Optional[str] = "BR"
    custom_requirements: Optional[Dict[str, Any]] = {}
    webhook_url: Optional[str] = None
    external_system_id: Optional[str] = None

class GenerateDocumentRequest(BaseModel):
    document_request: DocumentRequest

class DocumentResponse(BaseModel):
    document_id: str
    status: str
    message: str
    estimated_completion_time: Optional[int] = None

class DocumentStatus(BaseModel):
    document_id: str
    current_status: str
    current_step: str
    is_complete: bool
    is_approved: bool
    processing_time: float
    quality_score: float
    compliance_score: float
    error_messages: List[str]
    created_at: datetime
    updated_at: datetime

class DocumentContent(BaseModel):
    document_id: str
    content: str
    sections: Dict[str, str]
    legal_clauses: List[str]
    quality_issues: List[Dict[str, Any]]
    compliance_gaps: List[str]
    metadata: Dict[str, Any]

class ReviewDecision(BaseModel):
    decision: str  # approved, rejected, needs_revision
    reviewer_name: str
    reviewer_id: str
    feedback: str
    confidence_level: Optional[float] = 0.8

# Middleware para logging
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    end_time = datetime.now()
    
    logger.info(
        f"{request.method} {request.url.path}",
        status_code=response.status_code,
        duration=(end_time - start_time).total_seconds()
    )
    
    return response

# Endpoints principais
@app.post("/api/v1/documents/generate", response_model=DocumentResponse)
async def generate_document(
    request: Request,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    file: Optional[UploadFile] = File(None)
):
    data = await request.json()
    document_request = DocumentRequest(**data)
    """
    Gera um novo documento regulatório
    """
    try:
        # Validar tipo de documento
        valid_types = [
            "politica_privacidade", "termo_consentimento", "clausula_contratual",
            "ata_comite", "codigo_conduta", "acordo_tratamento_dados",
            "notificacao_violacao", "avaliacao_impacto"
        ]
        
        if document_request.document_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de documento inválido. Tipos válidos: {valid_types}"
            )
        
        # Ler arquivo se fornecido
        file_content = None
        if file:
            file_content = await file.read()
            
            # Validar tamanho do arquivo
            if len(file_content) > config.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Arquivo muito grande. Tamanho máximo: {config.MAX_FILE_SIZE} bytes"
                )
        
        # Criar contexto do workflow
        context = WorkflowContext(
            workflow_id=str(uuid.uuid4()),
            user_id=None,  # Implementar autenticação
            session_id=str(uuid.uuid4()),
            priority="medium",
            deadline=None,
            custom_requirements=document_request.custom_requirements,
            template_preferences={},
            quality_threshold=0.8,
            compliance_level="standard"
        )
        
        # Criar estado inicial
        initial_state = workflow.create_initial_state(
            document_type=document_request.document_type,
            company_name=document_request.company_name,
            activity_description=document_request.activity_description,
            uploaded_file=file_content,
            context=context
        )
        
        # Adicionar informações adicionais
        initial_state["language"] = document_request.language
        initial_state["jurisdiction"] = document_request.jurisdiction
        initial_state["industry_sector"] = document_request.industry_sector
        initial_state["webhook_url"] = document_request.webhook_url
        initial_state["external_system_id"] = document_request.external_system_id
        
        # Executar workflow em background
        background_tasks.add_task(execute_workflow_async, initial_state)
        
        # Estimar tempo de conclusão
        estimated_time = estimate_completion_time(document_request.document_type, document_request.industry_sector)
        
        logger.info(f"Documento {initial_state['document_id']} iniciado")
        
        return DocumentResponse(
            document_id=initial_state["document_id"],
            status="processing",
            message="Documento iniciado com sucesso",
            estimated_completion_time=estimated_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar documento: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/v1/documents/{document_id}/status", response_model=DocumentStatus)
async def get_document_status(document_id: str):
    """
    Obtém o status atual de um documento
    """
    try:
        status = workflow.get_workflow_status(document_id)
        
        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        elif status.get("status") == "error":
            raise HTTPException(status_code=500, detail=status.get("error", "Erro desconhecido"))
        
        return DocumentStatus(
            document_id=document_id,
            current_status=status.get("current_status", "unknown"),
            current_step=status.get("current_step", "unknown"),
            is_complete=status.get("is_complete", False),
            is_approved=status.get("is_approved", False),
            processing_time=status.get("processing_time", 0.0),
            quality_score=status.get("quality_score", 0.0),
            compliance_score=status.get("compliance_score", 0.0),
            error_messages=status.get("error_messages", []),
            created_at=datetime.now(),  # Implementar recuperação real
            updated_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/v1/documents/{document_id}/content", response_model=DocumentContent)
async def get_document_content(document_id: str):
    """
    Obtém o conteúdo de um documento aprovado
    """
    try:
        # Recuperar estado do documento
        thread = workflow.app.get_state({"configurable": {"thread_id": document_id}})
        
        if not thread or not thread.values:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        state = thread.values[-1]
        
        if not state.get("is_approved", False):
            raise HTTPException(status_code=400, detail="Documento ainda não foi aprovado")
        
        return DocumentContent(
            document_id=document_id,
            content=state.get("generated_content", ""),
            sections=state.get("content_sections", {}),
            legal_clauses=state.get("legal_clauses", []),
            quality_issues=state.get("quality_issues", []),
            compliance_gaps=state.get("compliance_issues", []),
            metadata={
                "document_type": state.get("document_type", ""),
                "company_name": state.get("company_name", ""),
                "quality_score": state.get("quality_score", 0.0),
                "compliance_score": state.get("compliance_score", 0.0),
                "processing_time": state.get("processing_time", 0.0),
                "created_at": state.get("created_at", datetime.now()).isoformat(),
                "approved_at": state.get("approval_date", datetime.now()).isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter conteúdo: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/api/v1/documents/{document_id}/review")
async def submit_review_decision(
    document_id: str,
    decision: ReviewDecision
):
    """
    Submete decisão de revisão humana
    """
    try:
        # Recuperar estado atual
        thread = workflow.app.get_state({"configurable": {"thread_id": document_id}})
        
        if not thread or not thread.values:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        current_state = thread.values[-1]
        
        # Processar decisão
        reviewer_info = {
            "reviewer_id": decision.reviewer_id,
            "reviewer_name": decision.reviewer_name,
            "confidence_level": decision.confidence_level,
            "review_time_minutes": 5  # Implementar cálculo real
        }
        
        updated_state = workflow.human_supervision_agent.process_review_decision(
            current_state, decision.decision, reviewer_info, decision.feedback
        )
        
        # Atualizar estado no workflow
        workflow.app.update_state(
            {"configurable": {"thread_id": document_id}},
            updated_state
        )
        
        logger.info(f"Decisão de revisão submetida para {document_id}: {decision.decision}")
        
        return {
            "document_id": document_id,
            "status": "review_processed",
            "decision": decision.decision,
            "message": "Decisão de revisão processada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar decisão de revisão: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.delete("/api/v1/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Remove um documento do sistema
    """
    try:
        # Em uma implementação real, isso removeria o documento do storage
        # Por enquanto, apenas retornamos sucesso
        logger.info(f"Documento {document_id} removido")
        
        return {
            "document_id": document_id,
            "status": "deleted",
            "message": "Documento removido com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao remover documento: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/v1/health")
async def health_check():
    """
    Verifica saúde da API
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/v1/metrics")
async def get_metrics():
    """
    Obtém métricas do sistema
    """
    # Implementar métricas reais
    return {
        "total_documents_processed": 0,
        "average_processing_time": 0.0,
        "success_rate": 0.0,
        "active_workflows": 0
    }

# Funções auxiliares
async def execute_workflow_async(initial_state: DocumentState):
    """Executa workflow de forma assíncrona"""
    try:
        final_state = workflow.execute_workflow(initial_state)
        
        # Enviar webhook se configurado
        if final_state.get("webhook_url"):
            await send_webhook_notification(final_state)
            
        logger.info(f"Workflow concluído para {initial_state['document_id']}")
        
    except Exception as e:
        logger.error(f"Erro no workflow assíncrono: {e}")

async def send_webhook_notification(state: DocumentState):
    """Envia notificação webhook"""
    try:
        import httpx
        
        payload = {
            "document_id": state["document_id"],
            "status": state["current_status"],
            "is_complete": state["is_complete"],
            "is_approved": state["is_approved"],
            "processing_time": state["processing_time"],
            "quality_score": state["quality_score"],
            "compliance_score": state["compliance_score"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(state["webhook_url"], json=payload)
            
        logger.info(f"Webhook enviado para {state['webhook_url']}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar webhook: {e}")

def estimate_completion_time(document_type: str, industry_sector: str) -> int:
    """Estima tempo de conclusão em minutos"""
    base_times = {
        "politica_privacidade": 15,
        "termo_consentimento": 8,
        "clausula_contratual": 12,
        "ata_comite": 5,
        "codigo_conduta": 18,
        "acordo_tratamento_dados": 20,
        "notificacao_violacao": 10,
        "avaliacao_impacto": 25
    }
    
    base_time = base_times.get(document_type, 15)
    
    # Ajustar baseado no setor
    if industry_sector in ["saúde", "financeiro", "bancário"]:
        base_time += 5  # Setores regulados levam mais tempo
    
    return base_time

# Configurar logging
if __name__ == "__main__":
    import uvicorn
    
    # Validar configurações
    if not config.validate():
        logger.error("Configurações inválidas. Verifique as variáveis de ambiente.")
        exit(1)
    
    logger.info("Iniciando Privacy Point API")
    
    uvicorn.run(
        "src.api.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        workers=config.API_WORKERS,
        reload=config.DEBUG
    )
