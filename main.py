import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
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

# قاعدة بيانات سلاسل التقارير (Anatomy)
ANATOMY_SERIES = [
    {"id": 1, "title": "أساسيات علم التشريح", "status": "ready", "link": "https://example.com/anatomy_1.pdf", "desc": "مقدمة شاملة وأساسيات علم التشريح البشري."},
    {"id": 2, "title": "الخلايا والأنسجة", "status": "soon", "link": "", "desc": "دراسة أنواع الخلايا والأنسجة في الجسم."},
    {"id": 3, "title": "الجهاز الهيكلي - مقدمة", "status": "soon", "link": "", "desc": "نظرة عامة على الجهاز الهيكلي."},
    {"id": 4, "title": "عظام الجمجمة", "status": "soon", "link": "", "desc": "تفاصيل عظام الجمجمة والوجه."},
    {"id": 5, "title": "العمود الفقري", "status": "soon", "link": "", "desc": "تشريح فقرات العمود الفقري."},
    {"id": 6, "title": "القفص الصدري", "status": "soon", "link": "", "desc": "تشريح الضلوع وعظمة القص."},
    {"id": 7, "title": "الطرف العلوي", "status": "soon", "link": "", "desc": "عظام وعضلات اليد والذراع."},
    {"id": 8, "title": "الطرف السفلي", "status": "soon", "link": "", "desc": "عظام وعضلات الساق والقدم."},
    {"id": 9, "title": "المفاصل وأنواعها", "status": "soon", "link": "", "desc": "تصنيف المفاصل وحركاتها."},
    {"id": 10, "title": "الجهاز العضلي - مقدمة", "status": "soon", "link": "", "desc": "أساسيات عمل العضلات."},
    {"id": 11, "title": "عضلات الرأس والوجه", "status": "soon", "link": "", "desc": "تشريح العضلات التعبيرية في الوجه."},
    {"id": 12, "title": "عضلات الرقبة", "status": "soon", "link": "", "desc": "تشريح وعضلات الرقبة."},
    {"id": 13, "title": "عضلات الصدر", "status": "soon", "link": "", "desc": "تشريح عضلات منطقة الصدر."},
    {"id": 14, "title": "عضلات البطن", "status": "soon", "link": "", "desc": "تشريح عضلات البطن."},
    {"id": 15, "title": "عضلات الظهر", "status": "soon", "link": "", "desc": "تشريح عضلات الظهر."},
    {"id": 16, "title": "عضلات الطرف العلوي", "status": "soon", "link": "", "desc": "تفاصيل عضلات الذراعين."},
    {"id": 17, "title": "عضلات الطرف السفلي", "status": "soon", "link": "", "desc": "تفاصيل عضلات الأرجل."},
    {"id": 18, "title": "الجهاز العصبي - مقدمة", "status": "soon", "link": "", "desc": "أساسيات الجهاز العصبي."},
    {"id": 19, "title": "الدماغ", "status": "soon", "link": "", "desc": "تشريح أقسام الدماغ الرئيسية."},
    {"id": 20, "title": "الحبل الشوكي", "status": "soon", "link": "", "desc": "تشريح الحبل الشوكي ووظائفه."},
    {"id": 21, "title": "الأعصاب القحفية", "status": "soon", "link": "", "desc": "الأعصاب القحفية الـ 12 وتوزيعها."},
    {"id": 22, "title": "الأعصاب الشوكية", "status": "soon", "link": "", "desc": "توزيع الأعصاب الشوكية."},
    {"id": 23, "title": "الجهاز الدوري - تشريح القلب", "status": "soon", "link": "", "desc": "تشريح حجرات وصمامات القلب."},
    {"id": 24, "title": "الأوعية الدموية", "status": "soon", "link": "", "desc": "الشرايين والأوردة الرئيسية."},
    {"id": 25, "title": "الجهاز التنفسي", "status": "soon", "link": "", "desc": "تشريح الرئتين والمجاري التنفسية."},
    {"id": 26, "title": "الجهاز الهضمي", "status": "soon", "link": "", "desc": "تشريح أعضاء الجهاز الهضمي."},
    {"id": 27, "title": "الجهاز البولي", "status": "soon", "link": "", "desc": "تشريح الكلى والمثانة."},
    {"id": 28, "title": "الجهاز التناسلي", "status": "soon", "link": "", "desc": "نظرة عامة على الجهاز التناسلي."},
    {"id": 29, "title": "الجلد وملحقاته", "status": "soon", "link": "", "desc": "طبقات الجلد، الغدد، الشعر والأظافر."},
    {"id": 30, "title": "تشريح الوجه المهم للتجميل والليزر", "status": "soon", "link": "", "desc": "أهم الطبقات والأعصاب المستهدفة في جلسات الليزر والتجميل."},
]

