import time
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import ContextTypes,CallbackContext


# Dictionary to store user data (user_id: product_link)
user_data = {}

# Scraper function (example for Amazon product pages)
def fetch_price(product_url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Modify this selector for the website you're targeting
    price_tag = soup.find("span", {"class": "a-price-whole"})  # Example for Amazon
    if price_tag:
        return price_tag.get_text().strip()
    return "Price not found"

# Command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a product link to start tracking its price.")

# Message handler
async def set_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_link = update.message.text
    user_id = update.message.chat_id
    # Add user data handling here
    await update.message.reply_text("Got it! I'll send you daily updates about the price of this product.")

# Function to send daily updates
def send_daily_updates(context: CallbackContext):
    for user_id, product_link in user_data.items():
        try:
            price = fetch_price(product_link)
            context.bot.send_message(chat_id=user_id, text=f"Daily Price Update:\n{product_link}\nCurrent Price: {price}")
        except Exception as e:
            context.bot.send_message(chat_id=user_id, text=f"Failed to fetch price for {product_link}. Error: {str(e)}")

def main():

    # Replace 'YOUR_API_TOKEN' with your bot token
    application = Application.builder().token("7405891258:AAECHaOEacx7VGJoG-K_69mAMtrDSrmhBE4").build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_product))

    # Run the bot
    application.run_polling()


if __name__ == "__main__":
    main()
