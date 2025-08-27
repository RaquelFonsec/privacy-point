
"""
Privacy Point - Sistema de Automação LGPD/ANPD
Script principal para execução do sistema
"""

import os
import sys
import time
import signal
import subprocess
import argparse
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    required_packages = [
        "fastapi",
        "streamlit", 
        "langchain",
        "langgraph",
        "openai",
        "pydantic",
        "structlog",
        ("python-multipart", "multipart"),
        ("opencv-python", "cv2"),
        ("pytesseract", "pytesseract"),
        "plotly"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if isinstance(package, tuple):
            package_name, import_name = package
        else:
            package_name = import_name = package
            
        try:
            if import_name == "multipart":
                import multipart
            else:
                __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f" Dependências faltando: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Verifica se as variáveis de ambiente estão configuradas"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f" Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        print("Configure o arquivo .env com as variáveis necessárias")
        return False
    
    return True

def start_api():
    """Inicia a API FastAPI"""
    print(" Iniciando API FastAPI...")
    
    # Verificar se porta está em uso
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        if result == 0:
            print("  Porta 8000 já está em uso. Tentando matar processo...")
            import os
            os.system("pkill -f 'uvicorn.*8000' 2>/dev/null || true")
            os.system("pkill -f 'python.*8000' 2>/dev/null || true")
            time.sleep(3)
    except:
        pass
    
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "src.api.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ])
    
    # Aguardar API estar pronta
    print(" Aguardando API estar pronta...")
    time.sleep(5)
    
    # Verificar se API está rodando
    try:
        import requests
        response = requests.get("http://localhost:8000/api/v1/health", timeout=10)
        if response.status_code == 200:
            print(" API pronta!")
            return api_process
        else:
            print(" API não está respondendo corretamente")
            return api_process  # Retornar processo mesmo assim
    except Exception as e:
        print(f" Erro ao verificar API: {e}")
        print(" Retornando processo da API mesmo assim...")
        return api_process  # Retornar processo mesmo com erro

def start_dashboard():
    """Inicia o dashboard Streamlit"""
    print(" Iniciando Dashboard Streamlit...")
    
    # Verificar se porta está em uso
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8501))
        sock.close()
        if result == 0:
            print("  Porta 8501 já está em uso. Tentando matar processo...")
            import os
            os.system("pkill -f 'streamlit.*8501' 2>/dev/null || true")
            os.system("pkill -f 'python.*8501' 2>/dev/null || true")
            time.sleep(3)
    except:
        pass
    
    dashboard_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", 
        "src/ui/app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])
    
    return dashboard_process

def wait_for_processes(processes):
    """Aguarda os processos em execução"""
    try:
        print(" Aguardando... (Ctrl+C para parar)")
        for process in processes:
            if process:
                process.wait()
    except KeyboardInterrupt:
        print("\n Parando sistema...")
        for process in processes:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        # Limpar processos órfãos
        import os
        os.system("pkill -f 'uvicorn.*8000' 2>/dev/null || true")
        os.system("pkill -f 'streamlit.*8501' 2>/dev/null || true")
        print(" Sistema parado com sucesso")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Privacy Point - Sistema de Automação LGPD/ANPD")
    parser.add_argument("--api-only", action="store_true", help="Executar apenas a API")
    parser.add_argument("--dashboard-only", action="store_true", help="Executar apenas o dashboard")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(" PRIVACY POINT - Sistema de Automação LGPD/ANPD")
    print("=" * 60)
    print(" Recursos disponíveis:")
    print("   • API FastAPI: http://localhost:8000")
    print("   • Dashboard: http://localhost:8501")
    print("   • Documentação API: http://localhost:8000/docs")
    print(" Agentes especializados:")
    print("   • OCR Agent - Processamento de documentos")
    print("   • Classifier Agent - Classificação de contexto")
    print("   • Data Mapping Agent - Mapeamento de fluxo de dados")
    print("   • Research Agent - Pesquisa regulatória")
    print("   • Legal Expert Agent - Assessoria jurídica especializada")
    print("   • Cyber Security Agent - Avaliação de segurança")
    print("   • Structure Agent - Estruturação de conteúdo")
    print("   • Generator Agent - Geração de conteúdo")
    print("   • Quality Agent - Controle de qualidade")
    print("   • Compliance Agent - Validação de conformidade")
    print("   • Human Supervision Agent - Supervisão humana")
    print(" Tipos de documentos suportados:")
    print("   • Política de Privacidade")
    print("   • Termo de Consentimento")
    print("   • Cláusula Contratual")
    print("   • Ata de Comitê")
    print("   • Código de Conduta")
    print("   • Acordo de Tratamento de Dados")
    print("   • Notificação de Violação")
    print("   • Avaliação de Impacto")
    print(" Para parar o sistema, pressione Ctrl+C")
    print("=" * 60)
    
    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar variáveis de ambiente
    if not check_environment():
        sys.exit(1)
    
    processes = []
    
    try:
        if args.api_only:
            # Executar apenas API
            api_process = start_api()
            if api_process:
                processes.append(api_process)
                print(" Sistema iniciado com sucesso!")
                print(" API disponível em: http://localhost:8000")
                print(" Documentação em: http://localhost:8000/docs")
                wait_for_processes(processes)
            else:
                print(" Processo API terminou inesperadamente")
                sys.exit(1)
                
        elif args.dashboard_only:
            # Executar apenas dashboard
            dashboard_process = start_dashboard()
            processes.append(dashboard_process)
            print(" Sistema iniciado com sucesso!")
            print(" Dashboard disponível em: http://localhost:8501")
            wait_for_processes(processes)
            
        else:
            # Executar sistema completo
            api_process = start_api()
            if api_process:
                processes.append(api_process)
                time.sleep(2)
                
                dashboard_process = start_dashboard()
                processes.append(dashboard_process)
                
                print(" Sistema iniciado com sucesso!")
                print(" API disponível em: http://localhost:8000")
                print(" Dashboard disponível em: http://localhost:8501")
                print(" Documentação em: http://localhost:8000/docs")
                
                wait_for_processes(processes)
            else:
                print(" Processo API terminou inesperadamente")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n Sistema interrompido pelo usuário")
    except Exception as e:
        print(f" Erro inesperado: {e}")
        sys.exit(1)
    finally:
        # Garantir que todos os processos sejam terminados
        for process in processes:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

if __name__ == "__main__":
    main()
