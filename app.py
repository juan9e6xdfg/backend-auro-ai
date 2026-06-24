from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# Acá el servidor busca tu llave secreta escondida en las variables de entorno
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return "Servidor de Auro AI activo y listo.", 200

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    if not data or "prompt" not in data:
        return jsonify({"error": "Falta el prompt"}), 400
    
    user_prompt = data["prompt"]
    is_premium = data.get("is_premium", False)
    
    # Lógica de monetización: si no tiene el gamepass, el texto no puede ser super largo
    if not is_premium and len(user_prompt) > 250:
        return jsonify({"error": "Prompt muy largo para la versión gratuita. ¡Adquiere el pase Premium!"}), 400

    system_instruction = (
        "Eres una IA experta en desarrollo de videojuegos para Roblox Studio (Luau). "
        "Tu único objetivo es devolver el código puro que te pida el usuario. "
        "NO uses bloques de código con marcas de tres acentos invertidos (```), NO des explicaciones, "
        "NO digas 'Aquí tienes tu script'. Devuelve ÚNICAMENTE el código ejecutable limpio."
    )

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        
        response = model.generate_content(user_prompt)
        ai_code = response.text.strip()
        
        return jsonify({"code": ai_code}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
