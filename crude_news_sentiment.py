import requests
from textblob import TextBlob
from telegram import Bot
from telegram.constants import ParseMode
import logging
import os

# Logging setup
logging.basicConfig(level=logging.INFO)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # Set these in Render environment variables
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_API_KEY)

def fetch_crude_oil_news():
    url = f"https://newsapi.org/v2/everything?q=crude+oil&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [article["title"] for article in articles[:1]]  # Only fetch the latest headline
    return []

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
        return "📈 Signal: BUY CALL OPTION"
    elif sentiment == "Bearish":
        return "📉 Signal: BUY PUT OPTION"
    else:
        return "📊 Signal: NO CLEAR DIRECTION"

def send_telegram_message(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.HTML)

def main():
    logging.info("Fetching latest news headline...")
    headlines = fetch_crude_oil_news()
    if not headlines:
        logging.info("No headlines found.")
        return

    latest = headlines[0]
    sentiment = analyze_sentiment(latest)
    signal = sentiment_to_signal(sentiment)
    message = (
        "🛢️ <b>Crude Oil News Sentiment Update:</b>\n\n"
        f"[{sentiment}] {latest}\n\n"
        f"{signal}"
    )
    send_telegram_message(message)
    logging.info(f"Sent latest headline: {latest}")

if __name__ == "__main__":
    main()
