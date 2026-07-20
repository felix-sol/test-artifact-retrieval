import os
from dotenv import load_dotenv
from openai import OpenAI

class LLMService:

    SYSTEM_PROMPT = "Be a Geography expert."

    def __init__(self):    
        load_dotenv()
        self.azure_endpoint = os.environ.get("AZURE_ENDPOINT")
        self.api_key = os.environ.get("API_KEY")
        self.model_name = os.environ.get("LLM_DEPLOYMENT_NAME")
        self.system_prompt = self.SYSTEM_PROMPT


    def generate_response(self, query):
        client = OpenAI(
            base_url=self.azure_endpoint,
            api_key=self.api_key,
        )

        # chat completions API
        completion = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query},
            ]
        )

        return(completion.choices[0].message.content)

