from datetime import datetime, date
import re
from pytz import timezone
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters,CallbackQueryHandler,ContextTypes, CallbackContext
from src.ui import welcome_message, main_menu_message, main_menu_keyboard, task_menu_message, task_menu_keyboard, track_menu_message, track_price_keyboard
from src.updateUser import schedule_user_daily_update,send_single_product_detail
from src.utils import fetch_price
from src.initialize import prisma,tz,log

async def main_menu(update,context):
  query = update.callback_query
  await query.answer()
  await query.edit_message_text(
                        text=await main_menu_message(),
                        reply_markup=await main_menu_keyboard(context=context),parse_mode='HTML')
  
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
    try:
        if context.user_data.get('awaiting_product_link')==False:
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
            except ValueError as e:
                log.error("An error occurred: Invalid custom price")
                log.error("Stack trace:", exc_info=True)
                await update.message.reply_text("Waiting on your price for previous product...")
        
        
        else:
            await update.message.reply_text("Hold on, let me check the price for you...")
            original_product_link = update.message.text
            url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2})|[/?=&])+')
            if not url_pattern.search(original_product_link):
                await update.message.reply_text("Please send a valid product link.")
                await update.message.reply_text(await main_menu_message(), reply_markup=await main_menu_keyboard(context))
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
            try:
                if context.user_data['task'] == 'track_price':
                    await update.message.reply_text(await track_menu_message(),
                                    reply_markup=await track_price_keyboard())
                elif context.user_data['task'] == 'search_better_price':
                    await update.message.reply_text("Not Implemented Yet")
                    await update.message.reply_text(await main_menu_message(), reply_markup=await main_menu_keyboard(context),pass_mode='HTML')
                else:
                    await update.message.reply_text(await task_menu_message(), reply_markup=await task_menu_keyboard())

            except Exception as e:
                log.error(f"An error occurred: {e}")
                log.error("Stack trace:", exc_info=True)
                await update.message.reply_text(await task_menu_message(), reply_markup=await task_menu_keyboard())



    except Exception as e:
        log.error(f"An error occurred: {e}")
        log.error("Stack trace:", exc_info=True)
        await update.message.reply_text("Hmm 🤔, something went wrong. Please try again.")
        await update.message.reply_text(await main_menu_message(), reply_markup=await main_menu_keyboard(context), parse_mode='HTML')

