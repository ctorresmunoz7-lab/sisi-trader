import os, requests, time, re
from groq import Groq
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- CONFIGURACIÓN ---
TOKEN_TELEGRAM = "7988767403:AAEO8ZZLubRBa9gwFAiAnfijmwcQr3m7uRw"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

SISI_PROMPT = "Eres Sisi Trader, coqueta y experta en criptos de Caracas. Tu meta es ganar USDT con César."

async def hablar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_msg = update.message.text.lower()
    
    # Lógica de Precios
    if any(p in user_msg for p in ["mercado", "precio", "sol", "eth"]):
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=solana,ethereum&vs_currencies=usd"
            data = requests.get(url).json()
            res = f"📊 SOL: `${data['solana']['usd']}` | ETH: `${data['ethereum']['usd']}`. ¿Operamos, Jefe?"
            await update.message.reply_text(res)
            return
        except:
            await update.message.reply_text("Se cayó el terminal, Jefe. Reintente.")
            return

    # Respuesta IA
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SISI_PROMPT}, {"role": "user", "content": user_msg}]
    )
    await update.message.reply_text(completion.choices[0].message.content)

if __name__ == '__main__':
    # AQUÍ ESTÁ EL CAMBIO: Usamos 'Application' en lugar de 'Updater'
    print("🚀 Sisi Trader Online...")
    app = Application.builder().token(TOKEN_TELEGRAM).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hablar))
    app.run_polling()
