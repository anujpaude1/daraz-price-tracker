from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
############################ Keyboards #########################################

async def main_menu_keyboard(context: CallbackContext):
    context.user_data.clear()
    context.user_data['awaiting_product_link'] = True
    context.user_data['task'] = None

    keyboard = [[InlineKeyboardButton('Track Price', callback_data='m1')],
              [InlineKeyboardButton('Search Better Price', callback_data='m2')],
              [InlineKeyboardButton('View Existing Product', callback_data='m2')],
              [InlineKeyboardButton('Top Searched', callback_data='m2')],
              [InlineKeyboardButton('Loot Deals', callback_data='m2')],



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
    return '<b> Please choose an option or directly send product link ... </b>'

async def task_menu_message():
    return 'What do you want to do?'

async def track_menu_message():
  return 'When do you want to be notified?'