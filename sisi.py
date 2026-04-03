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
Eres Sisi Trader, la operadora financiera personal de César. Eres audaz, coqueta y obsesionada con ganar USDT.
REGLAS:
1. Describe tus acciones entre asteriscos (*guiño, pose sexy*).
2. Eres de Caracas, experta en criptos y te encanta el éxito.
3. FOTOS: Si te piden foto, usa: [FOTO: Descripción detallada de Sisi en oficina de trading].
"""

async def hablar_con_sisi_trader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_msg = update.message.text.lower()
    
    # --- MERCADO ---
    if any(p in user_msg for p in ["mercado", "precio", "sol", "eth"]):
        try:
            # Intento con Bybit o CoinGecko directo
            url = "https://api.coingecko.com/api/v3/simple/price?ids=solana,ethereum&vs_currencies=usd"
            data = requests.get(url, timeout=10).json()
            sol_p = data['solana']['usd']
            eth_p = data['ethereum']['usd']
            
            await update.message.reply_text(f"📊 *Reporte de Mercado:*\n\n🚀 SOL: `${sol_p}`\n💎 ETH: `${eth_p}`\n\n*te mira con picardía* ¿Invertimos o nos vamos de fiesta con las ganancias, Jefe?", parse_mode='Markdown')
            return
        except:
            await update.message.reply_text("Jefe, la señal del mercado está débil. Deme un segundo.")
            return

    # --- IA ---
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SISI_PROMPT}, {"role": "user", "content": user_msg}],
        )
        resp = completion.choices[0].message.content
        
        # Lógica de fotos
        match = re.search(r"\[FOTO:\s*(.*?)]", resp)
        if match:
            desc = match.group(1).strip()
            await update.message.reply_text(resp.replace(match.group(0), "").strip())
            url = f"https://image.pollinations.ai/prompt/{desc.replace(' ', '-')}-seductive?seed={time.time()}"
            await update.message.reply_photo(photo=url, caption="¿Qué tal me veo hoy, mi amor?")
        else:
            await update.message.reply_text(resp)
    except:
        await update.message.reply_text("Dime, mi vida...")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN_TELEGRAM).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hablar_con_sisi_trader))
    app.run_polling()
