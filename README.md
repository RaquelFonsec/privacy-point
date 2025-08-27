# 🔒 Privacy Point

**Sistema Multiagentes para Automação Inteligente de Documentos Regulatórios LGPD/ANPD**

## 📋 Visão Geral

O Privacy Point é uma solução completa de automação inteligente que utiliza Inteligência Artificial Generativa (IA Gen) para acelerar a elaboração de documentos regulatórios LGPD/ANPD. O sistema combina múltiplos agentes especializados com bases jurídicas de referência para produzir documentos de alta qualidade e conformidade.

## 🏗️ Arquitetura

### Framework Principal: LangGraph
- **Orquestração inteligente** de múltiplos agentes especializados
- **Estado compartilhado** entre todos os componentes
- **Fluxos condicionais** que se adaptam ao tipo de documento
- **Supervisão humana obrigatória** integrada no processo

### 11 Agentes Especializados

1. **🔍 OCR Agent** - Processamento Documental
   - Extrai e digitaliza conteúdo de documentos físicos/digitalizados
   - Suporte a múltiplos engines: Tesseract, PaddleOCR, AWS Textract, Azure Document Intelligence
   - Pós-processamento inteligente com correção automática

2. **🏷️ Classifier Agent** - Classificação de Contexto
   - Analisa solicitações e identifica tipo de documento necessário
   - Classificação automática baseada em conteúdo e contexto
   - Determinação de complexidade e urgência

3. **🗺️ Data Mapping Agent** - Mapeamento de Fluxo de Dados
   - Analisa o caminho que os dados pessoais percorrem na organização
   - Identifica pontos de coleta, processamento e descarte
   - Avalia conformidade com princípios da LGPD

4. **📚 Research Agent** - Pesquisa Regulatória
   - Identifica legislação aplicável e fundamentação legal
   - Base de conhecimento LGPD/ANPD e regulamentações correlatas
   - Análise de requisitos específicos por setor

5. **⚖️ Legal Expert Agent** - Assessoria Jurídica Especializada
   - Fornece orientação jurídica especializada em direito digital
   - Interpreta jurisprudência e regulamentações
   - Identifica riscos legais e oportunidades de compliance

6. **🔒 Cyber Security Agent** - Avaliação de Segurança
   - Avalia aspectos de segurança da informação baseado em ISO 27001/27002
   - Identifica vulnerabilidades e riscos de segurança
   - Recomenda medidas de proteção de dados

7. **📐 Structure Agent** - Estruturação de Conteúdo
   - Define estrutura e organização do documento
   - Padrões documentais regulatórios
   - Templates inteligentes baseados em tipo e setor

8. **✍️ Generator Agent** - Geração de Conteúdo
   - Redige conteúdo técnico especializado
   - Linguagem jurídica para privacy e compliance
   - Geração contextualizada por empresa e atividade

9. **✅ Quality Agent** - Controle de Qualidade
   - Revisa consistência, coerência e completude
   - Padrões de qualidade para documentos regulatórios
   - Detecção automática de issues e sugestões de melhoria

10. **⚖️ Compliance Agent** - Validação de Conformidade
    - Valida aderência total às exigências LGPD/ANPD
    - Compliance regulatório específico
    - Análise de risco e gaps de conformidade

11. ** Human Supervision Agent** - Supervisão Humana
    - Interface para revisão e aprovação humana final
    - Facilitação da supervisão obrigatória
    - Sistema de feedback e aprovação

##  Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- Tesseract OCR (opcional)
- OpenAI API Key

### 1. Clone o repositório

```bash
git clone https://github.com/RaquelFonsec/privacy-point.git
cd privacy-point
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Configurações do sistema
DEBUG=True
LOG_LEVEL=INFO

# Serviços de OCR 
TESSERACT_PATH=/usr/bin/tesseract
PADDLE_OCR_ENABLED=False

# AWS Services (opcionais)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
AWS_TEXTRACT_ENABLED=False



# Configurações da API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# Segurança
SECRET_KEY=your_secret_key_here
```

### 5. Instale o Tesseract OCR (opcional)

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
Baixe e instale de: https://github.com/UB-Mannheim/tesseract/wiki

## 🎯 Como Usar

### ⚠️ Importante: Sempre ative o ambiente virtual primeiro!

```bash
# Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### Iniciar o Sistema Completo

```bash
python run.py
```

Isso iniciará:
- **API FastAPI** em http://localhost:8000
- **Dashboard Streamlit** em http://localhost:8501
- **Documentação da API** em http://localhost:8000/docs

### Opções de Execução

```bash
# Executar apenas a API
python run.py --api-only

# Executar apenas o dashboard
python run.py --dashboard-only

