from telegram.ext import Application, CommandHandler, MessageHandler, filters,CallbackQueryHandler
from telegram.ext import ContextTypes, CallbackContext
from telegram import Update
import datetime
from src.initialize import prisma
from src.ui import main_menu_message, main_menu_keyboard, track_menu_message, track_price_keyboard

async def search_better_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Not Implemented Yet")

    # await update.callback_query.edit_message_text(await main_menu_message(), reply_markup=await main_menu_keyboard(context),parse_mode='HTML')

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
        await update.callback_query.edit_message_text("Please enter your custom minimum price, current price is Rs. "+str(userproduct.product.prices[-1].price))