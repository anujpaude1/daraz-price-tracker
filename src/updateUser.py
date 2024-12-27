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

# Function to send updates to a specific user
async def send_updates(context: CallbackContext):
    user_id = context.job.data['user_id']
    uproduct = context.job.data['uproduct']
    check = context.job.data['check']
    print(f"Sending daily updates to user {user_id}")
    if not check:
        await send_single_product_detail(context, uproduct)
    else:
        fetch_price(uproduct.product.productUrl, uproduct.product.uniqueIdentifier)
        if check == "minimum":
            if uproduct.product.lowestPrice == uproduct.product.prices[-1].price:
                await send_single_product_detail(context,uproduct)
        elif check == "custom":
            if uproduct.minPrice >= uproduct.product.prices[-1].price:
                await send_single_product_detail(context,uproduct)


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
    userproducts = user.userProducts
    if userproducts:
        for uproduct in userproducts:
            if uproduct.notificationInterval == "daily":
                application.job_queue.run_daily(
                    send_updates,
                    time=notification_time_with_tz,
                    data={'user_id': user.telegramId,
                        "uproduct":uproduct,
                        "check":None},  # Use 'data' instead of 'context'  
                )
            elif uproduct.notificationInterval == "weekly":
                application.job_queue.run_repeating(
                send_updates,
                interval=timedelta(weeks=1),
                first=notification_time_with_tz,
                data={'user_id': user.telegramId,
                    "uproduct": uproduct,
                    "check": None},  # Use 'data' instead of 'context'
            )
            elif uproduct.notificationInterval == "minimum":
                application.job_queue.run_daily(
                    send_updates,
                    day=notification_time_with_tz.weekday(),
                    time=notification_time_with_tz,
                    data={'user_id': user.telegramId,
                        "uproduct":uproduct,
                        "check":"minimum"},  # Use 'data' instead of 'context'  
                )
            
            elif uproduct.notificationInterval == "custom":
                application.job_queue.run_daily(
                    send_updates,
                    day=notification_time_with_tz.weekday(),
                    time=notification_time_with_tz,
                    data={'user_id': user.telegramId,
                        "uproduct":uproduct,
                        "check":"custom"},  # Use 'data' instead of 'context'  
                )
            else:
                pass

async def schedule_jobs(application: Application):
    users = await prisma.user.find_many(
        include={'userProducts': {'include': {'product': {'include': {'prices': True}}}}}
    )
    for user in users:
        await schedule_user_daily_update(user,application=application)
