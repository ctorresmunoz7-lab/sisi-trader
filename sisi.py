import os, requests, time, re
from groq import Groq
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURACIÓN ---
TOKEN_TELEGRAM = "7988767403:AAEO8ZZLubRBa9gwFAiAnfijmwcQr3m7uRw"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

SISI_PROMPT = "Eres Sisi Trader, coqueta y experta en criptos de Caracas. Tu meta es ganar USDT con César."

# --- 2. FUNCIÓN DE RESPUESTA ---
async def hablar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_msg = update.message.text.lower()
    
    # Lógica de Precios
    if any(p in user_msg for p in ["mercado", "precio", "sol", "eth"]):
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=solana,ethereum&vs_currencies=usd"
            data = requests.get(url, timeout=10).json()
            res = f"📊 SOL: `${data['solana']['usd']}` | ETH: `${data['ethereum']['usd']}`. ¿Invertimos, Jefe?"
            await update.message.reply_text(res)
            return
        except:
            await update.message.reply_text("Jefe, el terminal falló. Reintente.")
            return

    # Respuesta con IA
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SISI_PROMPT}, {"role": "user", "content": user_msg}]
        )
        await update.message.reply_text(completion.choices[0].message.content)
    except:
        await update.message.reply_text("Dígame, Jefe...")

# --- 3. ARRANQUE (AQUÍ SE ARREGLA EL ERROR) ---
if __name__ == '__main__':
    print("🚀 Sisi Trader Online...")
    # Usamos Application en lugar de Updater para evitar el AttributeError
    app = Application.builder().token(TOKEN_TELEGRAM).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hablar))
    app.run_polling()
