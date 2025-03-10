let recognition;
let isListening = false;

// Verificar si el navegador soporta reconocimiento de voz
if (window.SpeechRecognition || window.webkitSpeechRecognition) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
}

// Función para actualizar el idioma del reconocimiento de voz
function actualizarIdiomaReconocimiento() {
    let idiomaSeleccionado = document.getElementById("idiomaDestino").value;
    let idiomasReconocimiento = {
        "en": "en-US",
        "es": "es-ES",
        "fr": "fr-FR",
        "de": "de-DE",
        "it": "it-IT",
        "pt": "pt-PT",
        "ru": "ru-RU",
        "ja": "ja-JP",
        "zh-cn": "zh-CN",
        "ar": "ar-SA"
    };
    
    recognition.lang = idiomasReconocimiento[idiomaSeleccionado] || "es-ES";
}

// Función para iniciar o detener la escucha automática
function toggleRecognition() {
    if (!isListening) {
        startRecognition();
    } else {
        stopRecognition();
    }
}

// Iniciar reconocimiento de voz en tiempo real
function startRecognition() {
    if (!recognition) {
        alert("Tu navegador no soporta reconocimiento de voz.");
        return;
    }
    
    actualizarIdiomaReconocimiento();
    isListening = true;
    document.getElementById("estado").innerText = "🎤 Escuchando...";
    recognition.start();

    recognition.onresult = async (event) => {
        let texto = event.results[event.results.length - 1][0].transcript;
        document.getElementById("mensaje").value = texto;
        await traducirTexto(texto);
    };

    recognition.onerror = (event) => {
        console.error("Error en reconocimiento de voz: ", event.error);
        stopRecognition();
    };
}

// Detener reconocimiento de voz
function stopRecognition() {
    if (recognition) {
        recognition.stop();
    }
    isListening = false;
    document.getElementById("estado").innerText = "⏸️ Detenido";
}

// Función para traducir texto en tiempo real
async function traducirTexto(texto) {
    let idiomaDestino = document.getElementById("idiomaDestino").value;
    
    if (!texto.trim()) return;
    
    try {
        const response = await fetch("/traducir_texto", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ texto: texto, idiomaDestino: idiomaDestino })
        });
        const data = await response.json();
        
        if (data.error) {
            console.error("Error: ", data.error);
            return;
        }

        // Mostrar idioma detectado y traducción
        document.getElementById("idioma").innerText = data.idioma_detectado;
        document.getElementById("traduccion").value = data.traduccion;
        
        // Reproducir traducción en voz
        let audioElement = document.getElementById("audio");
        audioElement.src = `/static/traduccion.mp3?${Date.now()}`;
        audioElement.load();
        audioElement.play();
    } catch (error) {
        console.error("Error en la traducción: ", error);
    }
}

// Asignar evento al botón de activación/desactivación de reconocimiento de voz
document.getElementById("toggleListen").addEventListener("click", toggleRecognition);

// Detectar cambios en el textarea y traducir en tiempo real
document.getElementById("mensaje").addEventListener("input", function () {
    let texto = this.value;
    traducirTexto(texto);
});

// Detectar cambio de idioma y actualizar el reconocimiento
document.getElementById("idiomaDestino").addEventListener("change", actualizarIdiomaReconocimiento);