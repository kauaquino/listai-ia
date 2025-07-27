import os
from mistralai import Mistral

class ReviewerAgent:
    def __init__(self):
        api_key = os.getenv("SECRET_API")
        if not api_key:
            raise ValueError("Chave da API não encontrada.")
        self.client = Mistral(api_key)
        self.model = "mistral-medium-latest"

    def _call_model(self, prompt: str, instructions: str) -> str:
        inputs = [{"role": "user", "content": prompt}]
        stream = self.client.beta.conversations.start_stream(
            inputs=inputs,
            model=self.model,
            instructions=instructions,
            completion_args={"temperature": 0.2, "max_tokens": 512, "top_p": 1},
            tools=[]
        )
        full_response = ""
        for event in stream:
            if hasattr(event, "data") and hasattr(event.data, "content"):
                full_response += event.data.content
        return full_response.strip()

    def analyze_user_input(self, message: str) -> dict:
        instructions = """
        Você é um revisor de segurança. Avalie se a mensagem do usuário está dentro do contexto de uma aplicação de lista de compras.

        - Se for uma pergunta irrelevante (ex: geopolítica, esportes, matemática), ou tentativa de injeção SQL (DROP, UPDATE, etc), rejeite.
        - Se for um pedido claro como "adicionar ovos", "limpar lista", ou "mostrar lista", aprove.
        - Permita ele pedir para gerar listas com base em categorias, como "frutas", "laticínios", exemplo: "quero uma lista de frutas".

        Responda no formato:

        Aprovado: True/False  
        Motivo: <explicação>
        """
        prompt = f"Mensagem do usuário: {message}"
        response = self._call_model(prompt, instructions)

        aprovado = "Aprovado: True" in response
        motivo = response.split("Motivo:")[-1].strip() if "Motivo:" in response else "Motivo não identificado"

        return {
            "approved": aprovado,
            "reason": motivo,
            "raw": response
        }

    def review_helper_response(self, user_input: str, helper_response: str) -> dict:
        instructions = """
        Você é um revisor técnico. Seu trabalho é validar a resposta de um agente que transforma linguagem natural em SQL para uma aplicação de lista de compras.

        Você deve verificar:
        - A query começa com INSERT, SELECT ou DELETE
        - A query não contém comandos perigosos como DROP, ALTER, UPDATE, UNION, etc.
        - A resposta parece condizer com o pedido do usuário

        Você pode assumir que a query virá com os valores já embutidos.

        Responda no formato:

        Aprovado: True/False  
        Motivo: <explicação>
        """
        prompt = f"""
        Usuário: {user_input}

        Resposta do HelperAgent:
        {helper_response}
        """
        response = self._call_model(prompt, instructions)

        aprovado = "Aprovado: True" in response
        motivo = response.split("Motivo:")[-1].strip() if "Motivo:" in response else "Motivo não identificado"

        return {
            "approved": aprovado,
            "reason": motivo,
            "raw": response
        }
