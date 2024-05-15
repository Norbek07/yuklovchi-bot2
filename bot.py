from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command
from aiogram.utils.chat_action import ChatActionSender
from aiogram import F
from aiogram.types import Message,InlineKeyboardButton,InputMediaPhoto,InputMediaVideo
from data import config
import asyncio
import logging
import sys
from menucommands.set_bot_commands  import set_default_commands
from baza.sqlite import Database
from filters.admin import IsBotAdminFilter
from filters.check_sub_channel import IsCheckSubChannels
from keyboard_buttons import admin_keyboard
from aiogram.fsm.context import FSMContext #new
from states.reklama import Adverts
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time 
from instasaves import get_insta

ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS

dp = Dispatcher()




@dp.message(CommandStart())
async def start_command(message:Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name,telegram_id=telegram_id) #foydalanuvchi bazaga qo'shildi
        await message.answer(text="Assalomu alaykum, Bu bot Instagram link orqali video va rasmlarni yuklab beradi.")
    except:
        await message.answer(text="Bu bot Instagram link orqali video va rasmlarni yuklab beradi.")
#e22bb6f141mshb5df187325fcfe1p122f8djsn1231cff01bb2
@dp.message(F.text)
async def save_insta(message:Message):
    link = message.text
    natija = get_insta(link)

    if natija.get("status"):
        await bot.send_chat_action(chat_id=message.from_user.id,action="typing")
        await message.answer(text="Yuborilyapti....")
        if natija.get("result").get("is_video"):
            await bot.send_chat_action(chat_id=message.from_user.id,action="upload_video")
            video = natija.get("result").get("video_url")
            caption = natija.get("result").get("caption")
            if caption:
                await message.answer_video(video=video,caption=caption)
            else:
                await message.answer_video(video=video)
        elif natija.get("result").get("is_album"):
            await bot.send_chat_action(chat_id=message.from_user.id,action="upload_document")
            albom = natija.get("album")
            print(albom)
            media = []
            caption = natija.get("result").get("caption")
            for index,i in enumerate(albom):
                if i.get("FileType") == 'image':
                    if index == 0 and caption:

                        media.append(InputMediaPhoto(media=i.get("url"),caption=caption))
                    else:  
                        media.append(InputMediaPhoto(media=i.get("url")))
 
                else:
                    if index == 0 and caption:

                        media.append(InputMediaVideo(media=i.get("url"),caption=caption))
                    else:  
                        media.append(InputMediaVideo(media=i.get("url")))
            
            if caption:
                await message.answer_media_group(media=media)
            else:
                await message.answer_media_group(media=media)

        else:
            await bot.send_chat_action(chat_id=message.from_user.id,action="upload_photo")
            rasm = natija.get("result").get("image_url")
            caption = natija.get("result").get("caption")
            if caption:
                await message.answer_photo(photo=rasm,caption=caption)
            else:
                await message.answer_photo(photo=rasm)
            
    elif natija.get("message").startswith("You have exceeded the MONTHLY quota"):
        await message.answer(text="Tez orada ishga tushiramiz....")
    else:
        await message.answer(text="Notog'ri link yubordingiz, instagram saytidan link yuboring!")


@dp.message(IsCheckSubChannels())
async def kanalga_obuna(message:Message):
    text = ""
    inline_channel = InlineKeyboardBuilder()
    for index,channel in enumerate(CHANNELS):
        ChatInviteLink = await bot.create_chat_invite_link(channel)
        inline_channel.add(InlineKeyboardButton(text=f"{index+1}-kanal",url=ChatInviteLink.invite_link))
    inline_channel.adjust(1,repeat=True)
    button = inline_channel.as_markup()
    await message.answer(f"{text} kanallarga azo bo'ling",reply_markup=button)



#help commands
@dp.message(Command("help"))
async def help_commands(message:Message):
    await message.answer("Sizga qanday yordam kerak")



#about commands
@dp.message(Command("about"))
async def about_commands(message:Message):
    await message.answer("Sifat 2024")


@dp.message(Command("admin"),IsBotAdminFilter(ADMINS))
async def is_admin(message:Message):
    await message.answer(text="Admin menu",reply_markup=admin_keyboard.admin_button)


@dp.message(F.text=="Foydalanuvchilar soni",IsBotAdminFilter(ADMINS))
async def users_count(message:Message):
    counts = db.count_users()
    text = f"Botimizda {counts[0]} ta foydalanuvchi bor"
    await message.answer(text=text)

@dp.message(F.text=="Reklama yuborish",IsBotAdminFilter(ADMINS))
async def advert_dp(message:Message,state:FSMContext):
    await state.set_state(Adverts.adverts)
    await message.answer(text="Reklama yuborishingiz mumkin !")

@dp.message(Adverts.adverts)
async def send_advert(message:Message,state:FSMContext):
    
    message_id = message.message_id
    from_chat_id = message.from_user.id
    users = db.all_users_id()
    count = 0
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0],from_chat_id=from_chat_id,message_id=message_id)
            count += 1
        except:
            pass
        time.sleep(0.01)
    
    await message.answer(f"Reklama {count}ta foydalanuvchiga yuborildi")
    await state.clear()


@dp.startup()
async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishga tushdi")
        except Exception as err:
            logging.exception(err)

#bot ishga tushganini xabarini yuborish
@dp.shutdown()
async def off_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishdan to'xtadi!")
        except Exception as err:
            logging.exception(err)


def setup_middlewares(dispatcher: Dispatcher, bot: Bot) -> None:
    """MIDDLEWARE"""
    from middlewares.throttling import ThrottlingMiddleware

    # Spamdan himoya qilish uchun klassik ichki o'rta dastur. So'rovlar orasidagi asosiy vaqtlar 0,5 soniya
    dispatcher.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))



async def main() -> None:
    global bot,db
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    db = Database(path_to_db="main.db")
    await set_default_commands(bot)
    await dp.start_polling(bot)
    setup_middlewares(dispatcher=dp, bot=bot)




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())