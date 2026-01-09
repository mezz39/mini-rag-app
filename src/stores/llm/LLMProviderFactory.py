from .LLMEnums import LLMEnums
from .providers import OpenAiProvider, CohereProvider
class LLMProviderFactory():
    def __init__(self, config) :
        self.config = config

    def create(self, provider:str):
        if provider == LLMEnums.OPENAI.value:
            return OpenAiProvider(api_key= self.config.OPENAI_API_KEY,
                api_url= self.config.OPENAI_API_URL,
                input_max_input_characters= self.config.input_max_input_characters,
                default_generation_max_output= self.config.default_generation_max_output
            )

        if provider == LLMEnums.COHERE.value:
            return CohereProvider(
                api_key= self.config.COHERE_API_KEY,
                input_max_input_characters= self.config.input_max_input_characters,
                default_generation_max_output= self.config.default_generation_max_output,
                default_generation_temperature= self.config.default_generation_temperature
            )

        return None

            