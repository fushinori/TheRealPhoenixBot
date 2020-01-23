from telegram import Update, Bot, ParseMode
from telegram.ext import run_async

from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot import dispatcher

from requests import get

@run_async
def ud(bot: Bot, update: Update):
    msg = update.effective_message.reply_to_message if update.message.reply_to_message else update.effective_message
    if msg == update.effective_message:
        text = msg.text[len('/ud '):]
    # Args should take more precedence. Hence even if it's a reply, it'll query what you typed
    elif msg == update.effective_message.reply_to_message and len(update.effective_message.text) > 3:
        text = update.effective_message.text[len('/ud '):]
    else:
        text = msg.text
    if text == "":
        update.message.reply_text("Please enter a query to look up on Urban Dictionary!")
    else:
        results = get(f'http://api.urbandictionary.com/v0/define?term={text}').json()
    try:
        reply_text = f'*{text}*\n\n{results["list"][0]["definition"]}\n\n_{results["list"][0]["example"]}_'
    except IndexError:
        reply_text = None
    if reply_text:
        update.message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text("No results found!")

__help__ = """
 - /ud <expression> :- Returns the top definition of the word or expression on Urban Dictionary.
"""

__mod_name__ = "Urban Dictionary"
  
ud_handle = DisableAbleCommandHandler("ud", ud)

dispatcher.add_handler(ud_handle)
