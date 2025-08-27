from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.config import config
from src.workflows.state import DocumentState

class BaseAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model="gpt-4",
            temperature=0.1
        )
    
    def log_action(self, state: DocumentState, message: str):
        if "processing_log" not in state:
            state["processing_log"] = []
        state["processing_log"].append(f"{self.__class__.__name__}: {message}")

class DocumentGeneratorAgent(BaseAgent):
    def execute(self, state: DocumentState) -> DocumentState:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um especialista em documentos LGPD/ANPD.
            Crie uma {document_type} para a empresa {company_name} 
            que atua em: {activity_description}
            
            Mantenha conformidade total com LGPD e use linguagem jurídica apropriada."""),
            ("human", "Gere o documento solicitado.")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "document_type": state["document_type"],
                "company_name": state["company_name"], 
                "activity_description": state["activity_description"]
            })
            
            state["generated_content"] = response.content
            state["quality_score"] = 0.85
            state["is_complete"] = True
            self.log_action(state, "Documento gerado com sucesso")
            
        except Exception as e:
            self.log_action(state, f"Erro: {str(e)}")
            state["is_complete"] = False
        
        return state
