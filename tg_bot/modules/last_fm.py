# Last.fm module by @TheRealPhoenix

import pylast

from telegram import Message, Chat, User, Update, Bot, ParseMode
from telegram.ext import CommandHandler,  run_async

from tg_bot import dispatcher, LASTFM_API_KEY
import tg_bot.modules.sql.last_fm_sql as sql
from tg_bot.modules.disable import DisableAbleCommandHandler


@run_async
def set_user(bot: Bot, update: Update, args):
    user_id = update.effective_user.id
    msg = update.effective_message
    username = " ".join(args)
    if username == "":
        msg.reply_text("Username can't be empty!")
    else:
        sql.set_user(user_id, username)
        msg.reply_text("Username set successfully!")
    
    
@run_async
def clear_user(bot: Bot, update: Update):
    user_id = update.effective_user.id
    sql.set_user(user_id, "")
    update.effective_message.reply_text("Username cleared from database!")


@run_async
def last_fm(bot: Bot, update: Update):
    msg = update.effective_message
    user = update.effective_user.first_name
    user_id = update.effective_user.id
    username = sql.get_user(user_id)
    now = ""
    recent = ""
    network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY)
    if not username:
        msg.reply_text("Please set your last.fm username first!")
        return
    else:
        try:
            now = network.get_user(username).get_now_playing()
        except pylast.WSError as e:
            msg.reply_text(str(e))
    if now != "" and now != None:
        loved = now.get_userloved()
        try:
            image = now.get_cover_image()
        except IndexError:
            image = None
        if image:
            rep = f"{user} is now listening to:\n🎧  <code>{now}</code><a href='{image}'>\u200c</a>"
        else:
            rep = f"{user} is now listening to:\n🎧  <code>{now}</code>"
        if loved:
            rep += " (♥️loved)"
        msg.reply_text(rep, parse_mode=ParseMode.HTML)
    else:
        try:
            fmuser = network.get_user(username)
            scrobbles = fmuser.get_playcount()
            recent = fmuser.get_recent_tracks(limit=3)
        except pylast.WSError as e:
            msg.reply_text(str(e))
        if recent != "" and recent != []:
            message = f"{user} was listening to:\n"
            for track in recent:
                message += f"🎧  <code>{track.track}</code>\n"
            message += f"(<code>{scrobbles}</code> scrobbles so far)"
            msg.reply_text(message, parse_mode=ParseMode.HTML)
        elif recent == []:
            msg.reply_text("You don't seem to have scrobbled any songs...")
            
__help__ = """
Share what you're what listening to with the help of this module!

*Available commands:*
 - /setuser <username>: sets your last.fm username.
 - /clearuser: removes your last.fm username from the bot's database.
 - /last: returns what you're scrobbling on last.fm.
"""

__mod_name__ = "Last.FM"
		
SET_USER_HANDLER = CommandHandler("setuser", set_user, pass_args=True)
CLEAR_USER_HANDLER = CommandHandler("clearuser", clear_user)
LAST_FM_HANDLER = DisableAbleCommandHandler("last", last_fm)

dispatcher.add_handler(SET_USER_HANDLER)
dispatcher.add_handler(CLEAR_USER_HANDLER)
dispatcher.add_handler(LAST_FM_HANDLER)