# ---------------------------------------------------------
# لوحة الأزرار السفلية الشاملة (Reply Keyboard)
# ---------------------------------------------------------
def get_main_keyboard(user_id: int):
    buttons = [
        [KeyboardButton("📚 سلاسل التقارير"), KeyboardButton("✨ تقارير التجميل والليزر")],
        [KeyboardButton("ℹ️ معلومات عن المكتبة")]
    ]
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton("⚙️ لوحة تحكم الأدمن")])
        
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ---------------------------------------------------------
# الأوامر والرسائل
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    reply_markup = get_main_keyboard(user.id)

    welcome_text = (
        f"أهلاً بك يا {user.first_name} في **مكتبة تقنيات التجميل والليزر**! 🌿🩺\n\n"
        "يمكنك استخدام الأزرار في الأسفل للتنقل بين سلاسل التقارير وتصفح الأقسام بكل سهولة."
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# التعامل مع الأزرار النصية السفلية
async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user = update.effective_user

    if text == "📚 سلاسل التقارير":
        keyboard = [
            [InlineKeyboardButton("📚 سلسلة علم التشريح (Anatomy)", callback_data="series_anatomy")],
        ]
        await update.message.reply_text(
            "📖 **سلاسل التقارير المتاحة:**\nاختر السلسلة التي ترغب بتصفحها:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif text == "✨ تقارير التجميل والليزر":
        keyboard = [
            [InlineKeyboardButton("⚡ تقارير أجهزة الليزر", callback_data="laser_reports")],
            [InlineKeyboardButton("🧪 تقارير المواد والتركيبات", callback_data="cosmetics_reports")],
            [InlineKeyboardButton("🩺 العناية والبروتوكولات السريرية", callback_data="clinical_reports")],
        ]
        await update.message.reply_text(
            "✨ **قسم تقارير التجميل والليزر الأكاديمي:**\n"
            "اختر التخصص الفرعي لعرض التقارير المتاحة:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif text == "ℹ️ معلومات عن المكتبة":
        await update.message.reply_text(
            "ℹ️ **عن المكتبة الرقمية:**\n\n"
            "مكتبة أكاديمية متخصصة في توفير التقارير والدراسات لطلاب قسم **تقنيات التجميل والليزر**.\n"
            "تم إعداد وتنسيق هذه السلاسل لمساعدة الطلاب في مسيرتهم العلمية 🌿."
        )

    elif text == "⚙️ لوحة تحكم الأدمن" and user.id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("📊 إحصائيات السلاسل والتقارير", callback_data="admin_stats")],
            [InlineKeyboardButton("✏️ تعديل حالات التقارير", callback_data="admin_edit_status")],
            [InlineKeyboardButton("📢 إرسال إشعار للطلاب (إذاعة)", callback_data="admin_broadcast")],
        ]
        await update.message.reply_text(
            "⚙️ **أهلاً بك في لوحة تحكم الأدمن المتقدمة:**\n"
            "من هنا يمكنك إدارة كامل محتوى البوت ومتابعة الحالة.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

# التعامل مع أزرار الشاشة (Inline Buttons)
async def inline_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    user = update.effective_user

    if data == "series_anatomy":
        keyboard = []
        for item in ANATOMY_SERIES:
            if item["status"] == "ready":
                icon = "🟢"
            elif item["status"] == "in_progress":
                icon = "🟡"
            else:
                icon = "🔴"
                
            btn_text = f"{icon} {item['id']}. {item['title']}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"anat_{item['id']}")])
            
        await query.edit_message_text(
            "📚 **سلسلة علم التشريح (Anatomy):**\n"
            "🟢 جاهز | 🟡 جاري العمل | 🔴 قريباً\n\n"
            "اختر التقرير لعرض تفاصيله ورابط التحميل:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif data.startswith("anat_"):
        item_id = int(data.split("_")[1])
        item = next((b for b in ANATOMY_SERIES if b["id"] == item_id), None)

        if item:
            status_text = "🟢 جاهز للتحميل" if item["status"] == "ready" else ("🟡 جاري العمل عليه" if item["status"] == "in_progress" else "🔴 قريباً يتم العمل عليه")
            
            text = (
                f"📖 **التقرير رقم {item['id']}:** {item['title']}\n"
                f"📊 **الحالة:** {status_text}\n\n"
                f"📝 **الوصف:**\n{item['desc']}"
            )
            
            keyboard = []
            if item["status"] == "ready":
                keyboard.append([InlineKeyboardButton("📥 تحميل / قراءة التقرير", url=item["link"])])
            
            keyboard.append([InlineKeyboardButton("🔙 عودة لسلسلة التشريح", callback_data="series_anatomy")])
            
            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
            )

    elif data in ["laser_reports", "cosmetics_reports", "clinical_reports"]:
        keyboard = [[InlineKeyboardButton("🔙 عودة", callback_data="series_anatomy")]]
        await query.edit_message_text(
            "🚧 **جاري تجهيز تقارير هذا القسم.**\nسيتم إطلاقها وترتيبها قريباً جداً!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    # أزرار لوحة التحكم
    elif data == "admin_stats" and user.id == ADMIN_ID:
        ready_c = sum(1 for i in ANATOMY_SERIES if i["status"] == "ready")
        prog_c = sum(1 for i in ANATOMY_SERIES if i["status"] == "in_progress")
        soon_c = sum(1 for i in ANATOMY_SERIES if i["status"] == "soon")
        
        await query.edit_message_text(
            f"📊 **إحصائيات سلسلة التشريح:**\n\n"
            f"🟢 التقارير الجاهزة: {ready_c}\n"
            f"🟡 تقارير قيد الإعداد: {prog_c}\n"
            f"🔴 تقارير قريباً: {soon_c}\n"
            f"📂 المجموع الكلي: {len(ANATOMY_SERIES)} تقريراً",
            parse_mode="Markdown"
        )

    elif data == "admin_edit_status" and user.id == ADMIN_ID:
        await query.edit_message_text(
            "✏️ **طريقة تعديل حالة أي تقرير:**\n\n"
            "تستطيع تغيير حالة أي تقرير بسهولة فقط بتغيير قيمة `" "status" "` داخل كود البوت إلى:\n"
            "• `ready` (جاهز 🟢)\n"
            "• `in_progress` (جاري العمل 🟡)\n"
            "• `soon` (قريباً 🔴)",
            parse_mode="Markdown"
        )

    elif data == "admin_broadcast" and user.id == ADMIN_ID:
        await query.edit_message_text(
            "📢 **خاصية الإذاعة:**\nيمكنك استخدام هذا الزر مستقبلاً لإرسال تحديثات المكتبة لجميع المشتركين.",
            parse_mode="Markdown"
        )

# ---------------------------------------------------------
# التشغيل الرئيسي
# ---------------------------------------------------------
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_buttons))
    app.add_handler(CallbackQueryHandler(inline_button_handler))

    print("🤖 البوت يعمل الآن بنجاح مع التوكن المحدث!")
    app.run_polling()

if __name__ == "__main__":
    main()