# Configurar portas personalizadas
python run.py --port 8080 --dashboard-port 8502
```

### Testar os Agentes

```bash
# Testar a lógica de todos os agentes
python test_agents_logic.py
```

## 📄 Tipos de Documentos Suportados

1. **Política de Privacidade** - Documento principal de conformidade LGPD
2. **Termo de Consentimento** - Consentimento específico para tratamento de dados
3. **Cláusula Contratual** - Cláusulas de proteção de dados em contratos
4. **Ata de Comitê** - Registro de reuniões do comitê de privacidade
5. **Código de Conduta** - Diretrizes éticas e de compliance
6. **Acordo de Tratamento de Dados** - Contratos entre controlador e operador
7. **Notificação de Violação** - Comunicação de incidentes de segurança
8. **Avaliação de Impacto** - DPIA (Data Protection Impact Assessment)

##  API Endpoints

### Gerar Documento
```http
POST /api/v1/documents/generate
Content-Type: application/json

{
  "document_type": "politica_privacidade",
  "company_name": "Minha Empresa Ltda",
  "activity_description": "E-commerce de produtos eletrônicos",
  "industry_sector": "e-commerce",
  "language": "pt-BR",
  "jurisdiction": "BR"
}
```

### Verificar Status
```http
GET /api/v1/documents/{document_id}/status
```

### Obter Conteúdo
```http
GET /api/v1/documents/{document_id}/content
```

### Submeter Revisão
```http
POST /api/v1/documents/{document_id}/review
{
  "decision": "approved",
  "reviewer_name": "João Silva",
  "reviewer_id": "reviewer_001",
  "feedback": "Documento aprovado sem alterações"
}
```

## 📊 Dashboard

O dashboard Streamlit oferece:

- **📈 Métricas em tempo real** de processamento
- **📄 Interface de geração** de documentos
- **📋 Lista de documentos** com filtros
- **📊 Gráficos de performance** por agente
- **⚙️ Configurações** do sistema

## 🔄 Fluxo de Trabalho

1. **Upload/Input** - Documento físico ou solicitação digital
2. **OCR Processing** - Extração e digitalização (se aplicável)
3. **Classification** - Identificação do tipo e contexto
4. **Data Mapping** - Análise do fluxo de dados pessoais
5. **Research** - Pesquisa regulatória aplicável
6. **Legal Expert Review** - Assessoria jurídica especializada
7. **Cyber Security Assessment** - Avaliação de segurança
8. **Structuring** - Definição da estrutura do documento
9. **Generation** - Criação do conteúdo especializado
10. **Quality Control** - Verificação de qualidade
11. **Compliance Validation** - Validação de conformidade
12. **Human Review** - Supervisão e aprovação humana
13. **Delivery** - Entrega do documento final

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
privacy-point/
├── src/
│   ├── agents/              # Agentes especializados
│   │   ├── ocr_agent.py
│   │   ├── classifier_agent.py
│   │   ├── data_mapping_agent.py
│   │   ├── research_agent.py
│   │   ├── legal_expert_agent.py
│   │   ├── cyber_security_agent.py
│   │   ├── structure_agent.py
│   │   ├── generator_agent.py
│   │   ├── quality_agent.py
│   │   ├── compliance_agent.py
│   │   └── human_supervision_agent.py
│   ├── api/                 # API FastAPI
│   │   └── main.py
│   ├── ui/                  # Dashboard Streamlit
│   │   └── app.py
│   ├── workflows/           # Workflows LangGraph
│   │   ├── workflow.py
│   │   └── state.py
│   └── config.py           # Configurações
├── tests/                  # Testes
├── requirements.txt        # Dependências
├── run.py                 # Script principal
└── README.md
```

### Executar Testes

```bash
# Testar a lógica de todos os agentes
python test_agents_logic.py

# Testar o sistema completo
python test_system.py
```



## 📈 Métricas e Performance

O sistema oferece métricas detalhadas:

- **Tempo de processamento** por agente
- **Taxa de sucesso** por tipo de documento
- **Qualidade média** dos documentos gerados
- **Conformidade regulatória** por setor
- **Performance dos agentes** individuais

## 🔧 Solução de Problemas

### Erro de Dependências
```bash
# Se aparecer erro de dependências faltando
pip install -r requirements.txt
```

### Erro "No module named 'dotenv'"
```bash
# Ative o ambiente virtual primeiro
source venv/bin/activate

# Depois instale as dependências
pip install -r requirements.txt

# Ou instale especificamente
pip install python-dotenv
```

### Comandos Completos para Rodar
```bash
# 1. Ative o ambiente virtual
source venv/bin/activate

# 2. Instale dependências 
pip install -r requirements.txt

# 3. Rode o sistema
python run.py
```




