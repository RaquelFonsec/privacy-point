"""
Agente de Estruturação de Conteúdo
Função: Define estrutura e organização do documento
Especialização: Padrões documentais regulatórios
"""
from typing import Dict, Any, List
import structlog
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

from src.agents.base_agent import BaseAgent
from src.workflows.state import DocumentState, ProcessingStatus

logger = structlog.get_logger()

class DocumentSection(BaseModel):
    title: str
    content_type: str  # text, table, list, form
    required: bool
    order: int
    description: str
    legal_basis: List[str]
    template_content: str

class DocumentStructure(BaseModel):
    title: str
    sections: List[DocumentSection]
    total_pages: int
    complexity_level: str
    reading_time: str
    compliance_score: float

class StructureAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.logger = logger.bind(agent="Structure")
        self.output_parser = JsonOutputParser(pydantic_object=DocumentStructure)

    def execute(self, state: DocumentState) -> DocumentState:
        """Define a estrutura do documento baseada no tipo e requisitos"""
        try:
            state["current_status"] = ProcessingStatus.PROCESSING
            state["current_step"] = "Content Structuring"
            
            # Criar estrutura do documento
            structure = self._create_document_structure(state)
            
            # Atualizar estado
            state["document_structure"] = structure.dict()
            state["content_outline"] = self._generate_outline(structure)
            state["current_status"] = ProcessingStatus.STRUCTURED
            
            self.log_action(state, f"Estrutura criada: {len(structure.sections)} seções, "
                                 f"{structure.total_pages} páginas estimadas")
            
        except Exception as e:
            self.log_action(state, f"Erro na estruturação: {str(e)}")
            state["error_messages"].append(f"Structure Error: {str(e)}")
            state["current_status"] = ProcessingStatus.ERROR
        
        return state

    def _create_document_structure(self, state: DocumentState) -> DocumentStructure:
        """Cria estrutura do documento baseada no tipo e requisitos"""
        document_type = state["document_type"].value
        
        # Obter seções base para o tipo de documento
        base_sections = self._get_base_sections(document_type)
        
        # Adicionar seções específicas baseadas na pesquisa regulatória
        regulatory_sections = self._add_regulatory_sections(state)
        
        # Combinar e ordenar seções
        all_sections = base_sections + regulatory_sections
        all_sections.sort(key=lambda x: x.order)
        
        # Calcular metadados
        total_pages = self._estimate_pages(all_sections)
        complexity_level = self._assess_complexity(all_sections)
        reading_time = self._estimate_reading_time(total_pages)
        compliance_score = self._calculate_compliance_score(all_sections, state)
        
        return DocumentStructure(
            title=self._generate_title(document_type, state["company_name"]),
            sections=all_sections,
            total_pages=total_pages,
            complexity_level=complexity_level,
            reading_time=reading_time,
            compliance_score=compliance_score
        )

    def _get_base_sections(self, document_type: str) -> List[DocumentSection]:
        """Retorna seções base para cada tipo de documento"""
        if document_type == "politica_privacidade":
            return [
                DocumentSection(
                    title="Cabeçalho e Identificação",
                    content_type="text",
                    required=True,
                    order=1,
                    description="Identificação da empresa e documento",
                    legal_basis=["LGPD Art. 13º"],
                    template_content="POLÍTICA DE PRIVACIDADE\n\n[EMPRESA]\n\nData de vigência: [DATA]"
                ),
                DocumentSection(
                    title="Objetivo e Escopo",
                    content_type="text",
                    required=True,
                    order=2,
                    description="Objetivo e escopo da política",
                    legal_basis=["LGPD Art. 5º"],
                    template_content="Esta Política de Privacidade tem por objetivo..."
                ),
                DocumentSection(
                    title="Base Legal",
                    content_type="list",
                    required=True,
                    order=3,
                    description="Fundamentação legal para tratamento",
                    legal_basis=["LGPD Art. 6º", "LGPD Art. 7º"],
                    template_content="O tratamento de dados pessoais fundamenta-se em:"
                ),
                DocumentSection(
                    title="Tipos de Dados Coletados",
                    content_type="table",
                    required=True,
                    order=4,
                    description="Categorias de dados pessoais coletados",
                    legal_basis=["LGPD Art. 13º"],
                    template_content="| Categoria | Finalidade | Base Legal |"
                ),
                DocumentSection(
                    title="Finalidade do Tratamento",
                    content_type="text",
                    required=True,
                    order=5,
                    description="Finalidades específicas do tratamento",
                    legal_basis=["LGPD Art. 6º"],
                    template_content="Os dados pessoais são tratados para as seguintes finalidades:"
                ),
                DocumentSection(
                    title="Compartilhamento de Dados",
                    content_type="text",
                    required=True,
                    order=6,
                    description="Compartilhamento com terceiros",
                    legal_basis=["LGPD Art. 18º"],
                    template_content="Os dados pessoais podem ser compartilhados com:"
                ),
                DocumentSection(
                    title="Direitos do Titular",
                    content_type="list",
                    required=True,
                    order=7,
                    description="Direitos garantidos pela LGPD",
                    legal_basis=["LGPD Art. 12º"],
                    template_content="O titular dos dados possui os seguintes direitos:"
                ),
                DocumentSection(
                    title="Segurança dos Dados",
                    content_type="text",
                    required=True,
                    order=8,
                    description="Medidas de segurança implementadas",
                    legal_basis=["LGPD Art. 46º"],
                    template_content="Implementamos medidas técnicas e organizacionais..."
                ),
                DocumentSection(
                    title="Retenção de Dados",
                    content_type="text",
                    required=True,
                    order=9,
                    description="Prazo de retenção dos dados",
                    legal_basis=["LGPD Art. 15º"],
                    template_content="Os dados pessoais são mantidos pelo período necessário..."
                ),
                DocumentSection(
                    title="Contato do DPO",
                    content_type="form",
                    required=True,
                    order=10,
                    description="Informações de contato do DPO",
                    legal_basis=["LGPD Art. 41º"],
                    template_content="Para exercer seus direitos, entre em contato:"
                )
            ]
        
        elif document_type == "termo_consentimento":
            return [
                DocumentSection(
                    title="Identificação da Empresa",
                    content_type="text",
                    required=True,
                    order=1,
                    description="Identificação clara da empresa",
                    legal_basis=["LGPD Art. 7º"],
                    template_content="[EMPRESA], pessoa jurídica de direito privado..."
                ),
                DocumentSection(
                    title="Finalidade do Consentimento",
                    content_type="text",
                    required=True,
                    order=2,
                    description="Finalidade específica do consentimento",
                    legal_basis=["LGPD Art. 7º"],
                    template_content="Solicitamos seu consentimento para:"
                ),
                DocumentSection(
                    title="Tipos de Dados",
                    content_type="list",
                    required=True,
                    order=3,
                    description="Dados que serão coletados",
                    legal_basis=["LGPD Art. 13º"],
                    template_content="Os seguintes dados pessoais serão coletados:"
                ),
                DocumentSection(
                    title="Base Legal",
                    content_type="text",
                    required=True,
                    order=4,
                    description="Fundamentação legal",
                    legal_basis=["LGPD Art. 6º"],
                    template_content="O tratamento fundamenta-se no consentimento..."
                ),
                DocumentSection(
                    title="Direitos do Titular",
                    content_type="list",
                    required=True,
                    order=5,
                    description="Direitos garantidos",
                    legal_basis=["LGPD Art. 12º"],
                    template_content="Você possui os seguintes direitos:"
                ),
                DocumentSection(
                    title="Revogação do Consentimento",
                    content_type="text",
                    required=True,
                    order=6,
                    description="Como revogar o consentimento",
                    legal_basis=["LGPD Art. 19º"],
                    template_content="Você pode revogar este consentimento a qualquer momento..."
                ),
                DocumentSection(
                    title="Aceite Expresso",
                    content_type="form",
                    required=True,
                    order=7,
                    description="Formulário de aceite",
                    legal_basis=["LGPD Art. 7º"],
                    template_content="[ ] Concordo com o tratamento dos dados pessoais"
                )
            ]
        
        # Estrutura padrão para outros tipos
        return [
            DocumentSection(
                title="Cabeçalho",
                content_type="text",
                required=True,
                order=1,
                description="Cabeçalho do documento",
                legal_basis=["LGPD Art. 5º"],
                template_content="[TÍTULO DO DOCUMENTO]\n\n[EMPRESA]"
            ),
            DocumentSection(
                title="Conteúdo Principal",
                content_type="text",
                required=True,
                order=2,
                description="Conteúdo principal do documento",
                legal_basis=["LGPD Art. 6º"],
                template_content="[Conteúdo específico do documento]"
            )
        ]

    def _add_regulatory_sections(self, state: DocumentState) -> List[DocumentSection]:
        """Adiciona seções específicas baseadas na pesquisa regulatória"""
        additional_sections = []
        
        # Adicionar seções baseadas em leis aplicáveis
        for law in state.get("applicable_laws", []):
            if "Marco Civil" in law:
                additional_sections.append(
                    DocumentSection(
                        title="Disposições do Marco Civil da Internet",
                        content_type="text",
                        required=True,
                        order=999,  # Alta prioridade
                        description="Conformidade com Marco Civil da Internet",
                        legal_basis=["Lei nº 12.965/2014"],
                        template_content="Este documento está em conformidade com o Marco Civil da Internet..."
                    )
                )
        
        # Adicionar seções baseadas no setor
        industry_sector = state.get("industry_sector", "")
        if industry_sector.lower() == "saúde":
            additional_sections.append(
                DocumentSection(
                    title="Disposições Específicas para Saúde",
                    content_type="text",
                    required=True,
                    order=998,
                    description="Conformidade com regulamentações de saúde",
                    legal_basis=["Resolução CFM nº 2.217/2018"],
                    template_content="Considerando as especificidades do setor de saúde..."
                )
            )
        
        return additional_sections

    def _generate_title(self, document_type: str, company_name: str) -> str:
        """Gera título apropriado para o documento"""
        titles = {
            "politica_privacidade": f"Política de Privacidade - {company_name}",
            "termo_consentimento": f"Termo de Consentimento - {company_name}",
            "clausula_contratual": f"Cláusula de Proteção de Dados - {company_name}",
            "ata_comite": f"Ata do Comitê de Privacidade - {company_name}",
            "codigo_conduta": f"Código de Conduta - {company_name}"
        }
        
        return titles.get(document_type, f"Documento - {company_name}")

    def _generate_outline(self, structure: DocumentStructure) -> str:
        """Gera outline textual da estrutura"""
        outline = f"# {structure.title}\n\n"
        
        for section in structure.sections:
            outline += f"## {section.order}. {section.title}\n"
            outline += f"**Tipo:** {section.content_type}\n"
            outline += f"**Obrigatório:** {'Sim' if section.required else 'Não'}\n"
            outline += f"**Descrição:** {section.description}\n"
            outline += f"**Base Legal:** {', '.join(section.legal_basis)}\n\n"
        
        return outline

    def _estimate_pages(self, sections: List[DocumentSection]) -> int:
        """Estima número de páginas baseado nas seções"""
        base_pages = len(sections) * 0.3  # Média de 0.3 páginas por seção
        
        # Ajustar baseado no tipo de conteúdo
        for section in sections:
            if section.content_type == "table":
                base_pages += 0.2
            elif section.content_type == "form":
                base_pages += 0.1
        
        return max(1, int(base_pages))

    def _assess_complexity(self, sections: List[DocumentSection]) -> str:
        """Avalia complexidade baseada no número e tipo de seções"""
        total_sections = len(sections)
        required_sections = sum(1 for s in sections if s.required)
        
        if total_sections > 10 or required_sections > 8:
            return "high"
        elif total_sections > 6 or required_sections > 5:
            return "medium"
        else:
            return "low"

    def _estimate_reading_time(self, pages: int) -> str:
        """Estima tempo de leitura"""
        minutes = pages * 2  # 2 minutos por página
        
        if minutes < 60:
            return f"{minutes} minutos"
        else:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            return f"{hours}h {remaining_minutes}min"

    def _calculate_compliance_score(self, sections: List[DocumentSection], state: DocumentState) -> float:
        """Calcula score de conformidade baseado nas seções e requisitos"""
        required_sections = [s for s in sections if s.required]
        regulatory_requirements = state.get("regulatory_requirements", [])
        
        # Score base: 70% se todas as seções obrigatórias estão presentes
        base_score = 0.7 if required_sections else 0.0
        
        # Bônus por requisitos regulatórios atendidos
        regulatory_bonus = min(0.3, len(regulatory_requirements) * 0.05)
        
        return min(1.0, base_score + regulatory_bonus)
