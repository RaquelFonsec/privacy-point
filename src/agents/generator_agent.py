"""
Agente Gerador de Conteúdo
Função: Redige o conteúdo técnico especializado
Especialização: Linguagem jurídica para privacy e compliance
"""
from typing import Dict, Any, List
import structlog
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

from src.agents.base_agent import BaseAgent
from src.workflows.state import DocumentState, ProcessingStatus

logger = structlog.get_logger()

class GeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.logger = logger.bind(agent="Generator")
        self.output_parser = StrOutputParser()

    def execute(self, state: DocumentState) -> DocumentState:
        """Gera o conteúdo do documento baseado na estrutura e requisitos"""
        try:
            state["current_status"] = ProcessingStatus.PROCESSING
            state["current_step"] = "Content Generation"
            
            # Gerar conteúdo para cada seção
            content_sections = {}
            legal_clauses = []
            
            structure = state.get("document_structure", {})
            sections = structure.get("sections", [])
            
            for section in sections:
                section_content = self._generate_section_content(section, state)
                content_sections[section["title"]] = section_content
                
                # Extrair cláusulas legais
                if section["content_type"] in ["text", "list"]:
                    clauses = self._extract_legal_clauses(section_content)
                    legal_clauses.extend(clauses)
            
            # Gerar documento completo
            full_content = self._assemble_document(content_sections, structure)
            
            # Atualizar estado
            state["generated_content"] = full_content
            state["content_sections"] = content_sections
            state["legal_clauses"] = legal_clauses
            state["current_status"] = ProcessingStatus.GENERATED
            
            self.log_action(state, f"Conteúdo gerado: {len(full_content)} caracteres, "
                                 f"{len(content_sections)} seções, {len(legal_clauses)} cláusulas")
            
        except Exception as e:
            self.log_action(state, f"Erro na geração: {str(e)}")
            state["error_messages"].append(f"Generation Error: {str(e)}")
            state["current_status"] = ProcessingStatus.ERROR
        
        return state

    def _generate_section_content(self, section: Dict[str, Any], state: DocumentState) -> str:
        """Gera conteúdo para uma seção específica"""
        section_type = section["content_type"]
        
        if section_type == "text":
            return self._generate_text_content(section, state)
        elif section_type == "list":
            return self._generate_list_content(section, state)
        elif section_type == "table":
            return self._generate_table_content(section, state)
        elif section_type == "form":
            return self._generate_form_content(section, state)
        else:
            return section.get("template_content", "")

    def _generate_text_content(self, section: Dict[str, Any], state: DocumentState) -> str:
        """Gera conteúdo textual para uma seção"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um especialista em redação jurídica para documentos LGPD/ANPD.
            
            Gere conteúdo técnico especializado para a seção solicitada, seguindo:
            1. Linguagem jurídica apropriada
            2. Conformidade com LGPD/ANPD
            3. Base legal específica
            4. Tom profissional e claro
            5. Estrutura lógica e coerente
            
            Contexto da empresa: {company_name} - {activity_description}
            Setor: {industry_sector}
            Base legal: {legal_basis}
            
            Seção: {section_title}
            Descrição: {section_description}
            Template base: {template_content}
            """),
            ("human", "Gere o conteúdo para esta seção do documento.")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        content = chain.invoke({
            "company_name": state["company_name"],
            "activity_description": state["activity_description"],
            "industry_sector": state.get("industry_sector", "geral"),
            "legal_basis": ", ".join(section.get("legal_basis", [])),
            "section_title": section["title"],
            "section_description": section["description"],
            "template_content": section.get("template_content", "")
        })
        
        return self._format_text_content(content, section["title"])

    def _generate_list_content(self, section: Dict[str, Any], state: DocumentState) -> str:
        """Gera conteúdo em formato de lista"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um especialista em redação jurídica para documentos LGPD/ANPD.
            
            Gere uma lista estruturada de itens para a seção solicitada.
            Cada item deve ser claro, específico e em conformidade com a LGPD.
            
            Contexto: {company_name} - {activity_description}
            Seção: {section_title}
            Descrição: {section_description}
            Base legal: {legal_basis}
            
            Retorne apenas a lista formatada, sem introdução adicional.
            """),
            ("human", "Gere a lista de itens para esta seção.")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        content = chain.invoke({
            "company_name": state["company_name"],
            "activity_description": state["activity_description"],
            "section_title": section["title"],
            "section_description": section["description"],
            "legal_basis": ", ".join(section.get("legal_basis", []))
        })
        
        return self._format_list_content(content)

    def _generate_table_content(self, section: Dict[str, Any], state: DocumentState) -> str:
        """Gera conteúdo em formato de tabela"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um especialista em redação jurídica para documentos LGPD/ANPD.
            
            Gere uma tabela estruturada para a seção solicitada.
            A tabela deve conter informações organizadas e em conformidade com a LGPD.
            
            Contexto: {company_name} - {activity_description}
            Seção: {section_title}
            Descrição: {section_description}
            
            Retorne a tabela em formato markdown com cabeçalhos apropriados.
            """),
            ("human", "Gere a tabela para esta seção.")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        content = chain.invoke({
            "company_name": state["company_name"],
            "activity_description": state["activity_description"],
            "section_title": section["title"],
            "section_description": section["description"]
        })
        
        return self._format_table_content(content)

    def _generate_form_content(self, section: Dict[str, Any], state: DocumentState) -> str:
        """Gera conteúdo de formulário"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um especialista em redação jurídica para documentos LGPD/ANPD.
            
            Gere um formulário estruturado para a seção solicitada.
            O formulário deve ser claro e em conformidade com a LGPD.
            
            Contexto: {company_name} - {activity_description}
            Seção: {section_title}
            Descrição: {section_description}
            
            Retorne o formulário formatado de forma clara e profissional.
            """),
            ("human", "Gere o formulário para esta seção.")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        content = chain.invoke({
            "company_name": state["company_name"],
            "activity_description": state["activity_description"],
            "section_title": section["title"],
            "section_description": section["description"]
        })
        
        return self._format_form_content(content)

    def _format_text_content(self, content: str, title: str) -> str:
        """Formata conteúdo textual"""
        # Adicionar título da seção
        formatted = f"## {title}\n\n"
        
        # Limpar e formatar o conteúdo
        content = content.strip()
        
        # Garantir que parágrafos estejam bem separados
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        formatted += content + "\n\n"
        
        return formatted

    def _format_list_content(self, content: str) -> str:
        """Formata conteúdo em lista"""
        # Garantir que itens da lista estejam bem formatados
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Se não começa com marcador de lista, adicionar
                if not re.match(r'^[-*•]\s', line) and not re.match(r'^\d+\.\s', line):
                    line = f"• {line}"
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)

    def _format_table_content(self, content: str) -> str:
        """Formata conteúdo de tabela"""
        # Garantir que a tabela esteja em formato markdown correto
        if not content.strip().startswith('|'):
            # Se não está em formato de tabela, criar estrutura básica
            content = "| Campo | Descrição |\n|-------|-----------|\n| Exemplo | Descrição do exemplo |"
        
        return content

    def _format_form_content(self, content: str) -> str:
        """Formata conteúdo de formulário"""
        # Garantir que campos do formulário estejam bem formatados
        content = re.sub(r'\[([^\]]+)\]', r'**[\1]**', content)  # Destacar campos
        return content

    def _extract_legal_clauses(self, content: str) -> List[str]:
        """Extrai cláusulas legais do conteúdo"""
        clauses = []
        
        # Padrões para identificar cláusulas legais
        patterns = [
            r'[A-Z][^.]*?(?:LGPD|Lei Geral de Proteção de Dados)[^.]*?\.',
            r'[A-Z][^.]*?(?:Art\.|Artigo)\s+\d+[^.]*?\.',
            r'[A-Z][^.]*?(?:conforme|nos termos de|de acordo com)[^.]*?\.',
            r'[A-Z][^.]*?(?:obrigatório|obrigatória|deverá|deverá ser)[^.]*?\.',
            r'[A-Z][^.]*?(?:direito|direitos)[^.]*?\.',
            r'[A-Z][^.]*?(?:responsabilidade|responsável)[^.]*?\.'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            clauses.extend(matches)
        
        # Remover duplicatas e limpar
        unique_clauses = list(set(clauses))
        cleaned_clauses = [clause.strip() for clause in unique_clauses if len(clause.strip()) > 20]
        
        return cleaned_clauses[:10]  # Limitar a 10 cláusulas

    def _assemble_document(self, content_sections: Dict[str, str], structure: Dict[str, Any]) -> str:
        """Monta o documento completo"""
        document_parts = []
        
        # Adicionar cabeçalho
        title = structure.get("title", "Documento")
        document_parts.append(f"# {title}\n\n")
        
        # Adicionar seções na ordem correta
        sections = structure.get("sections", [])
        for section in sections:
            section_title = section["title"]
            if section_title in content_sections:
                document_parts.append(content_sections[section_title])
        
        # Adicionar rodapé
        document_parts.append("\n---\n")
        document_parts.append("*Documento gerado automaticamente pelo sistema Privacy Point*\n")
        
        return "".join(document_parts)

    def _apply_company_specific_content(self, content: str, state: DocumentState) -> str:
        """Aplica conteúdo específico da empresa"""
        replacements = {
            "[EMPRESA]": state["company_name"],
            "[ATIVIDADE]": state["activity_description"],
            "[SETOR]": state.get("industry_sector", "geral"),
            "[DATA]": "Data de vigência: " + self._get_current_date()
        }
        
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        return content

    def _get_current_date(self) -> str:
        """Retorna data atual formatada"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y")

    def _validate_legal_compliance(self, content: str, state: DocumentState) -> Dict[str, Any]:
        """Valida conformidade legal do conteúdo gerado"""
        compliance_checks = {
            "lgpd_articles_mentioned": len(re.findall(r'Art\.\s*\d+', content)),
            "legal_terms_present": len(re.findall(r'\b(consentimento|dados pessoais|tratamento|titular)\b', content, re.IGNORECASE)),
            "company_identification": state["company_name"] in content,
            "rights_mentioned": len(re.findall(r'\b(direito|direitos)\b', content, re.IGNORECASE)),
            "contact_info": len(re.findall(r'\b(contato|email|telefone)\b', content, re.IGNORECASE))
        }
        
        total_score = sum(compliance_checks.values())
        max_score = len(compliance_checks) * 2  # Assumindo que cada check pode valer até 2 pontos
        
        return {
            "checks": compliance_checks,
            "score": total_score / max_score if max_score > 0 else 0.0
        }
