from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from server.services.data_loader import DataLoader
from server.services.langchain.tools.education_tools import (
    BransKarsilastirmaTool,
    IlceKarsilastirmaTool,
    IlceBransFiltrelemeTool,
    IlceNormFazlasiSiralama
)
from typing import Tuple, List
import os
import time
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

logger = logging.getLogger(__name__)

class DataAnalysisAgent:
    def __init__(self):
        self.data_loader = DataLoader()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY bulunamadı.")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0,
            max_retries=3,
            retry_wait_seconds=2
        )
        
        # Toolları oluştur
        self.tools = [
            BransKarsilastirmaTool(
                self.data_loader.ihtiyac_df,
                self.data_loader.norm_fazlasi_df
            ),
            IlceKarsilastirmaTool(
                self.data_loader.ihtiyac_df,
                self.data_loader.norm_fazlasi_df
            ),
            IlceBransFiltrelemeTool(
                self.data_loader.ihtiyac_df,
                self.data_loader.norm_fazlasi_df
            ),
            IlceNormFazlasiSiralama(
                self.data_loader.ihtiyac_df,
                self.data_loader.norm_fazlasi_df
            )
        ]
        
        # Agent'ı başlat
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )

        # Rate limiting için son istek zamanını tut
        self.last_request_time = 0
        self.min_request_interval = 1  # saniye

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception)),
        after=lambda retry_state: logger.warning(
            f"Retry attempt {retry_state.attempt_number} after error: {retry_state.outcome.exception()}"
        )
    )
    async def process_query(self, query: str) -> Tuple[str, List[dict]]:
        """Process user query and return response with thought process"""
        try:
            # Rate limiting kontrolü
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            
            if time_since_last_request < self.min_request_interval:
                sleep_time = self.min_request_interval - time_since_last_request
                logger.info(f"Rate limiting: Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            
            # İsteği gönder
            result = await self.agent.ainvoke(
                {"input": query}
            )
            
            # Son istek zamanını güncelle
            self.last_request_time = time.time()
            
            response = result.get("output", "Yanıt üretilemedi.")
            thought_process = self._format_thought_process(result.get("intermediate_steps", []))
            
            return response, thought_process
            
        except Exception as e:
            logger.error(f"Query processing error: {str(e)}")
            raise

    def _format_thought_process(self, steps: list) -> List[dict]:
        """Format intermediate steps into readable thought process"""
        formatted_steps = []
        try:
            for i, step in enumerate(steps, 1):
                formatted_steps.append({
                    "step": f"Adım {i}",
                    "thought": step.get("thought", ""),
                    "action": step.get("tool", ""),
                    "observation": step.get("observation", "")
                })
        except Exception as e:
            logger.error(f"Error formatting thought process: {str(e)}")
        return formatted_steps