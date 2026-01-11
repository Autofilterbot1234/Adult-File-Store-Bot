# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import requests
import string
import random
from configs import Config
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from handlers.helpers import str_to_b64
from handlers.database import db # ডাটাবেস ইম্পোর্ট করা হলো

# সময় সুন্দর করে দেখানোর জন্য ছোট ফাংশন
def get_readable_time(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds} Seconds"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes} Minutes"
    hours, min = divmod(minutes, 60)
    return f"{hours} Hours"

async def reply_forward(message: Message, file_id: int):
    try:
        # ডাটাবেস থেকে ডিলিট টাইম চেক করা হচ্ছে
        delete_time = await db.get_auto_delete_time()
        
        # যদি টাইম ০ হয়, তার মানে অটো ডিলিট অফ, তাই মেসেজ দেওয়ার দরকার নেই
        if delete_time == 0:
            return

        readable_time = get_readable_time(delete_time)
        
        await message.reply_text(
            f"⚠️ **Note:** This file will be deleted automatically in **{readable_time}** to avoid copyright issues. Please save it now!",
            disable_web_page_preview=True,
            quote=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await reply_forward(message, file_id)

async def media_forward(bot: Client, user_id: int, file_id: int):
    try:
        # ডাটাবেস থেকে ফরোয়ার্ড রেস্ট্রিকশন স্ট্যাটাস চেক করা হচ্ছে
        is_protected = await db.get_protect_content()

        if is_protected:
            # যদি প্রোটেকশন অন থাকে, তবে অবশ্যই copy_message ব্যবহার করতে হবে এবং protect_content=True দিতে হবে
            return await bot.copy_message(
                chat_id=user_id, 
                from_chat_id=Config.DB_CHANNEL,
                message_id=file_id,
                protect_content=True
            )
        elif Config.FORWARD_AS_COPY is True:
            return await bot.copy_message(
                chat_id=user_id, 
                from_chat_id=Config.DB_CHANNEL,
                message_id=file_id
            )
        else:
            return await bot.forward_messages(
                chat_id=user_id, 
                from_chat_id=Config.DB_CHANNEL,
                message_ids=file_id
            )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await media_forward(bot, user_id, file_id)

async def send_media_and_reply(bot: Client, user_id: int, file_id: int):
    sent_message = await media_forward(bot, user_id, file_id)
    
    if sent_message:
        await reply_forward(message=sent_message, file_id=file_id)
        
        # অটো ডিলিট লজিক
        delete_time = await db.get_auto_delete_time()
        if delete_time > 0:
            asyncio.create_task(delete_after_delay(sent_message, delete_time))

async def delete_after_delay(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass
