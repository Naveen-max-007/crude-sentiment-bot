import asyncio
import requests
from textblob import TextBlob
from telegram import Bot
from telegram.constants import ParseMode
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)

NEWS_API_KEY = "750cc6bad910478ea2cbbbad5aa6a65b"
TELEGRAM_API_KEY = "7679824546:AAF04WjNKRqno5FTOir8kvyOCxXO2apEQcA"
TELEGRAM_CHAT_ID = "1305865938"

bot = Bot(token=TELEGRAM_API_KEY)

def fetch_crude_oil_news():
    url = f"https://newsapi.org/v2/everything?q=crude+oil&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [article["title"] for article in articles[:10]]
    return []

def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return "Bullish"
    elif analysis.sentiment.polarity < -0.1:
        return "Bearish"
    else:
        return "Neutral"

async def send_telegram_message(message):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.HTML)

def determine_signal(sentiments):
    bullish = sentiments.count("Bullish")
    bearish = sentiments.count("Bearish")
    if bullish > bearish:
        return "📈 Signal: BUY CALL OPTION"
    elif bearish > bullish:
        return "📉 Signal: BUY PUT OPTION"
    else:
        return "📊 Signal: NO CLEAR DIRECTION"

async def main():
    logging.info("Fetching news and sending alert...")
    headlines = fetch_crude_oil_news()
    results = [(title, analyze_sentiment(title)) for title in headlines]
    message = "🛢️ <b>Crude Oil News Sentiment Update:</b>\n\n"
    sentiments = []
    for title, sentiment in results:
        message += f"[{sentiment}] {title}\n"
        sentiments.append(sentiment)
    message += f"\n{determine_signal(sentiments)}"
    await send_telegram_message(message)

if __name__ == "__main__":
    asyncio.run(main())
