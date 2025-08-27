"""
Agente de Conformidade
Função: Valida aderência total às exigências LGPD/ANPD
Especialização: Compliance regulatório específico
"""
from typing import Dict, Any, List
import structlog
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
import re

from src.agents.base_agent import BaseAgent
from src.workflows.state import DocumentState, ProcessingStatus

logger = structlog.get_logger()

class ComplianceRequirement(BaseModel):
    requirement_id: str
    description: str
    lgpd_article: str
    status: str  # compliant, non_compliant, partial
    evidence: str
    risk_level: str  # low, medium, high, critical

class ComplianceValidation(BaseModel):
    overall_compliance_score: float
    lgpd_compliance_score: float
    anpd_compliance_score: float
    industry_compliance_score: float
    requirements: List[ComplianceRequirement]
    compliance_gaps: List[str]
    risk_assessment: str
    recommendations: List[str]
    is_compliant: bool

class ComplianceAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.logger = logger.bind(agent="Compliance")
        self.output_parser = JsonOutputParser(pydantic_object=ComplianceValidation)

    def execute(self, state: DocumentState) -> DocumentState:
        """Executa validação de conformidade LGPD/ANPD"""
        try:
            state["current_status"] = ProcessingStatus.PROCESSING
            state["current_step"] = "Compliance Validation"
            
            # Realizar validação de conformidade
            validation = self._validate_compliance(state)
            
            # Atualizar estado
            state["compliance_score"] = validation.overall_compliance_score
            state["compliance_issues"] = validation.compliance_gaps
            state["compliance_checklist"] = self._create_compliance_checklist(validation)
            state["regulatory_validation"] = validation.dict()
            
            # Determinar status final
            if validation.is_compliant:
                state["current_status"] = ProcessingStatus.COMPLIANCE_VALIDATED
                self.log_action(state, f"Conformidade validada. Score: {validation.overall_compliance_score:.2f}")
            else:
                state["current_status"] = ProcessingStatus.COMPLIANCE_VALIDATED
                self.log_action(state, f"Conformidade insuficiente. Score: {validation.overall_compliance_score:.2f}")
            
        except Exception as e:
            self.log_action(state, f"Erro na validação de conformidade: {str(e)}")
            state["error_messages"].append(f"Compliance Error: {str(e)}")
            state["current_status"] = ProcessingStatus.ERROR
        
        return state

    def _validate_compliance(self, state: DocumentState) -> ComplianceValidation:
        """Valida conformidade com LGPD/ANPD"""
        content = state.get("generated_content", "")
        document_type = state["document_type"].value
        industry_sector = state.get("industry_sector", "geral")
        
        # Validar requisitos LGPD
        lgpd_requirements = self._validate_lgpd_requirements(content, document_type)
        
        # Validar requisitos ANPD
        anpd_requirements = self._validate_anpd_requirements(content, document_type)
        
        # Validar requisitos específicos do setor
        industry_requirements = self._validate_industry_requirements(content, industry_sector)
        
        # Combinar todos os requisitos
        all_requirements = lgpd_requirements + anpd_requirements + industry_requirements
        
        # Calcular scores
        lgpd_score = self._calculate_requirement_score(lgpd_requirements)
        anpd_score = self._calculate_requirement_score(anpd_requirements)
        industry_score = self._calculate_requirement_score(industry_requirements)
        
        # Score geral ponderado
        overall_score = (lgpd_score * 0.5 + anpd_score * 0.3 + industry_score * 0.2)
        
        # Identificar gaps
        compliance_gaps = self._identify_compliance_gaps(all_requirements)
        
        # Avaliar risco
        risk_assessment = self._assess_compliance_risk(all_requirements)
        
        # Gerar recomendações
        recommendations = self._generate_compliance_recommendations(all_requirements, overall_score)
        
        # Determinar se é compliant
        is_compliant = overall_score >= 0.85 and len([r for r in all_requirements if r.risk_level == "critical"]) == 0
        
        return ComplianceValidation(
            overall_compliance_score=overall_score,
            lgpd_compliance_score=lgpd_score,
            anpd_compliance_score=anpd_score,
            industry_compliance_score=industry_score,
            requirements=all_requirements,
            compliance_gaps=compliance_gaps,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            is_compliant=is_compliant
        )

    def _validate_lgpd_requirements(self, content: str, document_type: str) -> List[ComplianceRequirement]:
        """Valida requisitos específicos da LGPD"""
        requirements = []
        
        # Requisitos base para todos os documentos
        base_requirements = [
            {
                "id": "LGPD_001",
                "description": "Mencionar LGPD explicitamente",
                "article": "Art. 5º",
                "pattern": r'\b(LGPD|Lei Geral de Proteção de Dados)\b',
                "risk": "high"
            },
            {
                "id": "LGPD_002",
                "description": "Identificar controlador de dados",
                "article": "Art. 5º",
                "pattern": r'\b(controlador|responsável)\b',
                "risk": "high"
            },
            {
                "id": "LGPD_003",
                "description": "Especificar finalidade do tratamento",
                "article": "Art. 6º",
                "pattern": r'\b(finalidade|objetivo|propósito)\b',
                "risk": "high"
            },
            {
                "id": "LGPD_004",
                "description": "Mencionar base legal",
                "article": "Art. 7º",
                "pattern": r'\b(base legal|fundamento legal|consentimento|legítimo interesse)\b',
                "risk": "high"
            }
        ]
        
        # Requisitos específicos por tipo de documento
        if document_type == "politica_privacidade":
            base_requirements.extend([
                {
                    "id": "LGPD_005",
                    "description": "Informar direitos do titular",
                    "article": "Art. 12º",
                    "pattern": r'\b(direito|direitos)\b',
                    "risk": "critical"
                },
                {
                    "id": "LGPD_006",
                    "description": "Especificar prazo de retenção",
                    "article": "Art. 15º",
                    "pattern": r'\b(prazo|retenção|armazenamento|eliminação)\b',
                    "risk": "high"
                },
                {
                    "id": "LGPD_007",
                    "description": "Informar contato do DPO",
                    "article": "Art. 41º",
                    "pattern": r'\b(DPO|Encarregado|contato)\b',
                    "risk": "critical"
                }
            ])
        
        elif document_type == "termo_consentimento":
            base_requirements.extend([
                {
                    "id": "LGPD_008",
                    "description": "Consentimento livre e informado",
                    "article": "Art. 7º",
                    "pattern": r'\b(consentimento|livre|informado)\b',
                    "risk": "critical"
                },
                {
                    "id": "LGPD_009",
                    "description": "Direito de revogação",
                    "article": "Art. 19º",
                    "pattern": r'\b(revogação|revogar|cancelar)\b',
                    "risk": "critical"
                },
                {
                    "id": "LGPD_010",
                    "description": "Consequências da negativa",
                    "article": "Art. 7º",
                    "pattern": r'\b(consequência|negativa|recusa)\b',
                    "risk": "high"
                }
            ])
        
        # Validar cada requisito
        for req in base_requirements:
            status, evidence = self._check_requirement(content, req["pattern"])
            requirements.append(ComplianceRequirement(
                requirement_id=req["id"],
                description=req["description"],
                lgpd_article=req["article"],
                status=status,
                evidence=evidence,
                risk_level=req["risk"]
            ))
        
        return requirements

    def _validate_anpd_requirements(self, content: str, document_type: str) -> List[ComplianceRequirement]:
        """Valida requisitos específicos da ANPD"""
        requirements = []
        
        # Requisitos ANPD
        anpd_requirements = [
            {
                "id": "ANPD_001",
                "description": "Conformidade com orientações ANPD",
                "article": "Orientação ANPD",
                "pattern": r'\b(ANPD|Autoridade Nacional|orientação)\b',
                "risk": "medium"
            },
            {
                "id": "ANPD_002",
                "description": "Linguagem clara e acessível",
                "article": "Princípio da Transparência",
                "pattern": r'\b(claro|acessível|compreensível|simples)\b',
                "risk": "medium"
            },
            {
                "id": "ANPD_003",
                "description": "Informações completas e precisas",
                "article": "Princípio da Precisão",
                "pattern": r'\b(completo|preciso|detalhado|específico)\b',
                "risk": "high"
            }
        ]
        
        for req in anpd_requirements:
            status, evidence = self._check_requirement(content, req["pattern"])
            requirements.append(ComplianceRequirement(
                requirement_id=req["id"],
                description=req["description"],
                lgpd_article=req["article"],
                status=status,
                evidence=evidence,
                risk_level=req["risk"]
            ))
        
        return requirements

    def _validate_industry_requirements(self, content: str, industry_sector: str) -> List[ComplianceRequirement]:
        """Valida requisitos específicos do setor"""
        requirements = []
        
        # Requisitos específicos por setor
        sector_requirements = {
            "saúde": [
                {
                    "id": "SAUDE_001",
                    "description": "Conformidade com regulamentações de saúde",
                    "article": "Resolução CFM",
                    "pattern": r'\b(saúde|médico|tratamento|diagnóstico)\b',
                    "risk": "critical"
                },
                {
                    "id": "SAUDE_002",
                    "description": "Sigilo profissional",
                    "article": "Código de Ética Médica",
                    "pattern": r'\b(sigilo|confidencialidade|segredo)\b',
                    "risk": "critical"
                }
            ],
            "financeiro": [
                {
                    "id": "FIN_001",
                    "description": "Conformidade com regulamentações financeiras",
                    "article": "Resolução CMN",
                    "pattern": r'\b(financeiro|bancário|crédito|investimento)\b',
                    "risk": "critical"
                },
                {
                    "id": "FIN_002",
                    "description": "Sigilo bancário",
                    "article": "Lei Complementar 105/2001",
                    "pattern": r'\b(sigilo bancário|confidencialidade)\b',
                    "risk": "critical"
                }
            ],
            "e-commerce": [
                {
                    "id": "ECOMM_001",
                    "description": "Conformidade com Código de Defesa do Consumidor",
                    "article": "CDC",
                    "pattern": r'\b(consumidor|cliente|compra|venda)\b',
                    "risk": "high"
                }
            ]
        }
        
        sector_reqs = sector_requirements.get(industry_sector.lower(), [])
        
        for req in sector_reqs:
            status, evidence = self._check_requirement(content, req["pattern"])
            requirements.append(ComplianceRequirement(
                requirement_id=req["id"],
                description=req["description"],
                lgpd_article=req["article"],
                status=status,
                evidence=evidence,
                risk_level=req["risk"]
            ))
        
        return requirements

    def _check_requirement(self, content: str, pattern: str) -> tuple[str, str]:
        """Verifica se um requisito específico está atendido"""
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        if len(matches) >= 2:
            return "compliant", f"Encontradas {len(matches)} referências"
        elif len(matches) == 1:
            return "partial", f"Encontrada 1 referência"
        else:
            return "non_compliant", "Nenhuma referência encontrada"

    def _calculate_requirement_score(self, requirements: List[ComplianceRequirement]) -> float:
        """Calcula score baseado nos requisitos"""
        if not requirements:
            return 1.0
        
        total_weight = 0
        weighted_score = 0
        
        for req in requirements:
            # Peso baseado no nível de risco
            weight_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            weight = weight_map.get(req.risk_level, 1)
            
            # Score baseado no status
            status_score = {"compliant": 1.0, "partial": 0.5, "non_compliant": 0.0}
            score = status_score.get(req.status, 0.0)
            
            weighted_score += score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0

    def _identify_compliance_gaps(self, requirements: List[ComplianceRequirement]) -> List[str]:
        """Identifica gaps de conformidade"""
        gaps = []
        
        for req in requirements:
            if req.status in ["non_compliant", "partial"]:
                gaps.append(f"{req.description} ({req.lgpd_article}) - {req.evidence}")
        
        return gaps

    def _assess_compliance_risk(self, requirements: List[ComplianceRequirement]) -> str:
        """Avalia risco geral de conformidade"""
        critical_issues = len([r for r in requirements if r.risk_level == "critical" and r.status != "compliant"])
        high_issues = len([r for r in requirements if r.risk_level == "high" and r.status != "compliant"])
        
        if critical_issues > 0:
            return "critical"
        elif high_issues > 2:
            return "high"
        elif high_issues > 0:
            return "medium"
        else:
            return "low"

    def _generate_compliance_recommendations(self, requirements: List[ComplianceRequirement], overall_score: float) -> List[str]:
        """Gera recomendações de conformidade"""
        recommendations = []
        
        # Recomendações baseadas no score geral
        if overall_score < 0.7:
            recommendations.append("Revisão completa de conformidade necessária")
        elif overall_score < 0.85:
            recommendations.append("Melhorias de conformidade recomendadas")
        
        # Recomendações específicas por requisito
        non_compliant = [r for r in requirements if r.status == "non_compliant"]
        partial = [r for r in requirements if r.status == "partial"]
        
        for req in non_compliant:
            if req.risk_level in ["critical", "high"]:
                recommendations.append(f"CRÍTICO: Implementar {req.description}")
        
        for req in partial:
            if req.risk_level in ["critical", "high"]:
                recommendations.append(f"IMPORTANTE: Melhorar {req.description}")
        
        # Recomendações específicas por setor
        if any("SAUDE" in req.requirement_id for req in requirements):
            recommendations.append("Considerar regulamentações específicas do setor de saúde")
        
        if any("FIN" in req.requirement_id for req in requirements):
            recommendations.append("Considerar regulamentações específicas do setor financeiro")
        
        return recommendations

    def _create_compliance_checklist(self, validation: ComplianceValidation) -> Dict[str, bool]:
        """Cria checklist de conformidade"""
        return {
            "lgpd_compliant": validation.lgpd_compliance_score >= 0.85,
            "anpd_compliant": validation.anpd_compliance_score >= 0.8,
            "industry_compliant": validation.industry_compliance_score >= 0.8,
            "overall_compliant": validation.is_compliant,
            "no_critical_risks": validation.risk_assessment != "critical",
            "gaps_identified": len(validation.compliance_gaps) == 0
        }
