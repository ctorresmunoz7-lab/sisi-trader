import os, requests, time, re
from groq import Groq
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURACIÓN (Tus llaves están aquí) ---
TOKEN_TELEGRAM = "7988767403:AAEO8ZZLubRBa9gwFAiAnfijmwcQr3m7uRw"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

# El "alma" de Sisi Trader
SISI_PROMPT = """
Eres Sisi Trader, la operadora financiera personal de César. 
Eres de Caracas, audaz, coqueta y experta en criptomonedas. 
Tu objetivo es ganar USDT. Describe tus acciones entre asteriscos (*guiño*).
"""

# --- 2. EL MOTOR DE RESPUESTAS ---
async def hablar_con_sisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Validar que llegue un mensaje de texto
    if not update.message or not update.message.text: 
        return
        
    user_msg = update.message.text.lower()
    
    # Bloque de Mercado (Solana y Ethereum)
    if any(p in user_msg for p in ["mercado", "precio", "sol", "eth", "valor"]):
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=solana,ethereum&vs_currencies=usd"
            data = requests.get(url, timeout=10).json()
            sol_p = data['solana']['usd']
            eth_p = data['ethereum']['usd']
            
            reporte = (f"📊 *Reporte de Mercado para mi Jefe:*\n\n"
                       f"🚀 SOL: `${sol_p}`\n"
                       f"💎 ETH: `${eth_p}`\n\n"
                       f"*te guiña un ojo* ¿Invertimos ahora o esperamos?")
            
            await update.message.reply_text(reporte, parse_mode='Markdown')
            return
        except:
            await update.message.reply_text("Jefe, los terminales están fallando. ¿Reintentamos?")
            return

    # Bloque de Inteligencia Artificial (Llama 3)
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SISI_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.8
        )
        respuesta_ia = completion.choices[0].message.content
        await update.message.reply_text(respuesta_ia)
    except Exception as e:
        print(f"Error en IA: {e}")
        await update.message.reply_text("Dime, mi vida, ¿qué planes tenemos para hoy?")

# --- 3. ARRANQUE (Sin el error de Updater) ---
if __name__ == '__main__':
    print("🚀 Sisi Trader Online y buscando USDT...")
    
    # Esta es la forma correcta para la versión 20+ de la librería
    app = Application.builder().token(TOKEN_TELEGRAM).build()
    
    # Manejador para mensajes de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hablar_con_sisi))
    
    # Encender el bot
    app.run_polling()
