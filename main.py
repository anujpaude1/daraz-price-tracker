import os
from datetime import datetime, date, timedelta,time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import ContextTypes, CallbackContext
from dotenv import load_dotenv
from prisma import Prisma
from scrapePrice import DarazScraper
from datetime import datetime
import re
import asyncio
from utils import generate_price_chart
from pytz import timezone  # Import timezone from pytz
# Load environment variables
load_dotenv()

# Initialize Prisma client
prisma = Prisma()
scraper = DarazScraper()
tz = timezone("Asia/Kathmandu")


# Scraper function using DarazScraper
async def fetch_price(product_url, product_id=None):
    details = scraper.get_product_details(product_url)

   
    if product_id:
            product = await prisma.product.find_unique(where={'uniqueIdentifier': product_id})
            if product:
                current_price = int(details['Current Price'].replace('Rs. ', '').replace(',', ''))
                print(f"Creating price entry with productId: {product.id} and price: {current_price}")
                await prisma.price.create(data={
                    'productId': product.id,
                    'price': current_price
                })
                if current_price < product.lowestPrice:
                    await prisma.product.update(where={'id': product.id}, data={'lowestPrice': current_price})
                if current_price > product.highestPrice:
                    await prisma.product.update(where={'id': product.id}, data={'highestPrice': current_price})
                    await prisma.product.update(where={'id': product.id}, data={'lastFetched': datetime.now()})


    return details

# Command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_name = update.message.from_user.first_name

    # Store user data in the database
    user = await prisma.user.find_unique(where={'telegramId': str(user_id)})
    if not user:
        user= await prisma.user.create(
            data={
                'telegramId': str(user_id),
                'name': user_name,
                'notificationTime': datetime.now(tz=tz).strftime("%H:%M"),
            }
        )

        await schedule_user_daily_update(user, context.application)

    await update.message.reply_text("Welcome! Send me a product link to start tracking its price.")

# Message handler
async def set_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    original_product_link = update.message.text
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2})|[/?=&])+')
    if not url_pattern.search(original_product_link):
        await update.message.reply_text("Please send a valid product link.")
        return
    # Extract the actual product link from the original link
    product_link = re.search(url_pattern, original_product_link).group(0)
    user_id = update.message.chat_id
    chat_id = update.effective_chat.id

    # Fetch product details
    details =await fetch_price(product_link)

    # Store product data in the database
    user = await prisma.user.find_unique(where={'telegramId': str(user_id)})
    if user:
        existing_product = await prisma.product.find_unique(where={'uniqueIdentifier': details['Product ID']})
        if not existing_product:
            await prisma.product.create(
                data={
                    'name': details['Product Name'],
                    'photoUrl': details['Image URL'],
                    'productUrl': details['Final URL'],
                    'productRefer': details['Final URL'],
                    'uniqueIdentifier': details['Product ID'],
                    'lowestPrice': int(details['Current Price'].replace('Rs. ', '').replace(',', '')),
                    'highestPrice': int(details['Current Price'].replace('Rs. ', '').replace(',', '')),
                    'userId': user.id,
                    'prices': {
                        'create': {
                            'price': int(details['Current Price'].replace('Rs. ', '').replace(',', ''))
                        }
                    }
                }
            )

    # Send current product details to the user
    # Call the function to send single product detail
    await send_single_product_detail(context, details['Product ID'])

# Function to send a single product detail by its unique identifier
async def send_single_product_detail(context: CallbackContext, unique_identifier: str):
    try:
        product = await prisma.product.find_unique(where={'uniqueIdentifier': unique_identifier}, include={'user': True, 'prices': True})
        if product:
            user = product.user
            if product.lastFetched and product.lastFetched.date() == date.today():
                current_price = product.prices[-1].price
                highest_price = product.highestPrice
                lowest_price = product.lowestPrice
                product_url = product.productUrl

                message = (
                    f"<b>Product Name:</b> {product.name}\n"
                    f"<b>Current Price:</b> <a href='{product_url}'>Rs. {current_price}</a>\n"
                    f"<b>Highest Price:</b> Rs. {highest_price}\n"
                    f"<b>Lowest Price:</b> Rs. {lowest_price}\n"
                    f"<b>Product URL:</b> <a href='{product_url}'>{product_url}</a>"
                )

                await context.bot.send_message(
                    chat_id=user.telegramId,
                    text=message,
                    parse_mode='HTML'
                )
            else:
                try:
                    details = await fetch_price(product.productUrl, product.uniqueIdentifier)
                    current_price = int(details['Current Price'].replace('Rs. ', '').replace(',', ''))
                    highest_price = product.highestPrice
                    lowest_price = product.lowestPrice
                    product_url = product.productUrl

                    message = (
                        f"<b>Product Name:</b> {details['Product Name']}\n"
                        f"<b>Current Price:</b> <a href='{product_url}'>Rs. {current_price}</a>\n"
                        f"<b>Highest Price:</b> Rs. {highest_price}\n"
                        f"<b>Lowest Price:</b> Rs. {lowest_price}\n"
                        f"<b>Product URL:</b> <a href='{product_url}'>{product_url}</a>"
                    )

                    await context.bot.send_message(
                        chat_id=user.telegramId,
                        text=message,
                        parse_mode='HTML'
                    )
                except Exception as e:
                    await context.bot.send_message(chat_id=user.telegramId, text=f"Failed to fetch price for {product.name}. Error: {str(e)}")
            
            # Send the price chart
            await context.bot.send_photo(
                chat_id=user.telegramId,
                caption=f"<i>Price history for {product.name}</i>",
                photo=await generate_price_chart(product.id),
                parse_mode='HTML'
                
            )
    except Exception as e:
        await context.bot.send_message(chat_id=user.telegramId, text=f"An error occurred while retrieving product details. Error: {str(e)}")


# Function to send daily updates to a specific user
async def send_daily_updates(context: CallbackContext, user_id: str):
    print(f"Sending daily updates to user {user_id}")
    user = await prisma.user.find_unique(where={'telegramId': user_id}, include={'products': {'include': {'prices': True}}})
    if user:
        for product in user.products:
            await send_single_product_detail(context, product.uniqueIdentifier)

async def schedule_user_daily_update(user,application: Application):
    notification_datetime = datetime.strptime(user.notificationTime, "%H:%M")
    notification_time = notification_datetime.time()

    notification_time_with_tz = time(
        hour=notification_time.hour,
        minute=notification_time.minute,
        second=notification_time.second,
        tzinfo=tz  # Attach the timezone
    )

    print(f"Scheduling daily updates for user {user.telegramId} at {notification_time_with_tz} with info {notification_time_with_tz.tzinfo}")

    application.job_queue.run_daily(
        send_daily_updates,
        time=notification_time_with_tz,
        user_id=user.telegramId,
    )

async def schedule_jobs(application: Application):
    users = await prisma.user.find_many()
    for user in users:
        await schedule_user_daily_update(user,application=application)

def main():
    # Replace 'YOUR_API_TOKEN' with your bot token
    token = os.getenv("TOKEN")
    application = Application.builder().token(token).build()
        # Create an event loop
    loop = asyncio.get_event_loop()

    # Connect Prisma client
    loop.run_until_complete(prisma.connect())
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_product))

    # Schedule jobs for daily updates
    loop.run_until_complete(schedule_jobs(application))

    # Run the bot
    application.run_polling()

    # Disconnect Prisma client on shutdown
    loop.run_until_complete(prisma.disconnect())

if __name__ == "__main__":
    main()