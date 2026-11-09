from smallcaps import to_small_caps
import os
import logging
import random, string
import asyncio
import time
import datetime
import requests
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait, ButtonDataInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, delete_files
from database.users_chats_db import db
from info import STICKERS_IDS, SUPPORT_GROUP, INDEX_CHANNELS, ADMINS, IS_VERIFY, VERIFY_TUTORIAL, VERIFY_EXPIRE, TUTORIAL, SHORTLINK_API, SHORTLINK_URL, AUTH_CHANNEL, DELETE_TIME, SUPPORT_LINK, UPDATES_LINK, LOG_CHANNEL, PICS, PROTECT_CONTENT, IS_STREAM, IS_FSUB, PAYMENT_QR
from utils import get_settings, delayed_delete, get_size, is_subscribed, is_check_admin, get_shortlink, get_verify_status, update_verify_status, save_group_settings, temp, get_readable_time, get_wish, get_seconds

@Client.on_message(filters.command("ask") & filters.incoming) #add your support grp to use this
async def aiRes(_, message):
    if message.chat.id == SUPPORT_GROUP:
        asked = message.text.split(None, 1)[1]
        if not asked:
            return await message.reply(to_small_caps("Ask something after ask command!"))
        thinkStc = await message.reply_sticker(sticker=random.choice(STICKERS_IDS))
        url = f"https://bisal-ai-api.vercel.app/biisal" 
        res = requests.post(url , data={'query' : asked})
        if res.status_code == 200:
            response = res.json().get("response")
            await thinkStc.delete()
            await message.reply(to_small_caps(f"<b>hey {message.from_user.mention()},\n{response.lstrip() if response.startswith(' ') else response}</b>"))
        else:
            await thinkStc.delete()
            await message.reply(to_small_caps("Mausam kharab hai ! Thode der mein try kre !\nor Report to Developer."))
    else:
        btn = [[
            InlineKeyboardButton(to_small_caps('💡 Support Group 💡'), url=SUPPORT_LINK)
        ]]
        await message.reply(to_small_caps(f"<b>hey {message.from_user.mention},\n\nPlease use this command in support group.</b>"), reply_markup=InlineKeyboardMarkup(btn))
        
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    botid = client.me.id
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            username = f'@{message.chat.username}' if message.chat.username else 'Private'
            await client.send_message(LOG_CHANNEL, to_small_caps(script.NEW_GROUP_TXT.format(message.chat.title, message.chat.id, username, total)))       
            await db.add_chat(message.chat.id, message.chat.title)
        wish = get_wish()
        btn = [[
            InlineKeyboardButton(to_small_caps('⚡️ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ⚡️'), url=UPDATES_LINK),
            InlineKeyboardButton(to_small_caps('💡 Support Group 💡'), url=SUPPORT_LINK)
        ]]
        await message.reply(text=to_small_caps(f"<b>ʜᴇʏ {message.from_user.mention}, <i>{wish}</i>\nʜᴏᴡ ᴄᴀɴ ɪ ʜᴇʟᴘ ʏᴏᴜ??</b>"), reply_markup=InlineKeyboardMarkup(btn))
        return 
        
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, to_small_caps(script.NEW_USER_TXT.format(message.from_user.mention, message.from_user.id)))

    verify_status = await get_verify_status(message.from_user.id)
    if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
        await update_verify_status(message.from_user.id, is_verified=False)
    
    if (len(message.command) != 2) or (len(message.command) == 2 and message.command[1] == 'start'):
        buttons = [[
            InlineKeyboardButton(to_small_caps('⤬ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ⤬'), url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton(to_small_caps('🌿 ꜱᴜᴘᴘᴏʀᴛ'), callback_data="my_about"),
                    InlineKeyboardButton(to_small_caps('👤 ᴏᴡɴᴇʀ'), callback_data='my_owner')
                ],[
                    InlineKeyboardButton(to_small_caps('🍁 ғᴇᴀᴛᴜʀᴇs'), callback_data='help'),
                    InlineKeyboardButton(to_small_caps('🔐 ᴘʀᴇᴍɪᴜᴍ'), callback_data='buy_premium')
                ],[
                    InlineKeyboardButton(to_small_caps('💰 ᴇᴀʀɴ ᴍᴏɴᴇʏ ʙʏ ʙᴏᴛ 💰'), callback_data='earn')
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=to_small_caps(script.START_TXT.format(message.from_user.mention, get_wish())),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return


    mc = message.command[1]

    if mc.startswith('verify'):
        _, token = mc.split("_", 1)
        verify_status = await get_verify_status(message.from_user.id)
        if verify_status['verify_token'] != token:
            return await message.reply(to_small_caps("Your verify token is invalid."))
        await update_verify_status(message.from_user.id, is_verified=True, verified_time=time.time())
        if verify_status["link"] == "":
            reply_markup = None
        else:
            btn = [[
                InlineKeyboardButton(to_small_caps("📌 Get File 📌"), url=f'https://t.me/{temp.U_NAME}?start={verify_status["link"]}')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
        await message.reply(to_small_caps(f"✅ You successfully verified until: {get_readable_time(VERIFY_EXPIRE)}"), reply_markup=reply_markup, protect_content=True)
        return
    
    verify_status = await get_verify_status(message.from_user.id)
    if not await db.has_premium_access(message.from_user.id):
        if IS_VERIFY and not verify_status['is_verified']:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await update_verify_status(message.from_user.id, verify_token=token, link="" if mc == 'inline_verify' else mc)
            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://t.me/{temp.U_NAME}?start=verify_{token}')
            btn = [[
                InlineKeyboardButton(to_small_caps("🧿 Verify 🧿"), url=link)
            ],[
                InlineKeyboardButton(to_small_caps('🗳 Tutorial 🗳'), url=VERIFY_TUTORIAL)
            ]]
            await message.reply(to_small_caps("You not verified today! Kindly verify now. 🔐"), reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
            return
    else:
        pass

    settings = await get_settings(int(mc.split("_", 2)[1]))
    if settings.get('is_fsub', IS_FSUB):
        btn = await is_subscribed(client, message, settings['fsub'])
        if btn:
            btn.append(
                [InlineKeyboardButton(to_small_caps("🔁 Try Again 🔁"), callback_data=f"checksub#{mc}")]
            )
            reply_markup = InlineKeyboardMarkup(btn)
            await message.reply_photo(
                photo=random.choice(PICS),
                caption=to_small_caps(f"👋 Hello {message.from_user.mention},\n\nPlease join my 'Updates Channel' and try again. 😇"),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return 
        
    if mc.startswith('all'):
        _, grp_id, key = mc.split("_", 2)
        files = temp.FILES.get(key)
        if not files:
            return await message.reply(to_small_caps('No Such All Files Exist!'))
        settings = await get_settings(int(grp_id))
        for file in files:
            CAPTION = settings['caption']
            f_caption = CAPTION.format(
                file_name = file.file_name,
                file_size = get_size(file.file_size),
                file_caption=file.caption
            )   
            if settings.get('is_stream', IS_STREAM):
                btn = [[
                    InlineKeyboardButton(to_small_caps("✛ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ ✛"), callback_data=f"stream#{file.file_id}")
                ],[
                    InlineKeyboardButton(to_small_caps('⚡️ ᴜᴘᴅᴀᴛᴇs ⚡️'), url=UPDATES_LINK),
                    InlineKeyboardButton(to_small_caps('💡 ꜱᴜᴘᴘᴏʀᴛ 💡'), url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton(to_small_caps('⁉️ ᴄʟᴏsᴇ ⁉️'), callback_data='close_data')
                ]]
            else:
                btn = [[
                    InlineKeyboardButton(to_small_caps('⚡️ ᴜᴘᴅᴀᴛᴇs ⚡️'), url=UPDATES_LINK),
                    InlineKeyboardButton(to_small_caps('💡 ꜱᴜᴘᴘᴏʀᴛ 💡'), url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton(to_small_caps('⁉️ ᴄʟᴏsᴇ ⁉️'), callback_data='close_data')
                ]]
            sent_message = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file.file_id,
                caption=f_caption,
                protect_content=settings['file_secure'],
                reply_markup=InlineKeyboardMarkup(btn)
            )
            asyncio.create_task(delayed_delete(client, sent_message, 600))
        await message.reply(to_small_caps("<b>This file will be deleted after 10 min so please forward it in your saved messages.</b>"))                                   
        return

    type_, grp_id, file_id = mc.split("_", 2)
    files_ = await get_file_details(file_id)
    if not files_:
        return await message.reply(to_small_caps('No Such File Exist!'))
    files = files_[0]
    settings = await get_settings(int(grp_id))
    if type_ != 'shortlink' and settings['shortlink']:
        if not await db.has_premium_access(message.from_user.id):
            link = await get_shortlink(settings['url'], settings['api'], f"https://t.me/{temp.U_NAME}?start=shortlink_{grp_id}_{file_id}")
            btn = [[
                InlineKeyboardButton(to_small_caps("♻️ Get File ♻️"), url=link)
            ],[
                InlineKeyboardButton(to_small_caps("📍 ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ 📍"), url=settings['tutorial'])
            ]]
            await message.reply(to_small_caps(f"[{get_size(files.file_size)}] {files.file_name}\n\nYour file is ready, Please get using this link. 👍"), reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
            return
    else:
        pass
        
    CAPTION = settings['caption']
    f_caption = CAPTION.format(
        file_name = files.file_name,
        file_size = get_size(files.file_size),
        file_caption=files.caption
    )
    if settings.get('is_stream', IS_STREAM):
        btn = [[
            InlineKeyboardButton(to_small_caps("✛ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ ✛"), callback_data=f"stream#{file_id}")
        ],[
            InlineKeyboardButton(to_small_caps('⚡️ ᴜᴘᴅᴀᴛᴇs ⚡️'), url=UPDATES_LINK),
            InlineKeyboardButton(to_small_caps('💡 ꜱᴜᴘᴘᴏʀᴛ 💡'), url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton(to_small_caps('⁉️ ᴄʟᴏsᴇ ⁉️'), callback_data='close_data')
        ]]
    else:
        btn = [[
            InlineKeyboardButton(to_small_caps('⚡️ ᴜᴘᴅᴀᴛᴇs ⚡️'), url=UPDATES_LINK),
            InlineKeyboardButton(to_small_caps('💡 ꜱᴜᴘᴘᴏʀᴛ 💡'), url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton(to_small_caps('⁉️ ᴄʟᴏsᴇ ⁉️'), callback_data='close_data')
        ]]
    sent_message = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=settings['file_secure'],
        reply_markup=InlineKeyboardMarkup(btn)
    )
    await sent_message.reply(to_small_caps("<b>This file will be deleted after 10 min so please forward it in your saved messages.</b>"))
    asyncio.create_task(delayed_delete(client, sent_message, 600))

@Client.on_message(filters.command('index_channels') & filters.user(ADMINS))
async def channels_info(bot, message):
    """Send basic information of index channels"""
    ids = INDEX_CHANNELS
    if not ids:
        return await message.reply(to_small_caps("Not set INDEX_CHANNELS"))

    text = '**Indexed Channels:**\n\n'
    for id in ids:
        chat = await bot.get_chat(id)
        text += f'{chat.title}\n'
    text += f'\n**Total:** {len(ids)}'
    await message.reply(to_small_caps(text))

@Client.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot, message):
    msg = await message.reply(to_small_caps('Please Wait...'))
    files = await Media.count_documents()
    users = await db.total_users_count()
    chats = await db.total_chat_count()
    u_size = get_size(await db.get_db_size())
    f_size = get_size(536870912 - await db.get_db_size())
    uptime = get_readable_time(time.time() - temp.START_TIME)
    await msg.edit(to_small_caps(script.STATUS_TXT.format(files, users, chats, u_size, f_size, uptime)))    
    
@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(to_small_caps("<b>You are Anonymous admin you can't use this command !</b>"))
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text(to_small_caps("Use this command in group."))
    grp_id = message.chat.id
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text(to_small_caps('You not admin in this group.'))
    settings = await get_settings(grp_id)
    if settings is not None:
        buttons = [[
            InlineKeyboardButton(to_small_caps('Auto Filter'), callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}'),
            InlineKeyboardButton(to_small_caps('✅ Yes' if settings["auto_filter"] else '❌ No'), callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}')
        ],[
            InlineKeyboardButton(to_small_caps('File Secure'), callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}'),
            InlineKeyboardButton(to_small_caps('✅ Yes' if settings["file_secure"] else '❌ No'), callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}')
        ],[
            InlineKeyboardButton(to_small_caps('IMDb Poster'), callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}'),
            InlineKeyboardButton(to_small_caps('✅ Yes' if settings["imdb"] else '❌ No'), callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}')
        ],[
            InlineKeyboardButton(to_small_caps('Spelling Check'), callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}'),
            InlineKeyboardButton(to_small_caps('✅ Yes' if settings["spell_check"] else '❌ No'), callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}')
        ],[
            InlineKeyboardButton(to_small_caps('Auto Delete'), callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}'),
            InlineKeyboardButton(to_small_caps(f'{get_readable_time(DELETE_TIME)}' if settings["auto_delete"] else '❌ No'), callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}')
        ],[
            InlineKeyboardButton(to_small_caps('Welcome'), callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',),
            InlineKeyboardButton(to_small_caps('✅ Yes' if settings["welcome"] else '❌ No'), callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}'),
        ],[
            InlineKeyboardButton(to_small_caps('Shortlink'), callback_data=f'setgs#shortlink#{settings["shortlink"]}#{grp_id}'),
            InlineKeyboardButton(to_small_caps('✅ Yes' if settings["shortlink"] else '❌ No'), callback_data=f'setgs#shortlink#{settings["shortlink"]}#{grp_id}'),
        ],[
            InlineKeyboardButton(to_small_caps('Result Page'), callback_data=f'setgs#links#{settings["links"]}#{str(grp_id)}'),
            InlineKeyboardButton(to_small_caps('⛓ Link' if settings["links"] else '🧲 Button'), callback_data=f'setgs#links#{settings["links"]}#{str(grp_id)}')
        ],[
            InlineKeyboardButton(to_small_caps('Fsub'), callback_data=f'setgs#is_fsub#{settings.get("is_fsub", IS_FSUB)}#{str(grp_id)}'),
            InlineKeyboardButton(to_small_caps('✅ On' if settings.get("is_fsub", IS_FSUB) else '❌ Off'), callback_data=f'setgs#is_fsub#{settings.get("is_fsub", IS_FSUB)}#{str(grp_id)}')
        ],[
            InlineKeyboardButton(to_small_caps('Stream'), callback_data=f'setgs#is_stream#{settings.get("is_stream", IS_STREAM)}#{str(grp_id)}'),
            InlineKeyboardButton(to_small_caps('✅ On' if settings.get("is_stream", IS_STREAM) else '❌ Off'), callback_data=f'setgs#is_stream#{settings.get("is_stream", IS_STREAM)}#{str(grp_id)}')
        ],[
            InlineKeyboardButton(to_small_caps('❌ Close ❌'), callback_data='close_data')
        ]]
        await message.reply_text(
            text=to_small_caps(f"Change your settings for <b>'{message.chat.title}'</b> as your wish. ⚙"),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await message.reply_text(to_small_caps('Something went wrong!'))

@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(to_small_caps("<b>You are Anonymous admin you can't use this command !</b>"))
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text(to_small_caps("Use this command in group."))      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text(to_small_caps('You not admin in this group.'))
    try:
        template = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(to_small_caps("Command Incomplete!"))   
    await save_group_settings(grp_id, 'template', template)
    await message.reply_text(to_small_caps(f"Successfully changed template for {title} to\n\n{template}"))  
    
@Client.on_message(filters.command('set_caption'))
async def save_caption(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(to_small_caps("<b>You are Anonymous admin you can't use this command !</b>"))
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text(to_small_caps("Use this command in group."))      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text(to_small_caps('You not admin in this group.'))
    try:
        caption = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(to_small_caps("Command Incomplete!")) 
    await save_group_settings(grp_id, 'caption', caption)
    await message.reply_text(to_small_caps(f"Successfully changed caption for {title} to\n\n{caption}"))
        
@Client.on_message(filters.command('set_shortlink'))
async def save_shortlink(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(to_small_caps("<b>You are Anonymous admin you can't use this command !</b>"))
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text(to_small_caps("Use this command in group."))    
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text(to_small_caps('You not admin in this group.'))
    try:
        _, url, api = message.text.split(" ", 2)
    except:
        return await message.reply_text(to_small_caps("<b>Command Incomplete:-\n\ngive me a shortlink & api along with the command...\n\nEx:- <code>/shortlink mdisklink.link 5843c3cc645f5077b2200a2c77e0344879880b3e</code>"))   
    try:
        await get_shortlink(url, api, f'https://t.me/{temp.U_NAME}')
    except:
        return await message.reply_text(to_small_caps("Your shortlink API or URL invalid, Please Check again!"))   
    await save_group_settings(grp_id, 'url', url)
    await save_group_settings(grp_id, 'api', api)
    await message.reply_text(to_small_caps(f"Successfully changed shortlink for {title} to\n\nURL - {url}\nAPI - {api}"))
    
@Client.on_message(filters.command('get_custom_settings'))
async def get_custom_settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(to_small_caps("<b>You are Anonymous admin you can't use this command !</b>"))
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text(to_small_caps("Use this command in group."))
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text(to_small_caps('You not admin in this group...'))    
    settings = await get_settings(grp_id)
    text = f"""Custom settings for: {title}

Shortlink URL: {settings["url"]}
Shortlink API: {settings["api"]}

IMDb Template: {settings['template']}

File Caption: {settings['caption']}

Welcome Text: {settings['welcome_text']}

Tutorial Link: {settings['tutorial']}

Force Channels: {str(settings['fsub'])[1:-1] if settings['fsub'] else 'Not Set'}"""

    btn = [[
        InlineKeyboardButton(text=to_small_caps("Close"), callback_data="close_data")
    ]]
    await message.reply_text(to_small_caps(text), reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)

@Client.on_message(filters.command('set_welcome'))
async def save_welcome(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(to_small_caps("<b>You are Anonymous admin you can't use this command !</b>"))
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text(to_small_caps("Use this command in group."))      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text(to_small_caps('You not admin in this group.'))
    try:
        welcome = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(to_small_caps("Command Incomplete!"))    
    await save_group_settings(grp_id, 'welcome_text', welcome)
    await message.reply_text(to_small_caps(f"Successfully changed welcome for {title} to\n\n{welcome}"))
        
@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete_file(bot, message):
    try:
        query = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(to_small_caps("Command Incomplete!\nUsage: /delete query"))
    msg = await message.reply_text(to_small_caps('Searching...'))
    total, files = await delete_files(query)
    if int(total) == 0:
        return await msg.edit(to_small_caps('Not have files in your query'))
    btn = [[
        InlineKeyboardButton(to_small_caps("YES"), callback_data=f"delete_{query}")
    ],[
        InlineKeyboardButton(to_small_caps("CLOSE"), callback_data="close_data")
    ]]
    await msg.edit(to_small_caps(f"Total {total} files found in your query {query}.\n\nDo you want to delete?"), reply_markup=InlineKeyboardMarkup(btn))
 
@Client.on_message(filters.command('delete_all') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    btn = [[
        InlineKeyboardButton(text=to_small_caps("YES"), callback_data="delete_all")
    ],[
        InlineKeyboardButton(text=to_small_caps("CLOSE"), callback_data="close_data")
    ]]
    files = await Media.count_documents()
    if int(files) == 0:
        return await message.reply_text(to_small_caps('Not have files to delete'))
    await message.reply_text(to_small_caps(f'Total {files} files have.\nDo you want to delete all?'), reply_markup=InlineKeyboardMarkup(btn))

@Client.on_message(filters.command('set_tutorial'))
async def set_tutorial(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(to_small_caps("<b>You are Anonymous admin you can't use this command !</b>"))
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text(to_small_caps("Use this command in group."))       
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text(to_small_caps('You not admin in this group.'))
    try:
        tutorial = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(to_small_caps("Command Incomplete!"))   
    await save_group_settings(grp_id, 'tutorial', tutorial)
    await message.reply_text(to_small_caps(f"Successfully changed tutorial for {title} to\n\n{tutorial}"))

@Client.on_message(filters.command('set_fsub'))
async def set_fsub(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(to_small_caps("<b>You are Anonymous admin you can't use this command !</b>"))
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text(to_small_caps("Use this command in group."))      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text(to_small_caps('You not admin in this group.'))
    vp = message.text.split(" ", 1)[1]
    if vp.lower() in ["Off", "off", "False", "false", "Turn Off", "turn off"]:
        await save_group_settings(grp_id, 'is_fsub', False)
        return await message.reply_text(to_small_caps("Successfully Turned Off !"))
    elif vp.lower() in ["On", "on", "True", "true", "Turn On", "turn on"]:
        await save_group_settings(grp_id, 'is_fsub', True)
        return await message.reply_text(to_small_caps("Successfully Turned On !"))
    try:
        ids = message.text.split(" ", 1)[1]
        fsub_ids = list(map(int, ids.split()))
    except IndexError:
        return await message.reply_text(to_small_caps("Command Incomplete!\n\nCan multiple channel add separate by spaces. Like: /set_fsub id1 id2 id3"))
    except ValueError:
        return await message.reply_text(to_small_caps('Make sure ids is integer.'))        
    channels = "Channels:\n"
    for id in fsub_ids:
        try:
            chat = await client.get_chat(id)
        except Exception as e:
            return await message.reply_text(to_small_caps(f"{id} is invalid!\nMake sure this bot admin in that channel.\n\nError - {e}"))
        if chat.type != enums.ChatType.CHANNEL:
            return await message.reply_text(to_small_caps(f"{id} is not channel."))
        channels += f'{chat.title}\n'
    await save_group_settings(grp_id, 'fsub', fsub_ids)
    await message.reply_text(to_small_caps(f"Successfully set force channels for {title} to\n\n{channels}"))

@Client.on_message(filters.command('ping'))
async def ping(client, message):
    start_time = time.monotonic()
    msg = await message.reply(to_small_caps("👀"))
    end_time = time.monotonic()
    await msg.edit(to_small_caps(f'{round((end_time - start_time) * 1000)} ms'))
    
@Client.on_message(filters.command("add_premium"))
async def give_premium_cmd_handler(client, message):
    if message.from_user.id not in ADMINS:
        return
    if len(message.command) == 3:
        user_id = int(message.command[1])  # Convert the user_id to integer
        time = message.command[2]        
        seconds = await get_seconds(time)
        if seconds > 0:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            user_data = {"id": user_id, "expiry_time": expiry_time} 
            await db.update_user(user_data)  # Use the update_user method to update or insert user data
            await message.reply_text(to_small_caps("Premium access added to the user."))
            
            await client.send_message(
                chat_id=user_id,
                text=to_small_caps(f"<b>ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ꜰᴏʀ {time} ᴇɴᴊᴏʏ 😀\n</b>"),                
            )
        else:
            await message.reply_text(to_small_caps("Invalid time format. Please use '1day for days', '1hour for hours', or '1min for minutes', or '1month for months' or '1year for year'"))
    else:
        await message.reply_text(to_small_caps("<b>Usage: /add_premium user_id time \n\nExample /add_premium 1252789 10day \n\n(e.g. for time units '1day for days', '1hour for hours', or '1min for minutes', or '1month for months' or '1year for year')</b>"))
        
@Client.on_message(filters.command("remove_premium"))
async def remove_premium_cmd_handler(client, message):
    if message.from_user.id not in ADMINS:
        return
    if len(message.command) == 2:
        user_id = int(message.command[1])  # Convert the user_id to integer
      #  time = message.command[2]
        time = "1s"
        seconds = await get_seconds(time)
        if seconds > 0:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            user_data = {"id": user_id, "expiry_time": expiry_time}  # Using "id" instead of "user_id"
            await db.update_user(user_data)  # Use the update_user method to update or insert user data
            await message.reply_text(to_small_caps("Premium access removed to the user."))
            await client.send_message(
                chat_id=user_id,
                text=to_small_caps(f"<b>premium removed by admins \n\n Contact Admin if this is mistake \n\n 👮 Admin : @Rk_botowner \n</b>"),                
            )
        else:
            await message.reply_text(to_small_caps("Invalid time format.'"))
    else:
        await message.reply_text(to_small_caps("Usage: /remove_premium user_id"))
        
@Client.on_message(filters.command("plans"))
async def plans_cmd_handler(client, message):                
    btn = [            
        [InlineKeyboardButton(to_small_caps("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾"), url="t.me/Rk_botowner")],
        [InlineKeyboardButton(to_small_caps("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️"), callback_data="close_data")]
    ]
    reply_markup = InlineKeyboardMarkup(btn)
    await message.reply_photo(
        photo=PAYMENT_QR,
        caption=to_small_caps("**Pʀᴇᴍɪᴜᴍ Fᴇᴀᴛᴜʀᴇs 🎁\n\n☆ No Need To Verify\n☆ Ad Free Experience\n☆ Unlimited Movie And Series"),
        reply_markup=reply_markup
    )
        
@Client.on_message(filters.command("my_plan"))
async def check_plans_cmd(client, message):
    user_id  = message.from_user.id
    if await db.has_premium_access(user_id):         
        remaining_time = await db.check_remaining_uasge(user_id)             
        expiry_time = remaining_time + datetime.datetime.now()
        await message.reply_text(to_small_caps(f"**Your plans details are :\n\nRemaining Time : {remaining_time}\n\nExpirytime : {expiry_time}**"))
    else:
        btn = [ 
            [InlineKeyboardButton(to_small_caps("ɢᴇᴛ ғʀᴇᴇ ᴛʀᴀɪʟ ғᴏʀ 𝟻 ᴍɪɴᴜᴛᴇꜱ ☺️"), callback_data="get_trail")],
            [InlineKeyboardButton(to_small_caps("ʙᴜʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ : ʀᴇᴍᴏᴠᴇ ᴀᴅs"), callback_data="buy_premium")],
            [InlineKeyboardButton(to_small_caps("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️"), callback_data="close_data")]
        ]
        reply_markup = InlineKeyboardMarkup(btn)
        m=await message.reply_sticker("CAACAgIAAxkBAAIBTGVjQbHuhOiboQsDm35brLGyLQ28AAJ-GgACglXYSXgCrotQHjibHgQ")         
        await message.reply_text(to_small_caps(f"**😢 You Don't Have Any Premium Subscription.\n\n Check Out Our Premium /plans**"),reply_markup=reply_markup)
        await asyncio.sleep(2)
        await m.delete()