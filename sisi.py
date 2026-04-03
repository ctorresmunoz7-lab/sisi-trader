import os, datetime, requests, time, pytz, re
import ccxt 
from groq import Groq
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURACIÓN ---
TOKEN_TELEGRAM = "7988767403:AAEO8ZZLubRBa9gwFAiAnfijmwcQr3m7uRw"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)
zona_horaria = pytz.timezone('America/Caracas')
exchange = ccxt.bybit({'timeout': 20000, 'enableRateLimit': True})

SISI_PROMPT = """
Eres Sisi Trader, la operadora financiera de César. Eres audaz, coqueta y obsesionada con el USDT.
1. Describe acciones entre asteriscos (*guiño*).
2. Eres de Caracas y experta en criptos.
3. FOTOS: Responde con [FOTO: descripción] si te las piden.
"""

async def hablar_con_sisi_trader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_msg = update.message.text.lower()
    
    if any(p in user_msg for p in ["mercado", "precio", "sol", "eth", "valor"]):
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=solana,ethereum&vs_currencies=usd"
            data = requests.get(url, timeout=10).json()
            sol_p = data['solana']['usd']
            eth_p = data['ethereum']['usd']
            reporte = (f"📊 *Reporte de Mercado:*\n\n🚀 SOL: `${sol_p}`\n💎 ETH: `${eth_p}`\n\n*te guiña un ojo* ¿Invertimos o esperamos?")
            await update.message.reply_text(reporte, parse_mode='Markdown')
            return
        except:
            await update.message.reply_text("Jefe, conexión inestable. Reintente en un momento.")
            return

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SISI_PROMPT}, {"role": "user", "content": user_msg}],
            temperature=0.8
        )
        resp = completion.choices[0].message.content
        match = re.search(r"\[FOTO:\s*(.*?)]", resp)
        if match:
            desc = match.group(1).strip()
            await update.message.reply_text(resp.replace(match.group(0), "").strip())
            url_foto = f"https://image.pollinations.ai/prompt/{desc.replace(' ', '-')}-seductive?seed={time.time()}"
            await update.message.reply_photo(photo=url_foto, caption="¿Le gusta mi outfit de trading, Jefe?")
        else:
            await update.message.reply_text(resp)
    except Exception as e:
        print(f"Error IA: {e}")
        await update.message.reply_text("Dime, mi vida...")

if __name__ == '__main__':
    print("🚀 Sisi Trader Online...")
    app = Application.builder().token(TOKEN_TELEGRAM).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hablar_con_sisi_trader))
    app.run_polling()
