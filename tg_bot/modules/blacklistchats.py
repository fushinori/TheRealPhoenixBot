from telegram import Bot, Update
from telegram.ext import MessageHandler, Filters, DispatcherHandlerStop
from telegram.error import TelegramError

from tg_bot import dispatcher, BL_CHATS, LOGGER, OWNER_ID


BL_CHATS_GROUP = -1


def blacklist_chats(bot: Bot, update: Update):
    chat = update.effective_chat
    if not chat.id in BL_CHATS:
        return
    try:
        chat.send_message(
            "This chat has been blacklisted! Head over to @PhoenixSupport to find out why!"
        )
        chat.leave()
        raise DispatcherHandlerStop
    except TelegramError as e:
        LOGGER.error(f"Couldn't leave blacklisted chat: {chat.id} due to:\n{e}")
            
            
BLACKLIST_CHATS_HANDLER = MessageHandler(
    Filters.group,
    blacklist_chats
)

dispatcher.add_handler(
    BLACKLIST_CHATS_HANDLER,
    group=BL_CHATS_GROUP
)