from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# Conexión segura con tu clave oculta
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return "Motor de Automatización Auro AI v2 Activo.", 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    if not data or "prompt" not in data:
        return jsonify({"error": "Falta la instrucción del desarrollador."}), 400
    
    user_prompt = data["prompt"]
    chat_history = data.get("history", [])  # Recibe la memoria del chat desde Roblox
    is_premium = data.get("is_premium", False)
    
    # Control de abuso para usuarios gratuitos
    if not is_premium and len(user_prompt) > 500:
        return jsonify({"error": "Tu instrucción es muy detallada para el plan gratuito. ¡Consigue el pase Premium!"}), 400

    # INSTRUCCIONES MAESTRAS DE CONSTRUCCIÓN AVANZADA
    system_instruction = (
        "Eres 'Auro AI Engine v2', el motor de inteligencia artificial definitivo integrado en Roblox Studio.\n"
        "Tu función no es solo escribir código aislado, sino generar un script de Luau que se ejecutará "
        "DENTRO del plugin para CREAR, DISEÑAR y CONFIGURAR todo lo que el usuario pida de forma interactiva.\n\n"
        "REGLAS ESTRICTAS DE GENERACIÓN:\n"
        "1. NO uses marcas de bloques de código (```). Devuelve ÚNICAMENTE el código Luau plano y limpio.\n"
        "2. Si piden crear una interfaz (UI), genera código usando Instance.new() para crear ScreenGui, Frames, TextLabels, "
        "botones, etc. Aplica diseños profesionales: esquinas redondeadas (UICorner), colores modernos (gris oscuro, azul eléctrico, blanco texturizado) y colócalos en game.StarterGui.\n"
        "3. Si piden sistemas mecánicos (como velocidad, monedas, sistemas de guardado), tu script de automatización debe crear un Script o LocalScript, "
        "asignar su lógica interna a la propiedad .Source del script creado, y ubicarlo en el servicio correspondiente (ServerScriptService, StarterPlayerScripts, etc.).\n"
        "4. Para actuar sobre lo que el usuario tiene seleccionado actualmente en el Explorador de Studio, usa exactamente esta estructura:\n"
        "   local selection = game:GetService('Selection'):Get()\n"
        "   local target = selection[1] or workspace\n"
        "5. Si piden usar la Toolbox o modelos base, tu código puede instanciar geometrías complejas compuestas o dejar notas estructuradas listas para configurar."
    )

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        
        # Estructurar el historial en el formato nativo que requiere la IA de Google
        formatted_contents = []
        for msg in chat_history:
            formatted_contents.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["text"]]
            })
        
        # Añadir la petición actual al final de la conversación
        formatted_contents.append({"role": "user", "parts": [user_prompt]})
        
        response = model.generate_content(formatted_contents)
        ai_code = response.text.strip()
        
        return jsonify({"code": ai_code}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
