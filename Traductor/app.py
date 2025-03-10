import random
from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import wave
import os

app = Flask(__name__)

r = sr.Recognizer()
translator = Translator()

# Diccionario de idiomas soportados con nombres completos
idiomas_nombre = {
    "fr": "Francés",
    "pt": "Portugués",
    "es": "Español",
    "en": "Inglés",
    "de": "Alemán",
    "it": "Italiano",
    "ru": "Ruso",
    "ja": "Japonés",
    "zh-cn": "Chino Mandarín",
    "ar": "Árabe",
    "nl": "Neerlandés",
    "ko": "Coreano",
    "hi": "Hindi",
    "tr": "Turco",
    "pl": "Polaco",
    "sv": "Sueco",
    "fi": "Finlandés",
    "el": "Griego"
}

# Idiomas de prueba para reconocimiento de voz
idiomas_prueba = ["fr-FR", "pt-BR", "es-ES", "en-US", "de-DE", "it-IT", "ru-RU", "ja-JP", "zh-CN", "ar-SA",
                  "nl-NL", "ko-KR", "hi-IN", "tr-TR", "pl-PL", "sv-SE", "fi-FI", "el-GR"]

def reconocer(sonido):
    for idioma in idiomas_prueba:
        try:
            query = r.recognize_google(sonido, language=idioma)
            if query:
                print(f"La persona dijo: {query}")

                # Detectar el idioma usando Google Translate
                idioma_detectado = translator.detect(query).lang
                nombre_idioma_detectado = idiomas_nombre.get(idioma_detectado, "Desconocido")

                print(f"Idioma detectado: {nombre_idioma_detectado}")

                # Seleccionar un idioma de destino aleatorio diferente del detectado
                posibles_idiomas = list(set(idiomas_nombre.keys()) - {idioma_detectado})
                idioma_destino = random.choice(posibles_idiomas) if posibles_idiomas else "en"
                nombre_idioma_destino = idiomas_nombre.get(idioma_destino, "Inglés")  # Si no está, por defecto inglés

                # Traducimos el mensaje
                traduccion = translator.translate(query, src=idioma_detectado, dest=idioma_destino).text
                print(f"Traducción a {nombre_idioma_destino}: {traduccion}")

                # Convertimos texto a voz
                tts = gTTS(text=traduccion, lang=idioma_destino)
                tts.save("static/traduccion.mp3")

                return {
                    "mensaje": query,
                    "idioma_detectado": nombre_idioma_detectado,
                    "traduccion": traduccion,
                    "idioma_destino": nombre_idioma_destino
                }
        except:
            continue

    return {
        "mensaje": "Nada",
        "idioma_detectado": "Desconocido",
        "traduccion": "No se pudo traducir",
        "idioma_destino": "Ninguno"
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/traducir_texto", methods=["POST"])
def traducir_texto():
    data = request.get_json()
    texto = data.get("texto")
    idioma_destino = data.get("idiomaDestino")

    if not texto:
        return jsonify({"error": "No se recibió ningún texto"}), 400

    try:
        # Detectar el idioma del texto ingresado
        idioma_detectado = translator.detect(texto).lang
        nombre_idioma_detectado = idiomas_nombre.get(idioma_detectado, "Desconocido")

        # Traducir el texto
        traduccion = translator.translate(texto, src=idioma_detectado, dest=idioma_destino).text

        # Convertimos texto a voz
        tts = gTTS(text=traduccion, lang=idioma_destino)
        tts.save("static/traduccion.mp3")

        return jsonify({
            "mensaje": texto,
            "idioma_detectado": nombre_idioma_detectado,
            "traduccion": traduccion,
            "idioma_destino": idiomas_nombre.get(idioma_destino, "Desconocido")
        })
    except Exception as e:
        return jsonify({"error": f"Error al traducir: {e}"}), 500


@app.route("/traducir", methods=["POST"])
def traducir():
    if "audio" not in request.files:
        return jsonify({"error": "No se envió ningún archivo de audio"}), 400

    audio_file = request.files["audio"]
    idioma_destino = request.form.get("idiomaDestino", "en")

    audio_path = "audio.wav"
    audio_file.save(audio_path)

    # Verificar si el archivo realmente es un WAV válido
    try:
        with wave.open(audio_path, "rb") as wf:
            if wf.getnchannels() == 0:
                raise ValueError("Archivo WAV inválido")
    except wave.Error as e:
        return jsonify({"error": f"El archivo de audio no es un WAV válido: {e}"}), 400

    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)

    try:
        query = r.recognize_google(audio)
        if not query:
            return jsonify({"error": "No se pudo reconocer el audio"}), 400
    except sr.UnknownValueError:
        return jsonify({"error": "No se entendió el audio, intenta hablar más claro"}), 400
    except sr.RequestError:
        return jsonify({"error": "Error en el servicio de reconocimiento de voz"}), 500

    try:
        idioma_detectado = translator.detect(query).lang
        traduccion = translator.translate(query, src=idioma_detectado, dest=idioma_destino).text

        # Convertimos texto a voz
        tts = gTTS(text=traduccion, lang=idioma_destino)
        tts.save("static/traduccion.mp3")

        return jsonify({
            "mensaje": query,
            "idioma_detectado": idiomas_nombre.get(idioma_detectado, "Desconocido"),
            "traduccion": traduccion,
            "idioma_destino": idiomas_nombre.get(idioma_destino, "Desconocido")
        })
    except Exception as e:
        return jsonify({"error": f"Error en la traducción: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
