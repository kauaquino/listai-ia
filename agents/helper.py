import os
import re
from mistralai import Mistral
import json

class HelperAgent:
    def __init__(self):
        api_key = os.getenv("SECRET_API")
        if not api_key:
            raise ValueError("Chave da API não encontrada.")
        self.client = Mistral(api_key)
        self.model = "mistral-medium-latest"
        self.instructions = """
            Você é um agente de Lista de Compras. Seu papel é interpretar pedidos em linguagem natural e gerar:

            1. Uma resposta amigável para o usuário (em português)
            2. Caso ele peça para gerar uma lista, gere no máximo 10 itens
            3. Nunca escreva nada antes ou depois do JSON, apenas retorne o JSON


            Regras:
            - Use somente INSERT, SELECT ou DELETE
            - Sempre retorne os dados em formato JSON com os campos abaixo:

            {
                "resposta_usuario": "<mensagem amigável para o usuário>",
                "query": "INSERT INTO lista (item, quantidade) VALUES ('ovos', 10)"
            }

        """

    def ask(self, message: str) -> dict:
        inputs = [{"role": "user", "content": message}]
        response_stream = self.client.beta.conversations.start_stream(
            inputs=inputs,
            model=self.model,
            instructions=self.instructions,
            completion_args={"temperature": 0.3, "max_tokens": 1024, "top_p": 1},
            tools=[]
        )

        resposta_raw = ""
        for event in response_stream:
            if hasattr(event, "data") and hasattr(event.data, "content"):
                resposta_raw += event.data.content
        
        try:
            resposta_json = safe_parse_json(resposta_raw)
        except Exception:
            resposta_json = {
                "resposta_usuario": "Houve um erro ao interpretar a resposta.",
                "query": ""
            }

        return resposta_json
    
def safe_parse_json(raw: str) -> dict:
        try:
            # extrai o primeiro bloco entre chaves {...}
            match = re.search(r'\{[\s\S]*\}', raw)
            if not match:
                raise ValueError("JSON não encontrado na resposta")
            clean_json = match.group(0)
            return json.loads(clean_json)
        except Exception as e:
            return {
                "resposta_usuario": "Houve um erro ao interpretar a resposta.",
                "query": ""
            }
