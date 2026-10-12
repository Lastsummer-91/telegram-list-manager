import os, re, logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ChatMemberHandler, ContextTypes, filters
logging.basicConfig(level=logging.INFO)
BOT_TOKEN=os.getenv("BOT_TOKEN","").strip()
ADMIN_ID=int(os.getenv("ADMIN_ID","0") or "0")
GROUP_ID=int(os.getenv("GROUP_ID","0") or "0")
PATTERN=re.compile(r"(?<![\w])@([A-Za-z0-9_]{5,32})")
def admin(update): return bool(update.effective_user and ADMIN_ID and update.effective_user.id==ADMIN_ID)
async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if not admin(update):
        await update.message.reply_text("هذا البوت خاص بمسؤول القائمة.")
        return
    await update.message.reply_text("أرسل نصاً أو ملف TXT فيه حتى 1000 يوزر بصيغة @username. أزيل التكرار وأرجع ملفاً منظماً. /invite ينشئ رابط دعوة للكروب، و /stats يعرض الانضمامات المرصودة. فحص التنسيق لا يؤكد وجود الحساب، والبوت لا يضيف أشخاصاً قسراً.")
async def process(update, raw):
    if not admin(update):
        await update.message.reply_text("هذه الميزة متاحة لمسؤول البوت فقط.")
        return
    names=PATTERN.findall(raw)
    if len(names)>1000:
        await update.message.reply_text(f"وصلتني {len(names)} يوزرات. الحد 1000 في الدفعة؛ قسّم القائمة.")
        return
    seen=set(); unique=[]
    for n in names:
        k=n.lower()
        if k not in seen: seen.add(k); unique.append("@"+n)
    if not names:
        await update.message.reply_text("ما لقيت يوزرات بالتنسيق المتوقع مثل @username123.")
        return
    path="/tmp/clean_usernames.txt"
    with open(path,"w",encoding="utf-8") as f: f.write("\n".join(unique)+"\n")
    with open(path,"rb") as f:
        await update.message.reply_document(document=f,filename="clean_usernames.txt",caption=f"المقروء: {len(names)} | المكرر المحذوف: {len(names)-len(unique)} | بعد الفرز: {len(unique)}\nفحص التنسيق فقط، وليس تأكيد وجود الحساب.")
async def text_handler(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text and "@" in update.message.text: await process(update,update.message.text)
async def file_handler(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.document: return
    if not admin(update):
        await update.message.reply_text("رفع الملفات متاح لمسؤول البوت فقط."); return
    d=update.message.document
    if d.file_size and d.file_size>1_000_000:
        await update.message.reply_text("حجم الملف أكبر من 1 ميغابايت."); return
    tgfile=await context.bot.get_file(d.file_id)
    data=bytes(await tgfile.download_as_bytearray()).decode("utf-8-sig",errors="ignore")
    await process(update,data)
async def invite(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if not admin(update): await update.message.reply_text("الأمر للمسؤول فقط."); return
    if not GROUP_ID: await update.message.reply_text("أضف GROUP_ID في إعدادات الاستضافة أولاً."); return
    try:
        link=await context.bot.create_chat_invite_link(chat_id=GROUP_ID,name="دعوة مدير القوائم")
        await update.message.reply_text("رابط الدعوة:\n"+link.invite_link)
    except Exception as e:
        await update.message.reply_text("تعذر إنشاء الرابط. أضف البوت مشرفاً للكروب مع صلاحية دعوة المستخدمين. "+str(e)[:200])
async def stats(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if not admin(update): await update.message.reply_text("الأمر للمسؤول فقط."); return
    await update.message.reply_text(f"الانضمامات المرصودة منذ تشغيل البوت: {context.application.bot_data.get('joins',0)}. العداد مؤقت ويُصفّر عند إعادة التشغيل.")
async def member_update(update:Update, context:ContextTypes.DEFAULT_TYPE):
    c=update.chat_member
    if c and c.new_chat_member.status in ("member","administrator","creator") and c.old_chat_member.status not in ("member","administrator","creator"):
        context.application.bot_data["joins"]=context.application.bot_data.get("joins",0)+1
def main():
    if not BOT_TOKEN: raise RuntimeError("Missing BOT_TOKEN")
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start)); app.add_handler(CommandHandler("invite",invite)); app.add_handler(CommandHandler("stats",stats))
    app.add_handler(MessageHandler(filters.Document.ALL,file_handler)); app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text_handler))
    app.add_handler(ChatMemberHandler(member_update,ChatMemberHandler.CHAT_MEMBER))
    app.run_polling(allowed_updates=["message","chat_member"])
if __name__=="__main__": main()
