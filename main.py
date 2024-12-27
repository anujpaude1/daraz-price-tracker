import os
from datetime import datetime, date, timedelta,time
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters,CallbackQueryHandler
from telegram.ext import ContextTypes, CallbackContext
from dotenv import load_dotenv
from prisma import Prisma
from scrapePrice import DarazScraper
from datetime import datetime
import re
import asyncio
from utils import generate_price_chart
from pytz import timezone  # Import timezone from pytz
from src.logger import setup_logger
# Load environment variables
load_dotenv()

# Initialize Prisma client
prisma = Prisma()
scraper = DarazScraper()
tz = timezone("Asia/Kathmandu")
log=setup_logger(__name__)

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

    await update.message.reply_text(await welcome_message(),parse_mode='HTML')
    await update.message.reply_text(await  main_menu_message(),
                            reply_markup=await main_menu_keyboard(context=context),parse_mode='HTML')

# Message handler
async def set_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_product_link'):
        await update.message.reply_text("Hold on, let me check the price for you...")
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
        details = await fetch_price(product_link)

        # Store product data in the database
        user = await prisma.user.find_unique(where={'telegramId': str(user_id)})
        if user:
            existing_product = await prisma.product.find_unique(where={'uniqueIdentifier': details['Product ID']})
            if not existing_product:
                existing_product = await prisma.product.create(
                    data={
                        'name': details['Product Name'],
                        'photoUrl': details['Image URL'],
                        'productUrl': details['Final URL'],
                        'productRefer': details['Final URL'],
                        'uniqueIdentifier': details['Product ID'],
                        'lowestPrice': int(details['Current Price'].replace('Rs. ', '').replace(',', '')),
                        'highestPrice': int(details['Current Price'].replace('Rs. ', '').replace(',', '')),
                        'prices': {
                            'create': {
                                'price': int(details['Current Price'].replace('Rs. ', '').replace(',', ''))
                            }
                        }
                    }
                )
            user_existing_product = await prisma.userproduct.find_first(where={
                'userId': user.id,
                'productId': existing_product.id
            },
                include={
                    'product': True,
                    'user': True
                })
            if not user_existing_product:
                user_existing_product = await prisma.userproduct.create(
                    data={
                        'userId': user.id,
                        'notificationInterval': 'daily',
                        'productId': existing_product.id
                    },
                    include={
                        'product': True,
                        'user': True
                    }
                )

        # Send current product details to the user
        await send_single_product_detail(context, user_existing_product)
        context.user_data['user_product_id'] = user_existing_product.id
        context.user_data['awaiting_product_link'] = False
        if context.user_data['task'] == 'track_price':
            await update.message.reply_text(await track_menu_message(),
                            reply_markup=await track_price_keyboard())
        elif context.user_data['task'] == 'search_better_price':
            await update.message.reply_text("Not Implemented Yet")
            await update.message.reply_text(await main_menu_message(), reply_markup=await main_menu_keyboard(context))
        else:
            await update.message.reply_text(await task_menu_message(), reply_markup=await task_menu_keyboard())
        
    else:
        try:
            custom_price = int(update.message.text)
            user_product_id = context.user_data['user_product_id']

            # Update the custom price in the database
            await prisma.userproduct.update(
                where={'id': user_product_id},
                data={'minPrice': custom_price, 'notificationInterval': 'custom'}
            )
            await update.message.reply_text(f"Notification set to custom price: Rs. {custom_price}")

            # Clear the context data
            context.user_data['awaiting_product_link'] = True
            context.user_data['user_product_id'] = None

            # Send the main menu message
            await update.message.reply_text(await main_menu_message(), reply_markup=await main_menu_keyboard(context), parse_mode='HTML')
        except ValueError:
            await update.message.reply_text("Please enter a valid number for the custom price.")


        


async def search_better_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Not Implemented Yet")

    await update.callback_query.edit_message_text(await main_menu_message(), reply_markup=await main_menu_keyboard(context),parse_mode='HTML')

async def track_price(update,context : ContextTypes.DEFAULT_TYPE ):
    query = update.callback_query
    context.user_data['task'] = 'track_price'

    if not context.user_data.get('user_product_id'):
        await query.edit_message_text("Please send the product link you want to track.")
        context.user_data['awaiting_product_link'] = True
    else:
        await query.answer()
        await query.edit_message_text(await track_menu_message(), reply_markup=await track_price_keyboard())

async def daily_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.message.chat_id
    product_id = context.user_data['user_product_id']
    user = await prisma.user.find_unique(where={'telegramId': str(user_id)}, include={'userProducts': {'include': {'product': True}}})
    userproduct = await prisma.userproduct.find_first(where={'productId': product_id, 'userId': user.id})
    if userproduct:
        await prisma.userproduct.update(
            where={'id': userproduct.id},
            data={'notificationInterval': 'daily'}
        )
        await update.callback_query.answer("Daily Notification Set")
        await update.callback_query.edit_message_text(await main_menu_message(),reply_markup=await main_menu_keyboard(context), parse_mode='HTML')

async def weekly_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.message.chat_id
    product_id = context.user_data['user_product_id']
    user = await prisma.user.find_unique(where={'telegramId': str(user_id)}, include={'userProducts': {'include': {'product': True}}})
    userproduct = await prisma.userproduct.find_first(where={'productId': product_id, 'userId': user.id})
    if userproduct:
        await prisma.userproduct.update(
            where={'id': userproduct.id},
            data={'notificationInterval': 'weekly'}
        )
        await update.callback_query.answer("Weekly Notification Set")
        await update.callback_query.edit_message_text(await main_menu_message(),reply_markup=await main_menu_keyboard(context), parse_mode='HTML')

