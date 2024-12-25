from datetime import datetime, time, timedelta, date
from telegram.ext import ContextTypes, CallbackContext
from src.utils import fetch_price,generate_price_chart
from telegram.ext import Application, CommandHandler, MessageHandler, filters,CallbackQueryHandler
from src.initialize import prisma,tz,log


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
            photo = await generate_price_chart(product.id)
            await context.bot.send_photo(
                chat_id=user.telegramId,
                caption=f"<i>Price history for {product.name}</i>",
                photo=photo,
                parse_mode='HTML'
                
            )
            

    except Exception as e:
        await context.bot.send_message(chat_id=user.telegramId, text=f"An error occurred while retrieving product details. Error: {str(e)}")
        log.error(f"An error occurred while sending daily updates to user {user.telegramId}: {str(e)}")

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
