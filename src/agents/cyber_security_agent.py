"""
Cyber Security Agent - Avaliação de segurança da informação
Baseado nos conceitos e boas práticas da ISO 27001 e ISO 27002
"""

import structlog
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from .base_agent import BaseAgent
from src.workflows.state import DocumentState, ProcessingStatus

logger = structlog.get_logger()

class CyberSecurityAgent(BaseAgent):
    """Agente especializado em avaliação de segurança da informação"""
    
    def __init__(self):
        super().__init__()
        self.iso_27001_controls = {
            "A.5": "Políticas de Segurança da Informação",
            "A.6": "Organização da Segurança da Informação",
            "A.7": "Segurança de Recursos Humanos",
            "A.8": "Gestão de Ativos",
            "A.9": "Controle de Acesso",
            "A.10": "Criptografia",
            "A.11": "Segurança Física e Ambiental",
            "A.12": "Segurança Operacional",
            "A.13": "Segurança das Comunicações",
            "A.14": "Aquisição, Desenvolvimento e Manutenção de Sistemas",
            "A.15": "Relações com Fornecedores",
            "A.16": "Gestão de Incidentes de Segurança da Informação",
            "A.17": "Aspectos de Segurança da Informação na Gestão da Continuidade do Negócio",
            "A.18": "Conformidade"
        }
    
    def process(self, state: DocumentState) -> DocumentState:
        """Processa a avaliação de segurança da informação"""
        try:
            logger.info("Iniciando avaliação de segurança da informação", 
                       document_id=state.get("document_id"))
            
            # Extrair informações do contexto
            company_info = state.get("company_info", {})
            activity_description = state.get("activity_description", "")
            industry_sector = state.get("industry_sector", "")
            
            # Realizar avaliação ISO 27001/27002
            iso_assessment = self._assess_iso_27001_compliance(
                company_info, activity_description, industry_sector
            )
            
            # Identificar vulnerabilidades
            vulnerabilities = self._identify_vulnerabilities(
                activity_description, industry_sector
            )
            
            # Avaliar riscos de segurança
            security_risks = self._assess_security_risks(
                iso_assessment, vulnerabilities, industry_sector
            )
            
            # Gerar recomendações de segurança
            security_recommendations = self._generate_security_recommendations(
                iso_assessment, vulnerabilities, security_risks
            )
            
            # Atualizar estado
            state["cyber_security"] = {
                "iso_assessment": iso_assessment,
                "vulnerabilities": vulnerabilities,
                "security_risks": security_risks,
                "security_recommendations": security_recommendations,
                "assessment_timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            
            logger.info("Avaliação de segurança concluída", 
                       document_id=state.get("document_id"))
            
            return state
            
        except Exception as e:
            logger.error("Erro na avaliação de segurança", 
                        error=str(e), document_id=state.get("document_id"))
            state["cyber_security"] = {
                "status": "error",
                "error": str(e),
                "assessment_timestamp": datetime.now().isoformat()
            }
            return state
    
    def _assess_iso_27001_compliance(self, company_info: Dict, 
                                   activity_description: str, 
                                   industry_sector: str) -> Dict[str, Any]:
        """Avalia conformidade com ISO 27001/27002"""
        
        iso_assessment = {
            "overall_score": 0,
            "domains": {},
            "critical_gaps": [],
            "compliance_level": "basic"
        }
        
        # Avaliar cada domínio ISO 27001
        for domain_code, domain_name in self.iso_27001_controls.items():
            domain_assessment = self._assess_domain(
                domain_code, domain_name, activity_description, industry_sector
            )
            iso_assessment["domains"][domain_code] = domain_assessment
        
        # Calcular score geral
        domain_scores = [d.get("score", 0) for d in iso_assessment["domains"].values()]
        if domain_scores:
            iso_assessment["overall_score"] = sum(domain_scores) / len(domain_scores)
        
        # Determinar nível de conformidade
        if iso_assessment["overall_score"] >= 90:
            iso_assessment["compliance_level"] = "excellent"
        elif iso_assessment["overall_score"] >= 75:
            iso_assessment["compliance_level"] = "good"
        elif iso_assessment["overall_score"] >= 60:
            iso_assessment["compliance_level"] = "basic"
        else:
            iso_assessment["compliance_level"] = "poor"
        
        # Identificar gaps críticos
        iso_assessment["critical_gaps"] = self._identify_critical_gaps(
            iso_assessment["domains"]
        )
        
        return iso_assessment
    
    def _assess_domain(self, domain_code: str, domain_name: str, 
                      activity_description: str, industry_sector: str) -> Dict[str, Any]:
        """Avalia um domínio específico da ISO 27001"""
        
        # Scores base por setor e atividade
        base_scores = {
            "A.5": {"tecnologia": 85, "saude": 90, "financeiro": 95, "geral": 70},
            "A.6": {"tecnologia": 80, "saude": 85, "financeiro": 90, "geral": 65},
            "A.7": {"tecnologia": 75, "saude": 80, "financeiro": 85, "geral": 60},
            "A.8": {"tecnologia": 90, "saude": 85, "financeiro": 95, "geral": 75},
            "A.9": {"tecnologia": 85, "saude": 90, "financeiro": 95, "geral": 70},
            "A.10": {"tecnologia": 80, "saude": 85, "financeiro": 90, "geral": 65},
            "A.11": {"tecnologia": 70, "saude": 85, "financeiro": 90, "geral": 60},
            "A.12": {"tecnologia": 85, "saude": 80, "financeiro": 90, "geral": 70},
            "A.13": {"tecnologia": 80, "saude": 85, "financeiro": 90, "geral": 65},
            "A.14": {"tecnologia": 85, "saude": 75, "financeiro": 80, "geral": 70},
            "A.15": {"tecnologia": 75, "saude": 80, "financeiro": 85, "geral": 60},
            "A.16": {"tecnologia": 80, "saude": 85, "financeiro": 90, "geral": 65},
            "A.17": {"tecnologia": 70, "saude": 85, "financeiro": 90, "geral": 55},
            "A.18": {"tecnologia": 75, "saude": 90, "financeiro": 95, "geral": 70}
        }
        
        base_score = base_scores.get(domain_code, {}).get(industry_sector, 60)
        
        # Ajustes baseados na atividade
        if "ROPA" in activity_description:
            if domain_code in ["A.8", "A.18"]:
                base_score += 10  # Melhor gestão de ativos e conformidade
            elif domain_code in ["A.15"]:
                base_score += 5   # Melhor gestão de fornecedores
        
        # Ajustes baseados no setor
        if industry_sector == "saude":
            if domain_code in ["A.9", "A.10", "A.11"]:
                base_score += 5   # Maior foco em segurança para dados de saúde
        
        elif industry_sector == "financeiro":
            if domain_code in ["A.9", "A.10", "A.12"]:
                base_score += 5   # Maior foco em controle de acesso e operações
        
        return {
            "name": domain_name,
            "score": min(100, base_score),
            "status": "compliant" if base_score >= 75 else "needs_improvement",
            "controls": self._get_domain_controls(domain_code),
            "recommendations": self._get_domain_recommendations(domain_code, base_score)
        }
    
    def _identify_vulnerabilities(self, activity_description: str, 
                                industry_sector: str) -> List[Dict]:
        """Identifica vulnerabilidades de segurança"""
        
        vulnerabilities = []
        
        # Vulnerabilidades comuns por setor
        sector_vulnerabilities = {
            "tecnologia": [
                {"type": "API Security", "severity": "high", "description": "APIs expostas sem autenticação adequada"},
                {"type": "Cloud Security", "severity": "medium", "description": "Configurações inadequadas de cloud"},
                {"type": "Code Security", "severity": "medium", "description": "Vulnerabilidades em código-fonte"}
            ],
            "saude": [
                {"type": "Data Encryption", "severity": "critical", "description": "Dados de saúde não criptografados"},
                {"type": "Access Control", "severity": "high", "description": "Controle de acesso inadequado"},
                {"type": "Physical Security", "severity": "medium", "description": "Segurança física insuficiente"}
            ],
            "financeiro": [
                {"type": "Transaction Security", "severity": "critical", "description": "Segurança de transações inadequada"},
                {"type": "Compliance", "severity": "high", "description": "Não conformidade com regulamentações"},
                {"type": "Fraud Detection", "severity": "medium", "description": "Sistema de detecção de fraude insuficiente"}
            ],
            "geral": [
                {"type": "Password Policy", "severity": "medium", "description": "Política de senhas fraca"},
                {"type": "Backup Security", "severity": "medium", "description": "Backups não criptografados"},
                {"type": "Network Security", "severity": "medium", "description": "Segurança de rede inadequada"}
            ]
        }
        
        # Adicionar vulnerabilidades específicas do setor
        if industry_sector in sector_vulnerabilities:
            vulnerabilities.extend(sector_vulnerabilities[industry_sector])
        
        # Vulnerabilidades específicas para ROPA
        if "ROPA" in activity_description:
            vulnerabilities.extend([
                {"type": "Data Inventory", "severity": "high", "description": "Inventário de dados incompleto"},
                {"type": "Data Classification", "severity": "medium", "description": "Classificação de dados inadequada"},
                {"type": "Retention Policy", "severity": "medium", "description": "Política de retenção não implementada"}
            ])
        
        return vulnerabilities
    
    def _assess_security_risks(self, iso_assessment: Dict, vulnerabilities: List[Dict],
                              industry_sector: str) -> Dict[str, Any]:
        """Avalia riscos de segurança"""
        
        risk_assessment = {
            "overall_risk_level": "medium",
            "risk_categories": {},
            "mitigation_strategies": []
        }
        
        # Categorizar riscos
        risk_categories = {
            "data_breach": {"probability": "medium", "impact": "high"},
            "compliance_violation": {"probability": "medium", "impact": "high"},
            "system_compromise": {"probability": "low", "impact": "high"},
            "insider_threat": {"probability": "low", "impact": "medium"},
            "supply_chain": {"probability": "medium", "impact": "medium"}
        }
        
        # Ajustar baseado no setor
        if industry_sector == "saude":
            risk_categories["data_breach"]["impact"] = "critical"
            risk_categories["compliance_violation"]["impact"] = "critical"
        
        elif industry_sector == "financeiro":
            risk_categories["system_compromise"]["impact"] = "critical"
            risk_categories["fraud"] = {"probability": "medium", "impact": "high"}
        
        risk_assessment["risk_categories"] = risk_categories
        
        # Calcular nível de risco geral
        high_impact_risks = sum(1 for risk in risk_categories.values() 
                               if risk["impact"] in ["high", "critical"])
        high_probability_risks = sum(1 for risk in risk_categories.values() 
                                   if risk["probability"] in ["high", "medium"])
        
        if high_impact_risks >= 3 or high_probability_risks >= 4:
            risk_assessment["overall_risk_level"] = "high"
        elif high_impact_risks >= 1 or high_probability_risks >= 2:
            risk_assessment["overall_risk_level"] = "medium"
        else:
            risk_assessment["overall_risk_level"] = "low"
        
        # Estratégias de mitigação
        risk_assessment["mitigation_strategies"] = [
            "Implementar controles de acesso robustos",
            "Criptografar dados sensíveis",
            "Estabelecer monitoramento contínuo",
            "Realizar treinamentos de segurança",
            "Implementar resposta a incidentes"
        ]
        
        return risk_assessment
    
    def _generate_security_recommendations(self, iso_assessment: Dict, 
                                         vulnerabilities: List[Dict],
                                         security_risks: Dict) -> List[Dict]:
        """Gera recomendações de segurança"""
        
        recommendations = []
        
        # Recomendações baseadas na avaliação ISO
        if iso_assessment["overall_score"] < 75:
            recommendations.append({
                "priority": "high",
                "category": "ISO Compliance",
                "recommendation": "Implementar controles ISO 27001 prioritários",
                "timeline": "3-6 meses"
            })
        
        # Recomendações baseadas em vulnerabilidades críticas
        critical_vulnerabilities = [v for v in vulnerabilities if v["severity"] == "critical"]
        for vuln in critical_vulnerabilities:
            recommendations.append({
                "priority": "critical",
                "category": "Vulnerability Management",
                "recommendation": f"Remediar vulnerabilidade: {vuln['type']}",
                "timeline": "1-3 meses"
            })
        
        # Recomendações baseadas no nível de risco
        if security_risks["overall_risk_level"] == "high":
            recommendations.append({
                "priority": "high",
                "category": "Risk Management",
                "recommendation": "Implementar programa de gestão de riscos",
                "timeline": "6-12 meses"
            })
        
        # Recomendações específicas por domínio ISO
        for domain_code, domain_assessment in iso_assessment["domains"].items():
            if domain_assessment["score"] < 70:
                recommendations.append({
                    "priority": "medium",
                    "category": f"ISO {domain_code}",
                    "recommendation": f"Melhorar controles em {domain_assessment['name']}",
                    "timeline": "3-6 meses"
                })
        
        return recommendations
    
    def _identify_critical_gaps(self, domains: Dict) -> List[str]:
        """Identifica gaps críticos na conformidade ISO"""
        
        critical_gaps = []
        
        critical_domains = ["A.9", "A.10", "A.12", "A.18"]  # Domínios críticos
        
        for domain_code in critical_domains:
            if domain_code in domains:
                domain = domains[domain_code]
                if domain["score"] < 70:
                    critical_gaps.append(f"Gap crítico em {domain['name']} (Score: {domain['score']})")
        
        return critical_gaps
    
    def _get_domain_controls(self, domain_code: str) -> List[str]:
        """Retorna controles específicos de um domínio"""
        
        controls_map = {
            "A.5": ["Política de Segurança", "Revisão de Políticas"],
            "A.6": ["Funções de Segurança", "Contatos com Autoridades"],
            "A.9": ["Controle de Acesso", "Gestão de Acesso", "Política de Senhas"],
            "A.10": ["Controles de Criptografia", "Gestão de Chaves"],
            "A.12": ["Procedimentos Operacionais", "Gestão de Mudanças"],
            "A.18": ["Conformidade Legal", "Revisão de Segurança"]
        }
        
        return controls_map.get(domain_code, ["Controles Básicos"])
    
    def _get_domain_recommendations(self, domain_code: str, score: int) -> List[str]:
        """Retorna recomendações específicas para um domínio"""
        
        if score >= 80:
            return ["Manter controles atuais", "Considerar melhorias incrementais"]
        elif score >= 60:
            return ["Implementar controles básicos", "Estabelecer processos"]
        else:
            return ["Implementar controles críticos", "Priorizar segurança", "Buscar consultoria especializada"]
