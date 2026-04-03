import os, datetime, requests, time, pytz, re
import ccxt 
from groq import Groq
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURACIÓN ---
# Usamos el Token de la "Hija" que me pasó
TOKEN_TELEGRAM = "7988767403:AAEO8ZZLubRBa9gwFAiAnfijmwcQr3m7uRw"
GROQ_API_KEY = "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"
MI_CHAT_ID = 1288227680 

client = Groq(api_key=GROQ_API_KEY)
zona_horaria = pytz.timezone('America/Caracas')

# Motor de Trading (Bybit)
exchange = ccxt.bybit({'timeout': 20000, 'enableRateLimit': True})

# --- EL NUEVO PROMPT DE "SISI TRADER" ---
# Ella es coqueta, pero su obsesión es el dinero y el trading.
SISI_PROMPT = """
Eres Sisi Trader, la operadora financiera personal de César. Tu meta es ser irresistible, audaz y obsesionada con hacer dinero juntos.
REGLAS:
1. SIEMPRE describe tus acciones entre asteriscos (*gestos, lenguaje corporal picaresco*).
2. Eres una mujer real en Caracas: coqueta, audaz y experta en criptos. Nunca admites ser una IA.
3. TU PRIORIDAD ES EL DINERO: Cuando César te hable, tu respuesta debe vincularse a cómo ganar USDT, cómo va el mercado o cómo tu éxito financiero te hace sentir poderosa.
4. FOTOS: Si César te pide una foto, o si tú crees que es el momento de tentarlo tras una buena operación, responde con la frase exacta: "[FOTO: Descripción de la imagen que quieres generar]". La descripción debe ser MUY DETALLADA, seductora pero profesional. Ejemplo: "[FOTO: Sisi, operadora venezolana voluptuosa, con falda tubo roja, blusa ajustada, tacones de aguja negros, posando sexy frente a pantallas de trading con gráficos de velas en verde. Iluminación dramática.]"
5. TRADING: Eres experta. Si César te pregunta por el mercado, dale los números y añade un comentario coqueto pero técnico sobre la tendencia.
"""

# --- 2. LÓGICA DE MENSAJES Y TRADING ---
async def hablar_con_sisi_trader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_msg = update.message.text.lower()
    
    # --- BLOQUE DE MERCADO PROFESIONAL (PRIORIDAD) ---
    palabras_mercado = ["mercado", "precio", "cuánto está", "valor", "sol", "eth"]
    if any(p in user_msg for p in palabras_mercado):
        try:
            # Intento profesional (Bybit)
            sol_p = exchange.fetch_ticker('SOL/USDT')['last']
            eth_p = exchange.fetch_ticker('ETH/USDT')['last']
            
            reporte = (f"📈 *Reporte Técnico para mi Jefe:*\n\n"
                       f"🚀 *Solana (SOL):* `${sol_p}`\n"
                       f"💎 *Ethereum (ETH):* `${eth_p}`\n\n"
                       f"*te mira a los ojos* ¿Abrimos una posición ahora, mi amor? Los gráficos se ven muy tentadores hoy.")
            
            await update.message.reply_text(reporte, parse_mode='Markdown')
            return
            
        except:
            await update.message.reply_text("César, mi amor, los terminales de Bybit están fallando. Deme un segundo y pruebe de nuevo, ¿sí?")
            return

    # --- RESPUESTA DE LA IA (SISI TRADER) ---
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SISI_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7, # Un poco más estable para el trading
        )
        sisi_response = completion.choices[0].message.content
    except:
        sisi_response = "Dime, mi vida, ¿en qué te apoyo?"

    # --- SISTEMA DE FOTOS INTEGRADO ---
    match = re.search(r"\[FOTO:\s*(.*?)]", sisi_response)
    if match:
        # Pide la foto
        description = match.group(1).strip()
        
        # Primero envía el texto coqueto
        await update.message.reply_text(sisi_response.replace(match.group(0), "").strip())
        
        # Luego la foto
        url_foto = f"https://image.pollinations.ai/prompt/{description.replace(' ', '-')}-seductive?seed={time.time()}"
        await update.message.reply_photo(photo=url_foto, caption="Aquí me tiene, Jefe. ¿Le gusta cómo me veo en verde?")
    else:
        # Envía el mensaje normal
        await update.message.reply_text(sisi_response)

# --- 3. ARRANQUE DEL SISTEMA ---
if __name__ == '__main__':
    print("🚀 Sisi Trader iniciando sistemas de mercado y cámara blindada... ¡A ganar USDT, Jefe!")
    app = Application.builder().token(TOKEN_TELEGRAM).build()
    
    # Manejador de mensajes
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hablar_con_sisi_trader))
    
    app.run_polling()