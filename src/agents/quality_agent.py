"""
Agente de Controle de Qualidade
Função: Revisa consistência, coerência e completude
Especialização: Padrões de qualidade para documentos regulatórios
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

class QualityIssue(BaseModel):
    severity: str  # low, medium, high, critical
    category: str  # grammar, legal, structure, completeness
    description: str
    location: str
    suggestion: str

class QualityAssessment(BaseModel):
    overall_score: float
    grammar_score: float
    legal_score: float
    structure_score: float
    completeness_score: float
    issues: List[QualityIssue]
    recommendations: List[str]
    is_acceptable: bool

class QualityAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.logger = logger.bind(agent="Quality")
        self.output_parser = JsonOutputParser(pydantic_object=QualityAssessment)

    def execute(self, state: DocumentState) -> DocumentState:
        """Executa controle de qualidade do documento gerado"""
        try:
            state["current_status"] = ProcessingStatus.PROCESSING
            state["current_step"] = "Quality Control"
            
            # Realizar avaliação de qualidade
            assessment = self._assess_document_quality(state)
            
            # Atualizar estado
            state["quality_score"] = assessment.overall_score
            state["quality_issues"] = [issue.dict() for issue in assessment.issues]
            state["quality_checklist"] = self._create_quality_checklist(assessment)
            
            # Se qualidade não é aceitável, marcar para revisão
            if not assessment.is_acceptable:
                state["revision_attempts"] = state.get("revision_attempts", 0) + 1
                state["current_status"] = ProcessingStatus.QUALITY_CHECKED
                self.log_action(state, f"Documento requer revisão. Score: {assessment.overall_score:.2f}")
            else:
                state["current_status"] = ProcessingStatus.QUALITY_CHECKED
                self.log_action(state, f"Qualidade aprovada. Score: {assessment.overall_score:.2f}")
            
        except Exception as e:
            self.log_action(state, f"Erro no controle de qualidade: {str(e)}")
            state["error_messages"].append(f"Quality Error: {str(e)}")
            state["current_status"] = ProcessingStatus.ERROR
        
        return state

    def _assess_document_quality(self, state: DocumentState) -> QualityAssessment:
        """Avalia a qualidade do documento"""
        content = state.get("generated_content", "")
        document_type = state["document_type"].value
        
        # Avaliações específicas
        grammar_score = self._assess_grammar_quality(content)
        legal_score = self._assess_legal_quality(content, state)
        structure_score = self._assess_structure_quality(content, state)
        completeness_score = self._assess_completeness_quality(content, state)
        
        # Calcular score geral
        overall_score = (grammar_score + legal_score + structure_score + completeness_score) / 4
        
        # Identificar issues
        issues = self._identify_quality_issues(content, state)
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(issues, overall_score)
        
        # Determinar se é aceitável
        is_acceptable = overall_score >= 0.8 and len([i for i in issues if i.severity == "critical"]) == 0
        
        return QualityAssessment(
            overall_score=overall_score,
            grammar_score=grammar_score,
            legal_score=legal_score,
            structure_score=structure_score,
            completeness_score=completeness_score,
            issues=issues,
            recommendations=recommendations,
            is_acceptable=is_acceptable
        )

    def _assess_grammar_quality(self, content: str) -> float:
        """Avalia qualidade gramatical"""
        score = 1.0
        
        # Verificar erros comuns
        grammar_issues = [
            (r'\b([a-z])', r'Erro de capitalização'),  # Palavras que deveriam começar com maiúscula
            (r'\s+', r'Espaços múltiplos'),  # Espaços em excesso
            (r'[.!?]\s*[a-z]', r'Falta capitalização após pontuação'),  # Falta capitalização
            (r'\b(eu|tu|ele|ela|nós|vós|eles|elas)\b', r'Uso de pronomes pessoais'),  # Pronomes pessoais
            (r'\b(que|qual|quais)\b', r'Possível uso excessivo de pronomes relativos'),  # Pronomes relativos
        ]
        
        issue_count = 0
        for pattern, description in grammar_issues:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            issue_count += matches
        
        # Penalizar baseado no número de issues
        if issue_count > 20:
            score -= 0.3
        elif issue_count > 10:
            score -= 0.2
        elif issue_count > 5:
            score -= 0.1
        
        return max(0.0, score)

    def _assess_legal_quality(self, content: str, state: DocumentState) -> float:
        """Avalia qualidade legal do documento"""
        score = 1.0
        
        # Verificar elementos legais obrigatórios
        legal_elements = {
            "lgpd_mention": r'\b(LGPD|Lei Geral de Proteção de Dados)\b',
            "articles_mentioned": r'\b(Art\.|Artigo)\s+\d+',
            "legal_terms": r'\b(consentimento|dados pessoais|tratamento|titular|controlador|operador)\b',
            "rights_mentioned": r'\b(direito|direitos)\b',
            "obligations_mentioned": r'\b(obrigação|obrigações|dever|responsabilidade)\b',
            "contact_info": r'\b(contato|email|telefone|endereço)\b'
        }
        
        missing_elements = []
        for element, pattern in legal_elements.items():
            if not re.search(pattern, content, re.IGNORECASE):
                missing_elements.append(element)
        
        # Penalizar elementos faltantes
        penalty_per_element = 0.15
        score -= len(missing_elements) * penalty_per_element
        
        # Verificar consistência legal
        if self._check_legal_consistency(content):
            score += 0.1
        
        return max(0.0, score)

    def _assess_structure_quality(self, content: str, state: DocumentState) -> float:
        """Avalia qualidade estrutural do documento"""
        score = 1.0
        
        # Verificar estrutura de seções
        sections = state.get("required_sections", [])
        content_sections = state.get("content_sections", {})
        
        # Verificar se todas as seções obrigatórias estão presentes
        missing_sections = []
        for section in sections:
            if section not in content_sections:
                missing_sections.append(section)
        
        # Penalizar seções faltantes
        penalty_per_section = 0.2
        score -= len(missing_sections) * penalty_per_section
        
        # Verificar hierarquia de títulos
        title_hierarchy = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        if title_hierarchy:
            # Verificar se há progressão lógica (h1 -> h2 -> h3)
            levels = [len(level) for level, _ in title_hierarchy]
            if not self._is_hierarchy_consistent(levels):
                score -= 0.1
        
        # Verificar comprimento das seções
        if self._check_section_lengths(content_sections):
            score -= 0.1
        
        return max(0.0, score)

    def _assess_completeness_quality(self, content: str, state: DocumentState) -> float:
        """Avalia completude do documento"""
        score = 1.0
        
        # Verificar se o documento tem tamanho adequado
        content_length = len(content)
        document_type = state["document_type"].value
        
        min_lengths = {
            "politica_privacidade": 2000,
            "termo_consentimento": 800,
            "clausula_contratual": 1200,
            "ata_comite": 600,
            "codigo_conduta": 1500
        }
        
        min_length = min_lengths.get(document_type, 1000)
        if content_length < min_length:
            score -= 0.3
        
        # Verificar se todas as informações da empresa estão presentes
        company_info = state["company_name"]
        if company_info not in content:
            score -= 0.2
        
        # Verificar se há informações de contato
        if not re.search(r'\b(contato|email|telefone)\b', content, re.IGNORECASE):
            score -= 0.2
        
        # Verificar se há data de vigência
        if not re.search(r'\b(data|vigência|vigente)\b', content, re.IGNORECASE):
            score -= 0.1
        
        return max(0.0, score)

    def _identify_quality_issues(self, content: str, state: DocumentState) -> List[QualityIssue]:
        """Identifica issues específicos de qualidade"""
        issues = []
        
        # Issues gramaticais
        grammar_issues = self._find_grammar_issues(content)
        issues.extend(grammar_issues)
        
        # Issues legais
        legal_issues = self._find_legal_issues(content, state)
        issues.extend(legal_issues)
        
        # Issues estruturais
        structure_issues = self._find_structure_issues(content, state)
        issues.extend(structure_issues)
        
        # Issues de completude
        completeness_issues = self._find_completeness_issues(content, state)
        issues.extend(completeness_issues)
        
        return issues

    def _find_grammar_issues(self, content: str) -> List[QualityIssue]:
        """Encontra issues gramaticais"""
        issues = []
        
        # Verificar capitalização após pontuação
        sentences = re.split(r'[.!?]', content)
        for i, sentence in enumerate(sentences):
            if sentence.strip() and sentence.strip()[0].islower():
                issues.append(QualityIssue(
                    severity="medium",
                    category="grammar",
                    description="Falta capitalização no início da frase",
                    location=f"Sentença {i+1}",
                    suggestion="Capitalizar a primeira letra da frase"
                ))
        
        # Verificar espaços múltiplos
        if re.search(r'\s{2,}', content):
            issues.append(QualityIssue(
                severity="low",
                category="grammar",
                description="Espaços múltiplos encontrados",
                location="Documento",
                suggestion="Remover espaços em excesso"
            ))
        
        return issues

    def _find_legal_issues(self, content: str, state: DocumentState) -> List[QualityIssue]:
        """Encontra issues legais"""
        issues = []
        
        # Verificar se LGPD é mencionada
        if not re.search(r'\b(LGPD|Lei Geral de Proteção de Dados)\b', content, re.IGNORECASE):
            issues.append(QualityIssue(
                severity="high",
                category="legal",
                description="LGPD não mencionada explicitamente",
                location="Documento",
                suggestion="Incluir referência explícita à LGPD"
            ))
        
        # Verificar se há artigos da LGPD mencionados
        articles = re.findall(r'\b(Art\.|Artigo)\s+\d+', content)
        if len(articles) < 3:
            issues.append(QualityIssue(
                severity="medium",
                category="legal",
                description="Poucos artigos da LGPD mencionados",
                location="Documento",
                suggestion="Incluir mais referências aos artigos da LGPD"
            ))
        
        # Verificar se há informações de contato do DPO
        if not re.search(r'\b(DPO|Encarregado|contato)\b', content, re.IGNORECASE):
            issues.append(QualityIssue(
                severity="high",
                category="legal",
                description="Informações do DPO não encontradas",
                location="Documento",
                suggestion="Incluir seção com informações de contato do DPO"
            ))
        
        return issues

    def _find_structure_issues(self, content: str, state: DocumentState) -> List[QualityIssue]:
        """Encontra issues estruturais"""
        issues = []
        
        # Verificar seções obrigatórias
        required_sections = state.get("required_sections", [])
        content_sections = state.get("content_sections", {})
        
        for section in required_sections:
            if section not in content_sections:
                issues.append(QualityIssue(
                    severity="high",
                    category="structure",
                    description=f"Seção obrigatória ausente: {section}",
                    location="Estrutura do documento",
                    suggestion=f"Adicionar seção '{section}'"
                ))
        
        # Verificar hierarquia de títulos
        title_hierarchy = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        if title_hierarchy:
            levels = [len(level) for level, _ in title_hierarchy]
            if not self._is_hierarchy_consistent(levels):
                issues.append(QualityIssue(
                    severity="medium",
                    category="structure",
                    description="Hierarquia de títulos inconsistente",
                    location="Estrutura do documento",
                    suggestion="Revisar e corrigir hierarquia de títulos"
                ))
        
        return issues

    def _find_completeness_issues(self, content: str, state: DocumentState) -> List[QualityIssue]:
        """Encontra issues de completude"""
        issues = []
        
        # Verificar tamanho do documento
        content_length = len(content)
        document_type = state["document_type"].value
        
        min_lengths = {
            "politica_privacidade": 2000,
            "termo_consentimento": 800,
            "clausula_contratual": 1200,
            "ata_comite": 600,
            "codigo_conduta": 1500
        }
        
        min_length = min_lengths.get(document_type, 1000)
        if content_length < min_length:
            issues.append(QualityIssue(
                severity="medium",
                category="completeness",
                description=f"Documento muito curto ({content_length} caracteres)",
                location="Documento",
                suggestion=f"Expandir conteúdo para pelo menos {min_length} caracteres"
            ))
        
        # Verificar informações da empresa
        company_name = state["company_name"]
        if company_name not in content:
            issues.append(QualityIssue(
                severity="high",
                category="completeness",
                description="Nome da empresa não encontrado no documento",
                location="Documento",
                suggestion="Incluir nome da empresa no documento"
            ))
        
        return issues

    def _generate_recommendations(self, issues: List[QualityIssue], overall_score: float) -> List[str]:
        """Gera recomendações baseadas nos issues encontrados"""
        recommendations = []
        
        # Recomendações baseadas no score geral
        if overall_score < 0.7:
            recommendations.append("Revisão completa do documento recomendada")
        elif overall_score < 0.8:
            recommendations.append("Revisão parcial do documento recomendada")
        
        # Recomendações baseadas nos tipos de issues
        critical_issues = [i for i in issues if i.severity == "critical"]
        high_issues = [i for i in issues if i.severity == "high"]
        
        if critical_issues:
            recommendations.append("Corrigir issues críticos antes da aprovação")
        
        if high_issues:
            recommendations.append("Revisar e corrigir issues de alta severidade")
        
        # Recomendações específicas por categoria
        grammar_issues = [i for i in issues if i.category == "grammar"]
        legal_issues = [i for i in issues if i.category == "legal"]
        structure_issues = [i for i in issues if i.category == "structure"]
        
        if grammar_issues:
            recommendations.append("Revisar gramática e ortografia")
        
        if legal_issues:
            recommendations.append("Revisar conformidade legal")
        
        if structure_issues:
            recommendations.append("Revisar estrutura e organização")
        
        return recommendations

    def _create_quality_checklist(self, assessment: QualityAssessment) -> Dict[str, bool]:
        """Cria checklist de qualidade"""
        return {
            "grammar_acceptable": assessment.grammar_score >= 0.8,
            "legal_acceptable": assessment.legal_score >= 0.8,
            "structure_acceptable": assessment.structure_score >= 0.8,
            "completeness_acceptable": assessment.completeness_score >= 0.8,
            "no_critical_issues": len([i for i in assessment.issues if i.severity == "critical"]) == 0,
            "overall_acceptable": assessment.is_acceptable
        }

    def _check_legal_consistency(self, content: str) -> bool:
        """Verifica consistência legal do documento"""
        # Verificar se há contradições legais
        contradictions = [
            (r'\b(obrigatório|obrigatória)\b.*\b(opcional|facultativo)\b', "Contradição entre obrigatório e opcional"),
            (r'\b(sempre|nunca)\b.*\b(às vezes|ocasionalmente)\b', "Contradição temporal"),
            (r'\b(todos|todas)\b.*\b(alguns|algumas)\b', "Contradição quantitativa")
        ]
        
        for pattern, description in contradictions:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        
        return True

    def _is_hierarchy_consistent(self, levels: List[int]) -> bool:
        """Verifica se a hierarquia de títulos é consistente"""
        if not levels:
            return True
        
        # Verificar se há progressão lógica (não pula níveis)
        for i in range(1, len(levels)):
            if levels[i] > levels[i-1] + 1:
                return False
        
        return True

    def _check_section_lengths(self, content_sections: Dict[str, str]) -> bool:
        """Verifica se as seções têm comprimento adequado"""
        for section_name, content in content_sections.items():
            if len(content.strip()) < 50:  # Seção muito curta
                return False
        
        return True
