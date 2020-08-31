import re
import telegram.ext as tg
from telegram import Update
import tg_bot.modules.sql.blacklistusers_sql as sql

CMD_STARTERS = ('/', '!')


class CustomCommandHandler(tg.CommandHandler):
    def __init__(self, command, callback, **kwargs):
        if "admin_ok" in kwargs:
            del kwargs["admin_ok"]
        super().__init__(command, callback, **kwargs)

    def check_update(self, update):
        if (isinstance(update, Update)
                and (update.message or update.edited_message and self.allow_edited)):
            message = update.message or update.edited_message
            if update.effective_user:
                if sql.is_user_blacklisted(update.effective_user.id):
                    return False

            if message.text and len(message.text) > 1:
                fst_word = message.text_html.split(None, 1)[0]
                if len(fst_word) > 1 and any(fst_word.startswith(start) for start in CMD_STARTERS):
                    command = fst_word[1:].split('@')
                    command.append(message.bot.username)  # in case the command was sent without a username
                    if self.filters is None:
                        res = True
                    elif isinstance(self.filters, list):
                        res = any(func(message) for func in self.filters)
                    else:
                        res = self.filters(message)

                    return res and (command[0].lower() in self.command
                                    and command[1].lower() == message.bot.username.lower())

            return False


class CustomRegexHandler(tg.RegexHandler):
    def __init__(self, pattern, callback, friendly="", **kwargs):
        super().__init__(pattern, callback, **kwargs)

    def check_update(self, update):
        if isinstance(update, Update) and update.effective_message:
            if update.effective_user:
                if sql.is_user_blacklisted(update.effective_user.id):
                    return False
        else:
            return False
        if any([self.message_updates and update.message,
                    self.edited_updates and (update.edited_message or update.edited_channel_post),
                    self.channel_post_updates and update.channel_post]) and \
                    update.effective_message.text:
                match = re.match(self.pattern, update.effective_message.text)
                return bool(match)
        return False


class CustomMessageHandler(tg.MessageHandler):
    def __init__(self, filters, callback, **kwargs):
        super().__init__(filters, callback, **kwargs)
        
    def check_update(self, update):
        if isinstance(update, Update) and self._is_allowed_update(update):
            if update.effective_user:
                if sql.is_user_blacklisted(update.effective_user.id):
                    return False
            if self.filters is None:
                res = True
                
            else:
                message = update.effective_message
                if isinstance(self.filters, list):
                    res = any(func(message) for func in self.filters)
                else:
                    res = self.filters(message)
                    
        else:
            res = False
            
        return res
