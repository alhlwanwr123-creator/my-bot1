import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)

# إعداد السجلات (Logging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ---------------------------------------------------------
# البيانات الأساسية والتوكن
# ---------------------------------------------------------
BOT_TOKEN = "7124304852:AAF3iHQNYloTarfOwWoIKCnczhoQwDs7qI0"
ADMIN_ID = 5765266007

# قنوات الاشتراك الإجباري (ضع المعرفات الخاصة بقنواتك)
REQUIRED_CHANNELS = ["@TJMELON"] 

# حالات المتابعة لإدخال البيانات (Conversation States)
WAITING_REPORT_TITLE, WAITING_REPORT_DESC, WAITING_REPORT_FILE = range(3)

# ---------------------------------------------------------
# إدارة قاعدة البيانات (SQLite)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT DEFAULT 'Anatomy',
            desc TEXT,
            status TEXT DEFAULT 'ready',
            file_id TEXT,
            downloads INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# دالة التحقق من الاشتراك الإجباري
# ---------------------------------------------------------
async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    for ch in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return True
    return True

# ---------------------------------------------------------
# لوحة الأزرار السفلية الشاملة (Reply Keyboard)
# ---------------------------------------------------------
def get_main_keyboard(user_id: int):
    buttons = [
        [KeyboardButton("🚀 الدخول إلى المكتبة"), KeyboardButton("📚 سلاسل التقارير")],
        [KeyboardButton("🤖 الذكاء الاصطناعي"), KeyboardButton("🏆 ملف الأسبوع")],
        [KeyboardButton("👤 حسابي"), KeyboardButton("ℹ️ معلومات عن المكتبة")]
    ]
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton("⚙️ لوحة تحكم الأدمن")])
        
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ---------------------------------------------------------
# الأوامر والرسائل الرئيسية
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    is_subbed = await check_subscription(user.id, context)

    if not is_subbed:
        keyboard = [
            [InlineKeyboardButton("📢 قناة التجميل غير الجراحي", url="https://t.me/TJMELON")],
            [InlineKeyboardButton("🚀 تحقق من الاشتراك والدخول", callback_data="check_join")]
        ]
        welcome_text = (
            f"أهلاً وسهلاً بك يا {user.first_name} في **مكتبة التجميل غير الجراحي** 💎\n\n"
            "⚠️ **لطفاً، للاستفادة من كافة ملفات المكتبة والخدمات، يرجى الانضمام للقناة الرسمية أولاً:**"
        )
        await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return ConversationHandler.END

    reply_markup = get_main_keyboard(user.id)
    welcome_text = (
        f"🎀 أهلاً وسهلاً بك يا {user.first_name} في **مكتبة التجميل غير الجراحي**\n\n"
        "يسعدنا انضمامك 💙\n\n"
        "هذا البوت صُمم ليساعد طلبة قسم تقنيات التجميل والليزر في العراق على الوصول إلى المحتوى العلمي بسهولة.\n\n"
        "اختر من القائمة بالأسفل الخدمة التي تحتاجها وابدأ رحلتك التعليمية معنا 🌸"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return ConversationHandler.END

# التعامل مع الأزرار النصية السفلية
async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    user = update.effective_user

    if text in ["🚀 الدخول إلى المكتبة", "📚 سلاسل التقارير"]:
        await show_categories(update, context)

    elif text == "🤖 الذكاء الاصطناعي":
        ai_keyboard = [
            [InlineKeyboardButton("📝 تلخيص تقرير", callback_data="ai_summary"), InlineKeyboardButton("🌐 ترجمة مصطلحات", callback_data="ai_trans")],
            [InlineKeyboardButton("❓ إنشاء أسئلة MCQ", callback_data="ai_mcq")],
            [InlineKeyboardButton("🔙 العودة للقائمة", callback_data="back_home")]
        ]
        await update.message.reply_text("🤖 **قسم الذكاء الاصطناعي الطبي:**\nاختر الخدمة المطلوبة للمساعدة دراسياً:", reply_markup=InlineKeyboardMarkup(ai_keyboard), parse_mode="Markdown")

    elif text == "🏆 ملف الأسبوع":
        await update.message.reply_text("🏆 **ملف الأسبوع المميز:**\n\n📌 **تقرير 1: أساسيات علم التشريح (Fundamentals of Anatomy)**\n✍️ إعداد: أنور لؤي\n⭐ التقييم: 4.9/5", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📖 عرض التقرير", callback_data="view_rep_1")]]))

    elif text == "👤 حسابي":
        profile_text = (
            f"👤 **معلومات حسابك:**\n\n"
            f"🔹 **الاسم:** {user.first_name}\n"
            f"🆔 **المعرف:** `{user.id}`\n"
            f"📥 **سجل التحميلات:** متصل بالخادم ✅\n"
            f"⭐ **الحالة:** طالب/أخصائي متفاعل"
        )
        await update.message.reply_text(profile_text, parse_mode="Markdown")

    elif text == "ℹ️ معلومات عن المكتبة":
        info_text = (
            "📚 **معلومات المكتبة الرسمية**\n\n"
            "مرجع علمي شامل لطلبة وخريجي قسم تقنيات التجميل والليزر في العراق.\n\n"
            "👑 **إدارة وإشراف:** أنور ☑️\n"
            "🔹 **الفريق العلمي:** مكتبة التجميل غير الجراحي"
        )
        keyboard = [
            [InlineKeyboardButton("💬 التواصل مع الإدارة", url="https://t.me/ttzzzztt")],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_home")]
        ]
        await update.message.reply_text(info_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif text == "⚙️ لوحة تحكم الأدمن" and user.id == ADMIN_ID:
        await show_admin_panel(update, context)

    return ConversationHandler.END

# عرض التصنيفات والمواد الدراسية
async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧪 Anatomy (علم التشريح)", callback_data="sub_Anatomy")],
        [InlineKeyboardButton("🔬 Physiology (علم وظائف الأعضاء)", callback_data="sub_Physiology")],
        [InlineKeyboardButton("⚡ Laser Principles (مبادئ الليزر)", callback_data="sub_Laser")],
        [InlineKeyboardButton("🩺 Dermatology (الأمراض الجلدية)", callback_data="sub_Dermatology")],
        [InlineKeyboardButton("💉 أجهزة التجميل والفيلر", callback_data="sub_Aesthetics")],
        [InlineKeyboardButton("🔙 الصفحة الرئيسية", callback_data="back_home")]
    ]
    text = "📚 **المكتبة العلمية | اختر المادة الدراسية:**"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# عرض قائمة التقارير التابعة لمادة معينة
async def show_reports_by_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status FROM reports WHERE category=?", (category,))
    reports = cursor.fetchall()
    conn.close()

    keyboard = []
    if reports:
        for r_id, title, status in reports:
            icon = "🟢" if status == "ready" else ("🟡" if status == "in_progress" else "🔴")
            keyboard.append([InlineKeyboardButton(f"{icon} {title}", callback_data=f"view_rep_{r_id}")])
    else:
        keyboard.append([InlineKeyboardButton("لا توجد تقارير مضافة في هذا القسم بعد", callback_data="none")])

    keyboard.append([InlineKeyboardButton("🔙 رجوع للتصنيفات", callback_data="categories")])
    text = f"🧪 **سلسلة تقارير ({category}):**\n🟢 جاهز | 🟡 جاري العمل | 🔴 قريباً"
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# لوحة الأدمن
async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ إضافة تقرير جديد (PDF)", callback_data="admin_add_rep")],
        [InlineKeyboardButton("✏️ إدارة / حذف التقارير", callback_data="admin_manage_reps")],
    ]
    text = "⚙️ **لوحة تحكم الأدمن المتقدمة:**\nيمكنك من هنا رفع ملفات PDF وإدارتها حسب المواد."
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ---------------------------------------------------------
# خطوات إضافة تقرير جديد (ConversationHandler)
# ---------------------------------------------------------
async def start_add_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return ConversationHandler.END

    await query.edit_message_text("📝 **أرسل الآن عنوان/اسم التقرير الجديد:**", parse_mode="Markdown")
    return WAITING_REPORT_TITLE

async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["rep_title"] = update.message.text
    await update.message.reply_text("📖 **أرسل الآن وصفاً مختصراً للتقرير (أو الأقسام داخل التقرير):**")
    return WAITING_REPORT_DESC

async def receive_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["rep_desc"] = update.message.text
    await update.message.reply_text("📎 **الآن أرسل ملف الـ PDF الخاص بالتقرير:**")
    return WAITING_REPORT_FILE

async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.document:
        await update.message.reply_text("⚠️ يرجى إرسال ملف PDF كـ مستند (Document).")
        return WAITING_REPORT_FILE

    file_id = update.message.document.file_id
    title = context.user_data["rep_title"]
    desc = context.user_data["rep_desc"]

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reports (title, category, desc, status, file_id) VALUES (?, 'Anatomy', ?, 'ready', ?)", (title, desc, file_id))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ **تم إضافة التقرير بنجاح!**\n\n📌 **العنوان:** {title}", reply_markup=get_main_keyboard(ADMIN_ID), parse_mode="Markdown")
    return ConversationHandler.END

