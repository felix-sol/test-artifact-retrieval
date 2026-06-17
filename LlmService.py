import os
from dotenv import load_dotenv
from openai import OpenAI

class LLMService:

    def __init__(self):    
        load_dotenv()
        self.azure_endpoint = os.environ.get("AZURE_ENDPOINT")
        self.api_key = os.environ.get("API_KEY")
        self.model_name = os.environ.get("LLM_NAME")


    def generate_response(self, query):
        client = OpenAI(
            base_url=self.azure_endpoint,
            api_key=self.api_key,
        )

        # chat completions API
        completion = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "Be a Geology expert."},
                {"role": "user", "content": query},
            ]
        )

        print(completion.choices[0].message.content)

