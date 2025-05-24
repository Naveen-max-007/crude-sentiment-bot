import asyncio
import requests
from textblob import TextBlob
from telegram import Bot
from telegram.constants import ParseMode
import logging
import os

# Logging setup
logging.basicConfig(level=logging.INFO)
CACHE_FILE = "sent_headlines.txt"

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

def load_sent_headlines():
    if not os.path.exists(CACHE_FILE):
        return set()
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_sent_headline(headline):
    with open(CACHE_FILE, "a", encoding="utf-8") as f:
        f.write(headline + "\n")

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return "Bullish"
    elif polarity < -0.1:
        return "Bearish"
    else:
        return "Neutral"

def sentiment_to_signal(sentiment):
    if sentiment == "Bullish":
        return "📈 Signal: BUY CALL OPTION "
    elif sentiment == "Bearish":
        return "📉 Signal: BUY PUT OPTION"
    else:
        return "📊 Signal: NO CLEAR DIRECTION"

async def send_single_headline(title):
    sentiment = analyze_sentiment(title)
    signal = sentiment_to_signal(sentiment)
    message = (
        "🛢️ <b>Crude Oil News Sentiment Update:</b>\n\n"
        f"[{sentiment}] {title}\n\n"
        f"{signal}"
    )
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.HTML)

async def main():
    logging.info("Fetching latest news headline...")
    headlines = fetch_crude_oil_news()
    if not headlines:
        logging.info("No headlines found.")
        return

    latest = headlines[0]  # Get only the latest headline
    sentiment = analyze_sentiment(latest)
    signal = sentiment_to_signal(sentiment)
    message = (
        "🛢️ <b>Crude Oil News Sentiment Update:</b>\n\n"
        f"[{sentiment}] {latest}\n\n"
        f"{signal}"
    )
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
    logging.info(f"Sent latest headline: {latest}")


if __name__ == "__main__":
    asyncio.run(main())
