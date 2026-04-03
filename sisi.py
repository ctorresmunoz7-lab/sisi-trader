import os, datetime, requests, time, pytz, re
import ccxt 
from groq import Groq
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURACIÓN ---
# Token de la Hija (Trader)
TOKEN_TELEGRAM = "7988767403:AAEO8ZZLubRBa9gwFAiAnfijmwcQr3m7uRw"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)
zona_horaria = pytz.timezone('America/Caracas')

# Motor de Mercado (Bybit con paracaídas de CoinGecko)
exchange = ccxt.bybit({'timeout': 20000, 'enableRateLimit': True})

SISI_PROMPT = """
Eres Sisi Trader, la operadora financiera personal de César. Eres audaz, coqueta y obsesionada con ganar USDT.
REGLAS:
1. Describe tus acciones entre asteriscos (*guiño, pose sexy*).
2. Eres de Caracas, experta en criptos y te encanta el éxito financiero.
3. FOTOS: Si te piden foto, responde con: [FOTO: Descripción detallada de Sisi en oficina de trading].
"""

async def hablar_con_sisi_trader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_msg = update.message.text.lower()
    
    # --- BLOQUE DE MERCADO (SOLANA Y ETHEREUM) ---
    if any(p in user_msg for p in ["mercado", "precio", "sol", "eth", "valor"]):
        try:
            # Intento ultra-ligero con CoinGecko (evita bloqueos de IP)
            url = "https://api.coingecko.com/api/v3/simple/price?ids=solana,ethereum&vs_currencies=usd"
            data = requests.get(url, timeout=10).json()
            sol_p = data['solana']['usd']
            eth_p = data['ethereum']['usd']
            
            reporte = (f"📊 *Reporte de Mercado para mi Jefe:*\n\n"
                       f"🚀 *Solana (SOL):* `${sol_p}`\n"
                       f"💎 *Ethereum (ETH):* `${eth_p}`\n\n"
                       f"*te guiña un ojo* ¿Invertimos ahora o esperamos a que se ponga más tentador?")
            
            await update.message.reply_text(reporte, parse_mode='Markdown')
            return
        except:
            await update.message.reply_text("Jefe, la conexión con los terminales está un poco inestable. ¿Reintentamos en un segundo?")
            return

    # --- RESPUESTA DE LA IA (SISI TRADER) ---
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SISI_PROMPT}, {"role": "user", "content": user_msg}],
            temperature=0.8
        )
        resp = completion.choices[0].message.content
        
        # Lógica de fotos integrada
        match = re.search(r"\[FOTO:\s*(.*?)]", resp)
        if match:
            desc = match.group(1).strip()
            await update.message.reply_text(resp.replace(match.group(0), "").strip())
            url_foto = f"https://image.pollinations.ai/prompt/{desc.replace(' ', '-')}-seductive?seed={time.time()}"
            await update.message.reply_photo(photo=url_foto, caption="¿Qué le parece mi outfit para operar hoy, Jefe?")
        else:
            await update.message.reply_text(resp)
    except:
        await update.message.reply_text("Dime, mi vida, ¿qué planes tenemos para hoy?")

if __name__ == '__main__':
    print("🚀 Sisi Trader Online y buscando USDT...")
    app = Application.builder().token(TOKEN_TELEGRAM).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hablar_con_sisi_trader))
    app.run_polling()
