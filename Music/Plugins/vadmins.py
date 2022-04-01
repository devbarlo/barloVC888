from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from Music import app
from Music.MusicUtilities.tgcallsrun.music import pytgcalls as call_py

from Music.MusicUtilities.helpers.decorators import authorized_users_only
from Music.MusicUtilities.helpers.filters import command
from Music.MusicUtilities.tgcallsrun.queues import QUEUE, clear_queue
from Music.MusicUtilities.tgcallsrun.video import skip_current_song, skip_item


bttn = InlineKeyboardMarkup(
    [[InlineKeyboardButton("↩ - رجوع - ↪", callback_data="cbmenu")]]
)


bcl = InlineKeyboardMarkup([[InlineKeyboardButton("❌ -اخفاء - ❌", callback_data="cls")]])


@Client.on_callback_query(filters.regex("cbmenu"))
async def cbmenu(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer(
            "Anda adalah **Admin Anonim** !\n\n» kembali ke akun pengguna dari hak admin."
        )
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Hanya admin dengan izin mengelola obrolan suara yang dapat mengetuk tombol ini !",
            show_alert=True,
        )
    await query.edit_message_text(
        f"🌝 **أسم المجموعه** {query.message.chat.title}\n\n ⏸ : إيقاف مؤقت\n▶️ : أستمرار المقطع\n🔇 : كتم صوت المقطع\n🔊 : تنشيط صوت المقطع\n⏹ : لإنهاء البث المباشر",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⏹", callback_data="cbstop"),
                    InlineKeyboardButton("⏸", callback_data="cbpause"),
                    InlineKeyboardButton("▶️", callback_data="cbresume"),
                ],
                [
                    InlineKeyboardButton("🔇", callback_data="cbmute"),
                    InlineKeyboardButton("🔊", callback_data="cbunmute"),
                ],
                [InlineKeyboardButton("❌ -اخفاء - ❌", callback_data="cls")],
            ]
        ),
    )


@Client.on_callback_query(filters.regex("cls"))
async def close(_, query: CallbackQuery):
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Hanya admin dengan izin mengelola obrolan suara yang dapat mengetuk tombol ini !",
            show_alert=True,
        )
    await query.message.delete()


