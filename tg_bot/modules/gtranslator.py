from gpytranslate import Translator
from pyrogram import filters
from pyrogram.types import Message

from tg_bot import pg


trans = Translator()

LANG_CODES = [
    'af', 'sq', 'am', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs',
    'bg', 'ca', 'ceb', 'ny', 'zh-cn', 'zh-tw', 'co', 'hr', 'cs', 'da', 'nl',
    'en', 'eo', 'et', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gu',
    'ht', 'ha', 'haw', 'iw', 'he', 'hi', 'hmn', 'hu', 'is', 'ig', 'id', 'ga',
    'it', 'ja', 'jw', 'kn', 'kk', 'km', 'ko', 'ku', 'ky', 'lo', 'la', 'lv',
    'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn', 'my', 'ne',
    'no', 'or', 'ps', 'fa', 'pl', 'pt', 'pa', 'ro', 'ru', 'sm', 'gd', 'sr',
    'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg',
    'ta', 'te', 'th', 'tr', 'uk', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi',
    'yo', 'zu']


@pg.on_message(filters.command(["tl", "tr"]))
async def translate(_, message: Message) -> None:
    reply_msg = message.reply_to_message
    if not reply_msg:
        await message.reply_text("Reply to a message to translate it!")
        return
    try:
        args = message.text.split()[1].lower()
        if "//" in args:
            source = args.split("//")[0]
            dest = args.split("//")[1]
        else:
            source = await trans.detect(reply_msg.text)
            dest = args
    except IndexError:
        source = await trans.detect(reply_msg.text)
        dest = "en"
    if not (source in LANG_CODES and dest in LANG_CODES):
        await message.reply_text("Invalid language codes provided!")
        return
    translation = await trans(reply_msg.text,
                              sourcelang=source, targetlang=dest)
    reply = f"<b>Translated from {source} to {dest}</b>:\n" \
        f"<code>{translation.text}</code>"

    await message.reply_text(reply, parse_mode="html")


__mod_name__ = "Translation"

__help__ = """
Use this module to translate stuff... duh!

**Commands:**
• `/tr` or `/tl`: as a reply to a message, translates it!
Additional arguments you can use:
You can provide a destination language or both a \
source and destination language separated by //
Example: `/tl en` or `/tl en//ja`. The second example will translate \
text from English to Japanese."""
