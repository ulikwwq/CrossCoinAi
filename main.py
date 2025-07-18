import logging
import requests
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔐 ЗАМЕНИ НА СВОИ КЛЮЧИ (не выкладывай в сеть!)
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# 🔧 Настройка логов
logging.basicConfig(level=logging.INFO)

# 💰 Получение цены криптовалюты и изменение за 24ч
def get_price(symbol="bitcoin"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd&include_24hr_change=true"
    try:
        response = requests.get(url).json()
        price = response[symbol]["usd"]
        change = response[symbol]["usd_24h_change"]
        emoji = "📈" if change >= 0 else "📉"
        return f"{emoji} {symbol.capitalize()}: {price:.2f}$ ({change:+.2f}% за 24ч)"
    except Exception as e:
        logging.error(f"Ошибка при получении цены: {e}")
        return "❌ Не удалось получить цену. Пример: /price BTC"

# 🧠 Ответ ИИ
async def ai_answer(text):
    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # можно заменить на gpt-3.5-turbo при необходимости
            messages=[
                {"role": "system", "content": "Ты помощник по криптовалютам. Отвечай кратко, понятно и полезно."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        return "🤖 Ошибка при обращении к ИИ."

# 📍 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, я 🤖 *Crypto AI Bot*!\n\n"
        "Вот что я умею:\n"
        "/price BTC — курс крипты\n"
        "Напиши вопрос — я отвечу с помощью ИИ\n"
        "Поддержка: BTC, ETH, TON, и другие\n",
        parse_mode="Markdown"
    )

# 💵 Команда /price
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Пример: /price BTC")
        return
    symbol_input = context.args[0].lower()
    name_map = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "ton": "the-open-network",
        "bnb": "binancecoin",
        "sol": "solana",
        "ada": "cardano",
        "doge": "dogecoin",
        "xrp": "ripple"
    }
    symbol = name_map.get(symbol_input, symbol_input)
    result = get_price(symbol)
    await update.message.reply_text(result)

# ✉️ Обычные сообщения
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = await ai_answer(user_text)
    await update.message.reply_text(reply)

# 🚀 Запуск приложения
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
