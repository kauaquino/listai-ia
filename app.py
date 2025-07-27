from flask import Flask, request, jsonify
from agents.reviewer import ReviewerAgent
from agents.helper import HelperAgent
from dotenv import load_dotenv
from flask_cors import CORS
from db.db import init_db, executar_comando, listar_itens

load_dotenv()

app = Flask(__name__)
CORS(app)

init_db()
agent = HelperAgent()

@app.route("/chat", methods=["POST"])
def chat():
    try:
        reviewer = ReviewerAgent()
        user_input = request.json.get("message")
        if not user_input:
            return jsonify({"error": "Mensagem não fornecida."}), 400

        analise = reviewer.analyze_user_input(user_input)
        if not analise["approved"]:
            return jsonify({"error": "Ops, não posso ajudar com isso!", "motivo": analise["reason"]}), 403

        resposta = agent.ask(user_input)

        validacao = reviewer.review_helper_response(user_input, f"""
        resposta_usuario = "{resposta['resposta_usuario']}"
        query = {resposta['query']}
        """)

        if not validacao["approved"]:
            return jsonify({"error": "Ops, tente novamente!", "motivo": validacao["reason"]}), 403

        if resposta["query"].lower().startswith(("insert", "delete")):
            executar_comando(resposta["query"])

        return jsonify({ "response": resposta["resposta_usuario"] })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

@app.route("/lista", methods=["GET"])
def lista():
    try:
        itens = listar_itens()
        return jsonify({ "lista": itens })
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True)
