import logging
import requests
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔐 Токены
TELEGRAM_TOKEN = "7780572322:AAFDqw3n-SJ7Vt5oHbo1PoxVDfJegZkntqo"
OPENAI_API_KEY = "сюда вставим позже"  # напиши, если у тебя уже есть ключ OpenAI

# Настройка логов
logging.basicConfig(level=logging.INFO)

# 🎯 Получение цены криптовалюты
def get_price(symbol="bitcoin"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    response = requests.get(url).json()
    try:
        return f"💰 {symbol.capitalize()} = {response[symbol]['usd']}$"
    except:
        return "Не удалось получить цену. Попробуй BTC, ETH, TON."

# 💬 Ответ через OpenAI
async def ai_answer(text):
    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # или другой
            messages=[{"role": "user", "content": text}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка ИИ: {e}"

# 📥 Обработка команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, я Crypto AI 🤖. Спроси меня о крипте или напиши /price BTC")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Пример: /price BTC")
    else:
        symbol = context.args[0].lower()
        name_map = {"btc": "bitcoin", "eth": "ethereum", "ton": "the-open-network"}
        coin = name_map.get(symbol, symbol)
        await update.message.reply_text(get_price(coin))

# 🧠 Ответ на обычный вопрос
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await ai_answer(update.message.text)
    await update.message.reply_text(reply)

# 🚀 Запуск бота
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("Бот запущен!")
app.run_polling()
