"""
Dashboard Streamlit para o sistema Privacy Point
"""
import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Privacy Point - Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações
API_BASE_URL = "http://localhost:8000/api/v1"

def main():
    """Função principal do dashboard"""
    
    # Sidebar
    st.sidebar.title("Privacy Point")
    st.sidebar.markdown("Sistema de Automação LGPD/ANPD")
    
    # Menu de navegação
    page = st.sidebar.selectbox(
        "Navegação",
        ["Dashboard", "Gerar Documento", "Documentos", "Métricas", "Configurações"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Gerar Documento":
        show_document_generator()
    elif page == "Documentos":
        show_documents_list()
    elif page == "Métricas":
        show_metrics()
    elif page == "Configurações":
        show_settings()

def show_dashboard():
    """Página principal do dashboard"""
    st.title("Dashboard - Privacy Point")
    
    # Verificar saúde da API
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.success("API conectada e funcionando")
        else:
            st.warning("API não está respondendo - Modo Demo")
    except Exception as e:
        st.warning("API não disponível - Modo Demo")
        st.info("Algumas funcionalidades podem estar limitadas")
    
    # Métricas rápidas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Documentos Processados", "0", "0%")
    
    with col2:
        st.metric("Taxa de Sucesso", "0%", "0%")
    
    with col3:
        st.metric("Tempo Médio", "0 min", "0%")
    
    with col4:
        st.metric("Documentos Ativos", "0", "0%")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Documentos por Tipo")
        # Dados simulados
        data = {
            "Tipo": ["Política de Privacidade", "Termo de Consentimento", "Cláusula Contratual"],
            "Quantidade": [5, 3, 2]
        }
        df = pd.DataFrame(data)
        fig = px.bar(df, x="Tipo", y="Quantidade", color="Quantidade")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Qualidade vs Conformidade")
        # Dados simulados
        data = {
            "Documento": ["Doc 1", "Doc 2", "Doc 3", "Doc 4"],
            "Qualidade": [0.85, 0.92, 0.78, 0.88],
            "Conformidade": [0.90, 0.85, 0.82, 0.95]
        }
        df = pd.DataFrame(data)
        fig = px.scatter(df, x="Qualidade", y="Conformidade", text="Documento")
        st.plotly_chart(fig, use_container_width=True)
    
    # Documentos recentes
    st.subheader("Documentos Recentes")
    
    # Dados simulados
    recent_docs = [
        {
            "ID": "doc-001",
            "Tipo": "Política de Privacidade",
            "Empresa": "TechCorp Ltda",
            "Status": "Aprovado",
            "Qualidade": "85%",
            "Conformidade": "90%",
            "Data": "2024-01-15 14:30"
        },
        {
            "ID": "doc-002", 
            "Tipo": "Termo de Consentimento",
            "Empresa": "HealthClinic",
            "Status": "Em Revisão",
            "Qualidade": "78%",
            "Conformidade": "82%",
            "Data": "2024-01-15 13:45"
        }
    ]
    
    df_recent = pd.DataFrame(recent_docs)
    st.dataframe(df_recent, use_container_width=True)

def show_document_generator():
    """Página para gerar novos documentos"""
    st.title("Gerar Novo Documento")
    
    # Formulário de geração
    with st.form("document_generator"):
        st.subheader("Informações Básicas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            document_type = st.selectbox(
                "Tipo de Documento",
                [
                    "politica_privacidade",
                    "termo_consentimento", 
                    "clausula_contratual",
                    "ata_comite",
                    "codigo_conduta",
                    "acordo_tratamento_dados",
                    "notificacao_violacao",
                    "avaliacao_impacto"
                ],
                format_func=lambda x: {
                    "politica_privacidade": "Política de Privacidade",
                    "termo_consentimento": "Termo de Consentimento",
                    "clausula_contratual": "Cláusula Contratual",
                    "ata_comite": "Ata de Comitê",
                    "codigo_conduta": "Código de Conduta",
                    "acordo_tratamento_dados": "Acordo de Tratamento de Dados",
                    "notificacao_violacao": "Notificação de Violação",
                    "avaliacao_impacto": "Avaliação de Impacto"
                }[x]
            )
            
            company_name = st.text_input("Nome da Empresa")
            activity_description = st.text_area("Descrição da Atividade")
        
        with col2:
            industry_sector = st.selectbox(
                "Setor",
                ["geral", "saúde", "financeiro", "e-commerce", "educação", "tecnologia"]
            )
            
            language = st.selectbox("Idioma", ["pt-BR", "en-US", "es-ES"])
            jurisdiction = st.selectbox("Jurisdição", ["BR", "US", "EU"])
        
        st.subheader("Configurações Avançadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            quality_threshold = st.slider("Limite de Qualidade", 0.0, 1.0, 0.8, 0.05)
            compliance_level = st.selectbox("Nível de Conformidade", ["basic", "standard", "strict"])
        
        with col2:
            webhook_url = st.text_input("URL do Webhook (opcional)")
            external_system_id = st.text_input("ID do Sistema Externo (opcional)")
        
        # Upload de arquivo
        st.subheader("Upload de Documento (Opcional)")
        uploaded_file = st.file_uploader(
            "Carregar documento para processamento OCR",
            type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp"]
        )
        
        # Botão de submissão
        submitted = st.form_submit_button("🚀 Gerar Documento")
        
        if submitted:
            if not company_name or not activity_description:
                st.error("Por favor, preencha todos os campos obrigatórios")
                return
            
            # Preparar dados
            request_data = {
                "document_type": document_type,
                "company_name": company_name,
                "activity_description": activity_description,
                "industry_sector": industry_sector,
                "language": language,
                "jurisdiction": jurisdiction,
                "custom_requirements": {
                    "quality_threshold": quality_threshold,
                    "compliance_level": compliance_level
                },
                "webhook_url": webhook_url if webhook_url else None,
                "external_system_id": external_system_id if external_system_id else None
            }
            
            # Enviar requisição
            try:
                files = {}
                if uploaded_file:
                    files = {"file": uploaded_file}
                
                response = requests.post(
                    f"{API_BASE_URL}/documents/generate",
                    data={"request": json.dumps(request_data)},
                    files=files
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Documento iniciado com sucesso!")
                    st.info(f"ID do Documento: {result['document_id']}")
                    st.info(f"Tempo estimado: {result['estimated_completion_time']} minutos")
                    
                    # Mostrar progresso
                    show_document_progress(result['document_id'])
                else:
                    st.error(f"Erro ao gerar documento: {response.text}")
                    
            except Exception as e:
                st.error(f"Erro de conexão: {str(e)}")

def show_document_progress(document_id: str):
    """Mostra progresso de um documento específico"""
    st.subheader(f"Progresso - {document_id}")
    
    # Simular progresso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        time.sleep(0.1)
        progress_bar.progress(i + 1)
        status_text.text(f"Processando... {i + 1}%")
    
    status_text.text("Concluído!")

def show_documents_list():
    """Lista todos os documentos"""
    st.title("Lista de Documentos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["Todos", "Processando", "Aprovado", "Rejeitado", "Em Revisão"]
        )
    
    with col2:
        type_filter = st.selectbox(
            "Tipo",
            ["Todos", "Política de Privacidade", "Termo de Consentimento", "Cláusula Contratual"]
        )
    
    with col3:
        date_filter = st.date_input("Data")
    
    # Dados simulados
    documents = [
        {
            "ID": "doc-001",
            "Tipo": "Política de Privacidade",
            "Empresa": "TechCorp Ltda",
            "Status": "Aprovado",
            "Qualidade": "85%",
            "Conformidade": "90%",
            "Data": "2024-01-15 14:30",
            "Tempo": "12 min"
        },
        {
            "ID": "doc-002",
            "Tipo": "Termo de Consentimento", 
            "Empresa": "HealthClinic",
            "Status": "Em Revisão",
            "Qualidade": "78%",
            "Conformidade": "82%",
            "Data": "2024-01-15 13:45",
            "Tempo": "8 min"
        },
        {
            "ID": "doc-003",
            "Tipo": "Cláusula Contratual",
            "Empresa": "FinanceBank",
            "Status": "Processando",
            "Qualidade": "-",
            "Conformidade": "-", 
            "Data": "2024-01-15 15:20",
            "Tempo": "5 min"
        }
    ]
    
    # Filtrar dados
    if status_filter != "Todos":
        documents = [d for d in documents if d["Status"] == status_filter]
    
    if type_filter != "Todos":
        documents = [d for d in documents if d["Tipo"] == type_filter]
    
    # Mostrar tabela
    df = pd.DataFrame(documents)
    st.dataframe(df, use_container_width=True)
    
    # Ações em lote
    st.subheader("Ações")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Exportar Lista"):
            st.success("Lista exportada com sucesso!")
    
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    with col3:
        if st.button("Limpar Filtros"):
            st.rerun()

def show_metrics():
    """Página de métricas detalhadas"""
    st.title("Métricas Detalhadas")
    
    # Métricas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Documentos", "156", "+12%")
    
    with col2:
        st.metric("Taxa de Aprovação", "87%", "+3%")
    
    with col3:
        st.metric("Tempo Médio", "14.2 min", "-2.1 min")
    
    with col4:
        st.metric("Satisfação", "4.8/5", "+0.2")
    
    # Gráficos detalhados
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Volume por Período")
        # Dados simulados
        dates = pd.date_range(start="2024-01-01", end="2024-01-15", freq="D")
        volumes = [5, 8, 12, 6, 9, 15, 11, 7, 13, 10, 8, 14, 9, 12, 11]
        
        df_volume = pd.DataFrame({
            "Data": dates,
            "Documentos": volumes
        })
        
        fig = px.line(df_volume, x="Data", y="Documentos")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Performance por Agente")
        # Dados simulados
        agents = ["OCR", "Classificador", "Pesquisa", "Estruturação", "Geração", "Qualidade", "Conformidade"]
        performance = [95, 88, 92, 85, 90, 87, 93]
        
        df_perf = pd.DataFrame({
            "Agente": agents,
            "Performance": performance
        })
        
        fig = px.bar(df_perf, x="Agente", y="Performance", color="Performance")
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de performance
    st.subheader("Performance Detalhada")
    
    performance_data = [
        {
            "Agente": "OCR Agent",
            "Documentos Processados": 156,
            "Taxa de Sucesso": "95%",
            "Tempo Médio": "2.3s",
            "Erros": 8
        },
        {
            "Agente": "Classifier Agent",
            "Documentos Processados": 156,
            "Taxa de Sucesso": "88%",
            "Tempo Médio": "1.8s",
            "Erros": 19
        },
        {
            "Agente": "Research Agent",
            "Documentos Processados": 156,
            "Taxa de Sucesso": "92%",
            "Tempo Médio": "3.2s",
            "Erros": 12
        },
        {
            "Agente": "Structure Agent",
            "Documentos Processados": 156,
            "Taxa de Sucesso": "85%",
            "Tempo Médio": "2.1s",
            "Erros": 23
        },
        {
            "Agente": "Generator Agent",
            "Documentos Processados": 156,
            "Taxa de Sucesso": "90%",
            "Tempo Médio": "8.5s",
            "Erros": 16
        },
        {
            "Agente": "Quality Agent",
            "Documentos Processados": 156,
            "Taxa de Sucesso": "87%",
            "Tempo Médio": "4.2s",
            "Erros": 20
        },
        {
            "Agente": "Compliance Agent",
            "Documentos Processados": 156,
            "Taxa de Sucesso": "93%",
            "Tempo Médio": "3.8s",
            "Erros": 11
        }
    ]
    
    df_perf_detailed = pd.DataFrame(performance_data)
    st.dataframe(df_perf_detailed, use_container_width=True)

def show_settings():
    """Página de configurações"""
    st.title("Configurações")
    
    # Configurações da API
    st.subheader("🔗 Configurações da API")
    
    api_url = st.text_input("URL da API", value=API_BASE_URL)
    
    if st.button("Testar Conexão"):
        try:
            response = requests.get(f"{api_url}/health")
            if response.status_code == 200:
                st.success("Conexão bem-sucedida!")
            else:
                st.error("Falha na conexão")
        except Exception:
            st.error("Erro de conexão")
    
    # Configurações do sistema
    st.subheader("⚙️ Configurações do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_file_size = st.number_input("Tamanho máximo de arquivo (MB)", value=10, min_value=1, max_value=100)
        quality_threshold = st.slider("Limite de qualidade padrão", 0.0, 1.0, 0.8, 0.05)
    
    with col2:
        max_revision_attempts = st.number_input("Tentativas máximas de revisão", value=3, min_value=1, max_value=10)
        compliance_level = st.selectbox("Nível de conformidade padrão", ["basic", "standard", "strict"])
    
    # Configurações de notificação
    st.subheader("🔔 Configurações de Notificação")
    
    enable_webhooks = st.checkbox("Habilitar webhooks")
    webhook_url = st.text_input("URL do webhook padrão")
    
    enable_email = st.checkbox("Habilitar notificações por email")
    email_address = st.text_input("Email para notificações")
    
    # Salvar configurações
    if st.button("💾 Salvar Configurações"):
        st.success("Configurações salvas com sucesso!")

if __name__ == "__main__":
    main()