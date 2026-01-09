from abc import ABC, abstractmethod
from typing import Optional, List, Dict

class LLMInterface(ABC) :

    @abstractmethod
    def set_generation_model(self, model_id:str):
        pass

    @abstractmethod
    def set_embedding_model(self, model_id:str, embedding_size:int):
        pass

    @abstractmethod
    def generate_text(self, prompt:str,chat_history: List, max_output_token:int,
                            temperature: Optional[float]= None) -> str | None:
        pass
    @abstractmethod 
    def embed_text(self, text:str, document_type:Optional[str]= None) -> List[float] | None:  
        #the document type here state whether it is pdf or query
        pass

    @abstractmethod
    def construct_prompt(self, prompt:str, role:str) -> Dict[str, str]:
        pass
