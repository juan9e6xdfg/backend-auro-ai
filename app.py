from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
import os

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Memoria temporal para conectar la Web con Roblox
codigo_pendiente = None

# EL DISEÑO DE TU PÁGINA WEB (HTML + CSS + JavaScript integrados)
PAGINA_WEB = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Auro AI - Web Engine</title>
    <style>
        body { background-color: #121214; color: #e1e1e6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { color: #00d2ff; margin: 0; font-size: 32px; letter-spacing: 2px;}
        .header p { color: #8d8d99; margin-top: 5px; }
        #chat-box { width: 90%; max-width: 900px; height: 60vh; background: #202024; border-radius: 12px; padding: 20px; overflow-y: auto; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); border: 1px solid #323238;}
        .msg { margin-bottom: 15px; padding: 15px; border-radius: 8px; line-height: 1.5; font-size: 15px;}
        .user { background: #0078d7; color: white; text-align: left; border-left: 4px solid #00d2ff;}
        .ai { background: #29292e; color: #a8a8b3; text-align: left; border-left: 4px solid #04d361;}
        .input-area { width: 90%; max-width: 900px; display: flex; gap: 10px; }
        input { flex-grow: 1; padding: 18px; border-radius: 8px; border: 1px solid #323238; background: #121214; color: white; font-size: 16px; outline: none; transition: 0.3s;}
        input:focus { border-color: #00d2ff; }
        button { padding: 18px 35px; border: none; border-radius: 8px; background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%); color: white; font-size: 16px; cursor: pointer; font-weight: bold; transition: 0.3s;}
        button:hover { opacity: 0.8; transform: scale(1.02);}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ AURO AI ENGINE</h1>
        <p>Conectado en tiempo real con Roblox Studio</p>
    </div>
    
    <div id="chat-box">
        <div class="msg ai"><b>🤖 Auro AI:</b> Sistema en línea. Abre Roblox Studio, activa la conexión y dime qué quieres construir hoy.</div>
    </div>
    
    <div class="input-area">
        <input type="text" id="prompt" placeholder="Ej: Crea una UI de tienda con esquinas redondeadas en el StarterGui..." onkeypress="if(event.key === 'Enter') enviarOrden()">
        <button onclick="enviarOrden()" id="btn">Construir</button>
    </div>

    <script>
        async function enviarOrden() {
            const input = document.getElementById("prompt");
            const text = input.value;
            if (!text) return;
            
            const chatBox = document.getElementById("chat-box");
            chatBox.innerHTML += `<div class='msg user'><b>👤 Tú:</b> ${text}</div>`;
            input.value = "";
            
            const btn = document.getElementById("btn");
            btn.innerText = "Pensando...";
            btn.style.opacity = "0.5";
            chatBox.scrollTop = chatBox.scrollHeight;
            
            try {
                const res = await fetch("/enviar_orden", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({prompt: text})
                });
                
                const data = await res.json();
                if (data.success) {
                    chatBox.innerHTML += `<div class='msg ai'><b>🤖 Auro AI:</b> ¡Código generado! Míralo aparecer en Roblox Studio.</div>`;
                } else {
                    chatBox.innerHTML += `<div class='msg ai' style='border-color: #ff4a4a; color: #ff4a4a;'><b>❌ Error:</b> ${data.error}</div>`;
                }
            } catch (err) {
                chatBox.innerHTML += `<div class='msg ai' style='border-color: #ff4a4a; color: #ff4a4a;'><b>❌ Falla de conexión con la IA.</b></div>`;
            }
            
            btn.innerText = "Construir";
            btn.style.opacity = "1";
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

# 1. Ruta para entrar a la página web
@app.route("/", methods=["GET"])
def home():
    return render_template_string(PAGINA_WEB)

# 2. Ruta que recibe lo que escribes en la web y le habla a la IA
@app.route("/enviar_orden", methods=["POST"])
def enviar_orden():
    global codigo_pendiente
    data = request.json
    instruccion_usuario = data.get("prompt", "")
    
    instruccion_sistema = (
        "Eres Auro AI. Tu misión es devolver ÚNICAMENTE código Luau ejecutable para Roblox Studio. "
        "No incluyas marcas de texto como ```lua o ```, solo el código puro. "
        "El código debe usar Instance.new() para crear UIs, Scripts, o Modelos y ubicarlos correctamente (StarterGui, Workspace, etc.). "
        "Si el usuario te pide un script para una parte seleccionada, usa 'local seleccion = game:GetService(\"Selection\"):Get()[1]'."
    )
    
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=instruccion_sistema)
        respuesta = model.generate_content(instruccion_usuario)
        codigo_ia = respuesta.text.strip()
        
        # Limpieza de seguridad por si Gemini pone acentos invertidos
        if codigo_ia.startswith("```"):
            lineas = codigo_ia.split("\n")
            if len(lineas) > 2:
                codigo_ia = "\n".join(lineas[1:-1])
        
        # Guardar en memoria para que Roblox lo recoja
        codigo_pendiente = codigo_ia 
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 3. Ruta secreta que usa Roblox para "buscar" si hay nuevas órdenes
@app.route("/roblox_escucha", methods=["GET"])
def roblox_escucha():
    global codigo_pendiente
    if codigo_pendiente:
        codigo_a_enviar = codigo_pendiente
        codigo_pendiente = None # Lo borramos para que no lo ejecute 2 veces
        return jsonify({"hay_codigo": True, "codigo": codigo_a_enviar}), 200
    else:
        return jsonify({"hay_codigo": False}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
