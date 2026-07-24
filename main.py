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
BOT_TOKEN = "7124304852:AAHSlvMk_kyZE86ANyayMhGtLXV2gJ6sc80"
ADMIN_ID = 5765266007

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
            desc TEXT,
            status TEXT DEFAULT 'ready',
            file_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# لوحة الأزرار السفلية الشاملة (Reply Keyboard)
# ---------------------------------------------------------
def get_main_keyboard(user_id: int):
    buttons = [
        [KeyboardButton("📚 سلاسل التقارير"), KeyboardButton("ℹ️ معلومات عن المكتبة")]
    ]
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton("⚙️ لوحة تحكم الأدمن")])
        
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ---------------------------------------------------------
# الأوامر والرسائل الرئيسية
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    reply_markup = get_main_keyboard(user.id)

    welcome_text = (
        "🎀 أهلاً وسهلاً بك في بوت قناة التجميل غير الجراحي\n\n"
        "يسعدنا انضمامك 💙\n\n"
        "هذا البوت صُمم ليساعد طلبة قسم تقنيات التجميل والليزر في العراق على الوصول إلى المحتوى العلمي بسهولة\n\n"
        "ستجد هنا:\n"
        "📚 تقارير ومحاضرات\n"
        "🧬 مصادر علمية\n"
        "📝 أسئلة ومراجعات\n"
        "📢 آخر الإعلانات\n"
        "🎓 كل ما يخص القسم في مكان واحد\n\n"
        "اختر من القائمة بالأسفل الخدمة التي تحتاجها وابدأ رحلتك التعليمية معنا\n\n"
        "نتمنى لك التوفيق والنجاح 🌸\n\n"
        "https://t.me/TJMELON"
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, disable_web_page_preview=False)
    return ConversationHandler.END

# التعامل مع الأزرار النصية السفلية
async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    user = update.effective_user

    if text == "📚 سلاسل التقارير":
        await show_reports_list(update, context)

    elif text == "ℹ️ معلومات عن المكتبة":
        info_text = (
            "📚 معلومات المكتبة\n\n"
            "مرحباً بك في مكتبة التجميل غير الجراحي\n\n"
            "المكتبة أُنشئت لتكون مرجعاً علمياً لطلبة قسم تقنيات التجميل والليزر في العراق، وتهدف إلى جمع المصادر التعليمية في مكان واحد لتسهيل الوصول إليها.\n\n"
            "ستجد داخل المكتبة:\n"
            "📖 تقارير علمية\n"
            "📚 كتب ومراجع\n"
            "📝 ملخصات دراسية\n"
            "🎓 محاضرات وملفات PDF\n"
            "🧬 معلومات عن الأجهزة والتقنيات\n"
            "❓ أسئلة للمراجعة والاختبارات\n"
            "📢 ملفات ومحتوى يتم تحديثه باستمرار\n\n"
            "نسعى لتوفير محتوى علمي منظم وموثوق يساعد الطلبة طوال مسيرتهم الدراسية.\n\n"
            "نتمنى لكم الفائدة والتوفيق 🌸"
        )
        keyboard = [
            [InlineKeyboardButton("📖 الدخول إلى المكتبة", callback_data="open_library")],
            [InlineKeyboardButton("📂 التصنيفات", callback_data="categories")],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_home")]
        ]
        await update.message.reply_text(info_text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "⚙️ لوحة تحكم الأدمن" and user.id == ADMIN_ID:
        await show_admin_panel(update, context)

    return ConversationHandler.END

# عرض قائمة التقارير للطلاب
async def show_reports_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status FROM reports")
    reports = cursor.fetchall()
    conn.close()

    keyboard = []
    if reports:
        for r_id, title, status in reports:
            icon = "🟢" if status == "ready" else ("🟡" if status == "in_progress" else "🔴")
            keyboard.append([InlineKeyboardButton(f"{icon} {title}", callback_data=f"view_rep_{r_id}")])
    else:
        keyboard.append([InlineKeyboardButton("لا توجد تقارير مضافة حالياً", callback_data="none")])

    text = "📚 **سلاسل التقارير المتاحة:**\n🟢 جاهز | 🟡 جاري العمل | 🔴 قريباً\n\nاختر التقرير المطلوب:"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# لوحة الأدمن
async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ إضافة تقرير جديد (PDF)", callback_data="admin_add_rep")],
        [InlineKeyboardButton("✏️ إدارة / حذف التقارير", callback_data="admin_manage_reps")],
    ]
    text = "⚙️ **لوحة تحكم الأدمن المتقدمة:**\nيمكنك من هنا إضافة ملفات PDF وإدارتها وحذفها."
    
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
    await update.message.reply_text("📖 **أرسل الآن وصفاً مختصراً للتقرير:**")
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
    cursor.execute("INSERT INTO reports (title, desc, status, file_id) VALUES (?, ?, 'ready', ?)", (title, desc, file_id))
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

    if data == "open_library" or data == "categories":
        await show_reports_list(update, context)

    elif data == "back_home":
        await query.edit_message_text("🌸 نتمنى لك التوفيق والنجاح!")

    elif data.startswith("view_rep_"):
        rep_id = int(data.split("_")[2])
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, desc, status, file_id FROM reports WHERE id=?", (rep_id,))
        rep = cursor.fetchone()
        conn.close()

        if rep:
            r_id, title, desc, status, file_id = rep
            status_str = "🟢 جاهز للتحميل" if status == "ready" else ("🟡 جاري العمل عليه" if status == "in_progress" else "🔴 قريباً")
            
            text = f"📖 **التقرير:** {title}\n📊 **الحالة:** {status_str}\n\n📝 **الوصف:**\n{desc}"
            keyboard = []
            
            if file_id and status == "ready":
                keyboard.append([InlineKeyboardButton("📥 الحصول على ملف PDF", callback_data=f"send_file_{r_id}")])
            keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة", callback_data="open_library")])

            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith("send_file_"):
        rep_id = int(data.split("_")[2])
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title, file_id FROM reports WHERE id=?", (rep_id,))
        rep = cursor.fetchone()
        conn.close()

        if rep and rep[1]:
            await query.message.reply_document(document=rep[1], caption=f"📄 **ملف تقرير:** {rep[0]}")

    elif data == "admin_manage_reps" and user_id == ADMIN_ID:
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, status FROM reports")
        reports = cursor.fetchall()
        conn.close()

        keyboard = []
        for r_id, title, status in reports:
            icon = "🟢" if status == "ready" else ("🟡" if status == "in_progress" else "🔴")
            keyboard.append([
                InlineKeyboardButton(f"{icon} {title}", callback_data=f"adm_edit_{r_id}")
            ])
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
        await query.edit_message_text("✏️ **اختر الإجراء المطلوبة للتقرير:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith("set_stat_") and user_id == ADMIN_ID:
        _, _, rep_id, new_status = data.split("_")
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

    print("🤖 البوت يعمل بنجاح مع نظام قاعدة البيانات والملفات المباشرة!")
    app.run_polling()

if __name__ == "__main__":
    main()
