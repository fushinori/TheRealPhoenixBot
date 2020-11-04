import re
import telegram.ext as tg
from telegram import Update
import tg_bot.modules.sql.blacklistusers_sql as sql
from tg_bot import DEV_USERS, SUDO_USERS
from pyrate_limiter import (BucketFullException, Duration, RequestRate, Limiter,
                            MemoryListBucket)

CMD_STARTERS = ('/', '!')

class AntiSpam:

    def __init__(self):
        self.whitelist = (list(SUDO_USERS) or []) + (list(DEV_USERS) or [])
        #Values are HIGHLY experimental, its recommended you pay attention to our commits as we will be adjusting the values over time with what suits best.
        Duration.CUSTOM = 15  # Custom duration, 15 seconds
        self.sec_limit = RequestRate(6, Duration.CUSTOM)  # 6 / Per 15 Seconds
        self.min_limit = RequestRate(20, Duration.MINUTE)  # 20 / Per minute
        self.hour_limit = RequestRate(100, Duration.HOUR)  # 100 / Per hour
        self.daily_limit = RequestRate(1000, Duration.DAY)  # 1000 / Per day
        self.limiter = Limiter(
            self.sec_limit,
            self.min_limit,
            self.hour_limit,
            self.daily_limit,
            bucket_class=MemoryListBucket)

    def check_user(self, user):
        """
        Return True if user is to be ignored else False
        """
        if user in self.whitelist:
            return False
        try:
            self.limiter.try_acquire(user)
            return False
        except BucketFullException:
            return True


SpamChecker = AntiSpam()

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
                    if command[0].lower() in self.command and command[1].lower() == message.bot.username.lower():
                        if SpamChecker.check_user(update.effective_user.id):
                            return None
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
