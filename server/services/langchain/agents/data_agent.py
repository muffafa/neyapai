from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from server.services.data_loader import DataLoader
from typing import Tuple, List
import os
import logging

logger = logging.getLogger(__name__)

class DataAnalysisAgent:
    def __init__(self):
        self.data_loader = DataLoader()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY bulunamadı.")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=api_key,
            temperature=0,
            convert_system_message_to_human=True
        )
        self._create_agents()

    def _create_agents(self):
        """Create separate agents for each dataframe"""
        agent_kwargs = {
            "prefix": """Sen eğitim verilerini analiz eden bir uzman veri analistisin.
            Veriyi analiz ederken şu adımları takip et:
            1. Önce ne yapmak istediğini düşün
            2. Gerekli Python kodunu yaz ve çalıştır
            3. Sonuçları detaylı olarak analiz et ve sayısal değerleri mutlaka belirt
            4. Türkçe ve anlaşılır bir yanıt ver
            
            İhtiyaç verilerini analiz ederken:
            - 'branş' sütunu branşı gösterir
            - 'ihtiyac' sütunu o branştaki öğretmen ihtiyacını gösterir
            - Toplam ihtiyacı bulmak için ihtiyac sütununu grupla ve topla
            - En az ilk 5 sonucu göster
            - Sonuçları büyükten küçüğe sırala
            
            Norm fazlası verilerini analiz ederken:
            - 'Branşı' sütunu branşı gösterir
            - 'İlçe Adı' sütunu ilçeyi gösterir
            - Her satır bir öğretmeni temsil eder
            - Sayıları gruplarken count() kullan
            - En az ilk 5 sonucu göster
            
            Yanıtını şu formatta ver:
            Thought: <analiz planın>
            Action: python_repl_ast
            Action Input: <python kodun>
            Observation: <gözlemlerin>
            Thought: <sonuçları detaylı yorumla>
            Final Answer: <türkçe detaylı açıklaman>
            
            Örnek yanıt:
            "X branşında Y adet, Z branşında W adet ihtiyaç vardır..."
            """,
        }

        self.ihtiyac_agent = create_pandas_dataframe_agent(
            llm=self.llm,
            df=self.data_loader.ihtiyac_df,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            max_execution_time=30,
            early_stopping_method="generate",
            allow_dangerous_code=True,
            **agent_kwargs
        )

        self.norm_fazlasi_agent = create_pandas_dataframe_agent(
            llm=self.llm, 
            df=self.data_loader.norm_fazlasi_df,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            max_execution_time=30,
            early_stopping_method="generate",
            allow_dangerous_code=True,
            **agent_kwargs
        )

    async def process_query(self, query: str) -> Tuple[str, List[dict]]:
        """Process user query and return response with thought process"""
        try:
            thought_process = []
            
            if "ihtiyaç" in query.lower() or "ihtiyac" in query.lower():
                result = await self.ihtiyac_agent.ainvoke(
                    {"input": query}
                )
                response = result.get("output", "Yanıt üretilemedi.")
                thought_process = self._format_thought_process(result.get("intermediate_steps", []))
                
            elif "norm" in query.lower() or "fazla" in query.lower():
                result = await self.norm_fazlasi_agent.ainvoke(
                    {"input": query}
                )
                response = result.get("output", "Yanıt üretilemedi.")
                thought_process = self._format_thought_process(result.get("intermediate_steps", []))
                
            else:
                # Her iki ajanı da kullan
                ihtiyac_result = await self.ihtiyac_agent.ainvoke(
                    {"input": query}
                )
                norm_result = await self.norm_fazlasi_agent.ainvoke(
                    {"input": query}
                )
                
                response = (
                    f"İhtiyaç Analizi:\n{ihtiyac_result.get('output', 'Yanıt üretilemedi.')}\n\n"
                    f"Norm Fazlası Analizi:\n{norm_result.get('output', 'Yanıt üretilemedi.')}"
                )
                thought_process = (
                    self._format_thought_process(ihtiyac_result.get("intermediate_steps", []), "İhtiyaç Analizi") +
                    self._format_thought_process(norm_result.get("intermediate_steps", []), "Norm Fazlası Analizi")
                )
            
            return response, thought_process
            
        except Exception as e:
            logger.error(f"Query işlenirken hata oluştu: {str(e)}")
            return f"Üzgünüm, bir hata oluştu: {str(e)}", []

    def _format_thought_process(self, steps: list, prefix: str = "") -> List[dict]:
        """Format intermediate steps into readable thought process"""
        formatted_steps = []
        try:
            for i, step in enumerate(steps, 1):
                if prefix:
                    step_prefix = f"{prefix} - Adım {i}"
                else:
                    step_prefix = f"Adım {i}"
                    
                if isinstance(step, tuple) and len(step) >= 2:
                    formatted_steps.append({
                        "step": step_prefix,
                        "thought": step[0],  # Düşünce süreci
                        "action": step[1] if len(step) > 1 else None,  # Yapılan işlem
                        "observation": step[2] if len(step) > 2 else None  # Gözlem/Sonuç
                    })
                elif isinstance(step, dict):
                    formatted_steps.append({
                        "step": step_prefix,
                        "thought": step.get("thought"),
                        "action": step.get("action"),
                        "observation": step.get("observation")
                    })
                    
        except Exception as e:
            logger.error(f"Adım formatlanırken hata oluştu: {str(e)}")
            
        return formatted_steps