from ..LLMInterface import LLMInterface
from openai import OpenAI
from ..LLMEnums import OpenAIEnums
from typing import Optional, List
import logging
class OpenAiProvider(LLMInterface):

    def __init__(self, api_key:str, api_url: Optional[str]=None,
                        input_max_input_characters: int=1000,
                        default_generation_max_output: int=1000,
                        default_generation_temperature:float=0.1):
        self.api_key = api_key
        self.api_url = api_url

        self.input_max_input_characters = input_max_input_characters
        self.default_generation_max_output = default_generation_max_output
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id : Optional[str] = None

        self.embedding_model_id : Optional[str] = None
        self.embedding_size : Optional[int] = None    

        self.client = OpenAI(
            api_key=self.api_key, 
            base_url=self.api_url)
        
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
    
    def process_text(self, text:str):
        return text[:self.input_max_input_characters].strip()

    def generate_text(self, prompt:str,chat_history: List, max_output_token:int,
                      temperature: Optional[float]= None):
        
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model was not set") 
            return None
        max_output_token = max_output_token if max_output_token else self.default_generation_max_output
        temperature  = temperature if temperature else self.default_generation_temperature

        
        chat_history.append(
                self.construct_prompt(prompt, OpenAIEnums.USER.value)
            )
        response = self.client.chat.completions.create(
            model = self.generation_model_id, 
            messages=chat_history,
            max_tokens=max_output_token,
            temperature=temperature
        )
        if not response or not response.choices or len(response.choices)==0 or not response.choices[0].message:
            self.logger.error("Error while generating text with OpenAI")
            return None

        return response.choices[0].message.content
    def embed_text(self, text: str, document_type: Optional[str]= None):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model was not set")
            return None
        response = self.client.embeddings.create(
            model= self.embedding_model_id,
            input = self.process_text(text)
        )

        if not (response) or not (response.data) or (len(response.data)==0) or not response.data[0].embedding:
            self.logger.error("Error while embedding model with OpenAI")
            return None

        return response.data[0].embedding
    def construct_prompt(self, prompt: str, role: str):

        return {
            "role": role,
            "content": self.process_text(prompt)
        }
                

         