@app.on_message(command(["vskip", "skip", "تفاوت"]) & filters.group)
@authorized_users_only
async def skip(client, m: Message):

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="تحكم╎🎥", callback_data="cbmenu"),
            ]
        ]
    )

    chat_id = m.chat.id
    if len(m.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await m.reply("❌ Tidak ada yang sedang diputar")
        elif op == 1:
            await m.reply(
                "✅ __Antrian__ **kosong.**\n\n**• Assistant meninggalkan obrolan suara**"
            )
        elif op == 2:
            await m.reply(
                "🗑️ **Membersihkan Antrian**\n\n**• Assistant meninggalkan obrolan suara**"
            )
        else:
            await m.reply(
                f"""
⏭️ **Memutar {op[2]} selanjutnya**

🎥 **أسم المقطع:** [{op[0]}]({op[1]})
🎧 **أسم المتخطي:** {m.from_user.mention()}
""",
                disable_web_page_preview=True,
                reply_markup=keyboard,
            )
    else:
        skip = m.text.split(None, 1)[1]
        OP = "🗑 **Lagu dihapus dari antrian:**"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        OP = OP + "\n" + f"**#{x}** - {hm}"
            await m.reply(OP)


@app.on_message(command(["/vend", "غلق", "/vstop"]) & filters.group)
@authorized_users_only
async def stop(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await m.reply(" **تم إيقاف الفيديو داخل المحادثه الصوتيه 💁‍♂️**")
        except Exception as e:
            await m.reply(f"**Error:**\n\n`{e}`")
    else:
        await m.reply("❌ **لآ يوجد فيديوهات مشغله أصلا ...**")


@app.on_message(command(["vpause", "انتظار"]) & filters.group)
@authorized_users_only
async def pause(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await m.reply(
                "II **Video dijeda.**\n\n• **Untuk melanjutkan video, gunakan Perintah** » /vresume"
            )
        except Exception as e:
            await m.reply(f"**Error:**\n\n`{e}`")
    else:
        await m.reply("❌ **لآ يوجد فيديوهات مشغله أصلا ...**")


@app.on_message(command(["vresume", "اعاده"]) & filters.group)
@authorized_users_only
async def resume(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await m.reply(
                "▷ **Video dilanjutkan.**\n\n• **Untuk menjeda video, gunakan Perintah** » /vpause"
            )
        except Exception as e:
            await m.reply(f"**Error:**\n\n`{e}`")
    else:
        await m.reply("❌ **لآ يوجد فيديوهات مشغله أصلا ...**")


@app.on_message(command(["vmute", "كتم"]) & filters.group)
@authorized_users_only
async def mute(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.mute_stream(chat_id)
            await m.reply(
                "🔇 **تم كتم المساعد الأن.**\n\n• **لتنشيط صوت المساعد ، استخدم هذا الأمر 👇**\n» الغاء كتم"
            )
        except Exception as e:
            await m.reply(f"**Error:**\n\n`{e}`")
    else:
        await m.reply("❌ **لآ يوجد فيديوهات مشغله أصلا ...**")


@app.on_message(command(["vunmute", "الغاء كتم"]) & filters.group)
@authorized_users_only
async def unmute(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.unmute_stream(chat_id)
            await m.reply(
                "🔊 **تم تنشيط المساعد الأن.**\n\n• **لكتم المساعد مره أخري أستخدم هذا الأمر 👇**\n» كتم الفيديو"
            )
        except Exception as e:
            await m.reply(f"**Error:**\n\n`{e}`")
    else:
        await m.reply("❌ **لآ يوجد فيديوهات مشغله أصلا ...**")


@Client.on_callback_query(filters.regex("cbpause"))
async def cbpause(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer(
            "Anda adalah **Admin Anonim** !\n\n» kembali ke akun pengguna dari hak admin."
        )
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Hanya admin dengan izin mengelola obrolan suara yang dapat mengetuk tombol ini!",
            show_alert=True,
        )
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await query.edit_message_text("تم إيقاف الفيديو مؤقتآ .", reply_markup=bttn)
        except Exception as e:
            await query.edit_message_text(f"**Error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("❌ لا شيء يتدفق الأن", show_alert=True)


@Client.on_callback_query(filters.regex("cbresume"))
async def cbresume(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer(
            "Anda adalah **Admin Anonim** !\n\n» kembali ke akun pengguna dari hak admin."
        )
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Hanya admin dengan izin mengelola obrolan suara yang dapat mengetuk tombol ini !",
            show_alert=True,
        )
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await query.edit_message_text(
                "▷ تم استئناف المقطع . ✅", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"**Error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("❌ لا شيء يتدفق الأن", show_alert=True)


@Client.on_callback_query(filters.regex("cbstop"))
async def cbstop(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer(
            "Anda adalah **Admin Anonim** !\n\n» kembali ke akun pengguna dari hak admin."
        )
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Hanya admin dengan izin mengelola obrolan suara yang dapat mengetuk tombol ini !",
            show_alert=True,
        )
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await query.edit_message_text(
                "✅ **تم إنهاء البث المباشر داخل المحادثه الصوتيه . ✅**", reply_markup=bcl
            )
        except Exception as e:
            await query.edit_message_text(f"**Error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("❌ لا شيء يتدفق الأن", show_alert=True)


@Client.on_callback_query(filters.regex("cbmute"))
async def cbmute(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer(
            "Anda adalah **Admin Anonim** !\n\n» kembali ke akun pengguna dari hak admin."
        )
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Hanya admin dengan izin mengelola obrolan suara yang dapat mengetuk tombol ini !",
            show_alert=True,
        )
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.mute_stream(chat_id)
            await query.edit_message_text(
                "تم كتم صوت المقطع . 🔇", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"***Error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("❌ لا شيء يتدفق الأن", show_alert=True)


@Client.on_callback_query(filters.regex("cbunmute"))
async def cbunmute(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer(
            "Anda adalah **Admin Anonim** !\n\n» kembali ke akun pengguna dari hak admin."
        )
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Hanya admin dengan izin mengelola obrolan suara yang dapat mengetuk tombol ini !",
            show_alert=True,
        )
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.unmute_stream(chat_id)
            await query.edit_message_text(
                "تم أعاده تنشيط صوت المقطع . 🔊", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"**Error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("❌ لا شيء يتدفق الأن", show_alert=True)


@app.on_message(command(["volume", "vol"]))
@authorized_users_only
async def change_volume(client, m: Message):
    range = m.command[1]
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.change_volume_call(chat_id, volume=int(range))
            await m.reply(f"✅ **Volume disetel ke** `{range}`%")
        except Exception as e:
            await m.reply(f"**Error:**\n\n`{e}`")
    else:
        await m.reply("❌ **لآ يوجد فيديوهات مشغله أصلا ...**")