async def minimum_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.message.chat_id
    product_id = context.user_data['user_product_id']
    user = await prisma.user.find_unique(where={'telegramId': str(user_id)}, include={'userProducts': {'include': {'product': True}}})
    userproduct = await prisma.userproduct.find_first(where={'productId': product_id, 'userId': user.id})
    if userproduct:
        await prisma.userproduct.update(
            where={'id': userproduct.id},
            data={'notificationInterval': 'minimum'}
        )
        await update.callback_query.answer("Minimum Price Notification Set")
        await update.callback_query.edit_message_text(await main_menu_message(),reply_markup=await main_menu_keyboard(context), parse_mode='HTML')


async def custom_minimum_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.message.chat_id
    product_id = context.user_data['user_product_id']
    user = await prisma.user.find_unique(where={'telegramId': str(user_id)}, include={'userProducts': {'include': {'product': True}}})
    userproduct = await prisma.userproduct.find_first(where={'productId': product_id, 'userId': user.id}, include={'product': {'include': {'prices': True}}})
    if userproduct:
        context.user_data['awaiting_custom_price'] = True
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Please enter your custom minimum price, current minimum price is Rs. "+str(userproduct.minPrice))

async def main_menu(update,context):
  query = update.callback_query
  await query.answer()
  await query.edit_message_text(
                        text=await main_menu_message(),
                        reply_markup=await main_menu_keyboard(context=context),parse_mode='HTML')




############################ Keyboards #########################################

async def main_menu_keyboard(context: CallbackContext):
    context.user_data.clear()
    context.user_data['awaiting_product_link'] = True
    context.user_data['task'] = None

    keyboard = [[InlineKeyboardButton('Track Price', callback_data='m1')],
              [InlineKeyboardButton('Search Better Price', callback_data='m2')],
              [InlineKeyboardButton('View Existing Product', callback_data='m2')],

            ]
    return InlineKeyboardMarkup(keyboard)


async def task_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Track Price', callback_data='m1')],
              [InlineKeyboardButton('Search Better Price', callback_data='m2')],
            [InlineKeyboardButton('Main Menu', callback_data='main')]
            ]
  return InlineKeyboardMarkup(keyboard)

async def track_price_keyboard():
  keyboard = [[InlineKeyboardButton('Daily Notification', callback_data='ma1')],
              [InlineKeyboardButton('Weekly Notification', callback_data='ma2')],
              [InlineKeyboardButton('Minimum Price', callback_data='ma3')],
              [InlineKeyboardButton('Custom Minimum Price', callback_data='ma4')],
            [InlineKeyboardButton('Main Menu', callback_data='main')]
                ]
  return InlineKeyboardMarkup(keyboard)


############################# Messages #########################################
async def welcome_message():
    return (
        '👋 <b>Welcome to the Daraz Price Tracker Bot!</b>\n\n'
        '<i>Here are the options you can choose from:</i>\n\n'
        '1️⃣ <b>Track the price of any product</b> 🛒\n'
        '   <i>Stay updated with price changes on your favorite items.</i>\n\n'
        '2️⃣ <b>Search for cheaper options</b> 💰\n'
        '   <i>Find budget-friendly alternatives effortlessly.</i>\n\n'
        '3️⃣ <b>Send a product link to get started</b> 🔗\n'
        '   <i>Paste the product link to begin tracking or searching.</i>\n\n'
        '🎯 <i>Let’s get started!</i>'
    )

async def main_menu_message():
    return '<b> What do you want to do? </b>'

async def task_menu_message():
    return 'What do you want to do?'

async def track_menu_message():
  return 'When do you want to be notified?'





async def send_single_product_detail(context: CallbackContext, userProduct):
    try:
        product = userProduct.product
        if product:
            user = userProduct.user
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
async def send_daily_updates(context: CallbackContext):
    user_id = context.job.data['user_id']
    print(f"Sending daily updates to user {user_id}")
    user = await prisma.user.find_unique(where={'telegramId': user_id}, include={'userProducts': {'include': {'user': True,'product': True}}})
    if user:
        for uproduct in user.userProducts:
            await send_single_product_detail(context, uproduct)

async def schedule_user_daily_update(user,application: Application):
    notification_datetime = datetime.strptime(user.notificationTime, "%H:%M")

    #to check if notification works in 30 seconds
    # notification_datetime= datetime.now() + timedelta(seconds=10)

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
        data={'user_id': user.telegramId},  # Use 'data' instead of 'context'
        
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
    application.add_handler(CallbackQueryHandler(track_price, pattern='m1'))
    application.add_handler(CallbackQueryHandler(search_better_price, pattern='m2'))
    application.add_handler(CallbackQueryHandler(main_menu, pattern='main'))

    
    application.add_handler(CallbackQueryHandler(daily_notification, pattern='ma1'))
    application.add_handler(CallbackQueryHandler(weekly_notification, pattern='ma2'))
    application.add_handler(CallbackQueryHandler(minimum_price, pattern='ma3'))
    application.add_handler(CallbackQueryHandler(custom_minimum_price, pattern='ma4'))

    # Schedule jobs for daily updates
    loop.run_until_complete(schedule_jobs(application))

    # Run the bot
    application.run_polling()

    # Disconnect Prisma client on shutdown
    loop.run_until_complete(prisma.disconnect())

if __name__ == "__main__":
    main()