async def cancel_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ تم إلغاء الإضافة.", reply_markup=get_main_keyboard(ADMIN_ID))
    return ConversationHandler.END

# ---------------------------------------------------------
# معالجة الضغط على الأزرار الداخلية (Inline Buttons)
# ---------------------------------------------------------
async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "check_join":
        if await check_subscription(user_id, context):
            await query.edit_message_text("✅ تم التحقق من الانضمام بنجاح! أهلاً بك في المكتبة 🌸")
        else:
            await query.answer("❌ يرجى الاشتراك بقناة التجميل غير الجراحي أولاً!", show_alert=True)

    elif data == "categories":
        await show_categories(update, context)

    elif data == "back_home":
        await query.edit_message_text("🌸 أهلاً بك مجدداً في القائمة الرئيسية!")

    elif data.startswith("sub_"):
        cat_name = data.split("_")[1]
        await show_reports_by_category(update, context, cat_name)

    elif data.startswith("view_rep_"):
        rep_id = int(data.split("_")[2])
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE reports SET views = views + 1 WHERE id=?", (rep_id,))
        conn.commit()
        cursor.execute("SELECT id, title, category, desc, status, file_id, downloads, views FROM reports WHERE id=?", (rep_id,))
        rep = cursor.fetchone()
        conn.close()

        if rep:
            r_id, title, category, desc, status, file_id, downloads, views = rep
            status_str = "🟢 جاهز للتحميل" if status == "ready" else ("🟡 جاري العمل عليه" if status == "in_progress" else "🔴 قريباً")
            
            card_text = (
                f"📄 **اسم التقرير:** {title}\n"
                f"🧪 **المادة:** {category}\n"
                f"👤 **إعداد:** أخصائي التجميل والليزر أنور لؤي\n"
                f"📊 **الحالة:** {status_str}\n"
                f"👁 **المشاهدات:** {views} | 📥 **التحميلات:** {downloads}\n\n"
                f"📝 **الوصف والترتيب:**\n{desc}"
            )
            keyboard = []
            if file_id and status == "ready":
                keyboard.append([InlineKeyboardButton("📥 الحصول على ملف PDF", callback_data=f"send_file_{r_id}")])
            keyboard.append([InlineKeyboardButton("❤️ إضافة للمفضلة", callback_data="fav_add"), InlineKeyboardButton("⭐ تقييم الملف", callback_data="rate")])
            keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة", callback_data=f"sub_{category}")])

            await query.edit_message_text(card_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith("send_file_"):
        rep_id = int(data.split("_")[2])
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE reports SET downloads = downloads + 1 WHERE id=?", (rep_id,))
        conn.commit()
        cursor.execute("SELECT title, file_id FROM reports WHERE id=?", (rep_id,))
        rep = cursor.fetchone()
        conn.close()

        if rep and rep[1]:
            await query.message.reply_document(document=rep[1], caption=f"📄 **ملف تقرير:** {rep[0]}\n👑 إعداد وتنضيد: أنور لؤي ☑️")

    elif data in ["fav_add", "rate"]:
        await query.answer("✅ تم تسجيل تفاعلك مع التقرير!", show_alert=True)

    elif data == "admin_manage_reps" and user_id == ADMIN_ID:
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, status FROM reports")
        reports = cursor.fetchall()
        conn.close()

        keyboard = []
        for r_id, title, status in reports:
            icon = "🟢" if status == "ready" else ("🟡" if status == "in_progress" else "🔴")
            keyboard.append([InlineKeyboardButton(f"{icon} {title}", callback_data=f"adm_edit_{r_id}")])
        keyboard.append([InlineKeyboardButton("🔙 العودة للوحة الأدمن", callback_data="admin_home")])
        await query.edit_message_text("⚙️ **اختر التقرير لتغيير حالته أو حذفه:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "admin_home" and user_id == ADMIN_ID:
        await show_admin_panel(update, context)

    elif data.startswith("adm_edit_") and user_id == ADMIN_ID:
        rep_id = int(data.split("_")[2])
        keyboard = [
            [InlineKeyboardButton("🟢 تعيين كـ جاهز", callback_data=f"set_stat_{rep_id}_ready")],
            [InlineKeyboardButton("🟡 تعيين كـ جاري العمل", callback_data=f"set_stat_{rep_id}_in_progress")],
            [InlineKeyboardButton("🔴 تعيين كـ قريباً", callback_data=f"set_stat_{rep_id}_soon")],
            [InlineKeyboardButton("🗑️ حذف التقرير نهائياً", callback_data=f"del_rep_{rep_id}")],
            [InlineKeyboardButton("🔙 العودة", callback_data="admin_manage_reps")]
        ]
        await query.edit_message_text("✏️ **اختر الإجراء المطلوب للتقرير:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith("set_stat_") and user_id == ADMIN_ID:
        parts = data.split("_")
        rep_id = int(parts[2])
        new_status = parts[3]
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE reports SET status=? WHERE id=?", (new_status, rep_id))
        conn.commit()
        conn.close()
        await query.edit_message_text("✅ **تم تحديث حالة التقرير بنجاح!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 العودة", callback_data="admin_manage_reps")]]), parse_mode="Markdown")

    elif data.startswith("del_rep_") and user_id == ADMIN_ID:
        rep_id = int(data.split("_")[2])
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reports WHERE id=?", (rep_id,))
        conn.commit()
        conn.close()
        await query.edit_message_text("🗑️ **تم حذف التقرير بنجاح.**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 العودة", callback_data="admin_manage_reps")]]), parse_mode="Markdown")

# ---------------------------------------------------------
# التشغيل الرئيسي
# ---------------------------------------------------------
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    # محادثة إضافة التقرير
    add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_report, pattern="^admin_add_rep$")],
        states={
            WAITING_REPORT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],
            WAITING_REPORT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_desc)],
            WAITING_REPORT_FILE: [MessageHandler(filters.Document.ALL, receive_file)],
        },
        fallbacks=[CommandHandler("cancel", cancel_add)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(add_conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_buttons))
    app.add_handler(CallbackQueryHandler(inline_handler))

    print("🤖 البوت يعمل بنجاح مع القناة الرسمية ونظام الأقسام الاحترافي!")
    app.run_polling()

if __name__ == "__main__":
    main()
