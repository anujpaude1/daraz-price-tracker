import os
from dotenv import load_dotenv
from pytz import timezone  # Import timezone from pytz
from src.updateUser import schedule_jobs
from src.mainHandler import main_menu, start, set_product
from src.callBack import daily_notification, weekly_notification, minimum_price, custom_minimum_price,track_price, search_better_price

from telegram.ext import Application, CommandHandler, MessageHandler, filters,CallbackQueryHandler
from src.initialize import prisma, tz, scraper, log
import asyncio

# Load environment variables
load_dotenv()



def main():
    try:
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
    except Exception as e:
        log.error(f"An error occurred: {e}")
if __name__ == "__main__":
    main()