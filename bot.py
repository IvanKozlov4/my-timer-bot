from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

TOKEN = "8747552463:AAFc4_nF7mFngASjPulW67rV45FlHYaqK2Q"
TARGET_DATE = datetime(2026, 6, 6, 2, 0, 0)

# Храним задачи
active_timers = {}

def get_time_text():
    now = datetime.now()
    diff = TARGET_DATE - now
    
    if now >= TARGET_DATE:
        return "🎉"
    
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    seconds = diff.seconds % 60
    
    # Только цифры через двоеточие
    return f"{days:03d}:{hours:02d}:{minutes:02d}:{seconds:02d}"

async def start(update: Update, context):
    await update.message.reply_text(
        "Команды:\n"
        "/check - проверить\n"
        "/live - запустить\n"
        "/stop - остановить"
    )

async def check(update: Update, context):
    await update.message.reply_text(get_time_text())

async def live(update: Update, context):
    chat_id = update.effective_chat.id
    
    # Если уже есть таймер для этого чата - останавливаем
    if chat_id in active_timers:
        active_timers[chat_id].cancel()
    
    # Отправляем первое сообщение
    msg = await update.message.reply_text(get_time_text())
    
    # Создаем задачу на обновление
    task = asyncio.create_task(update_timer(context, chat_id, msg.message_id))
    active_timers[chat_id] = task

async def update_timer(context, chat_id, message_id):
    """Обновляет сообщение каждую секунду"""
    try:
        while True:
            await asyncio.sleep(1)  # Ждем 1 секунду
            
            try:
                # Пробуем отредактировать сообщение
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=get_time_text()
                )
                print(f"✅ Обновлено: {chat_id}")
            except Exception as e:
                print(f"Ошибка редактирования: {e}")
                # Если редактировать не получается - выходим
                break
    except asyncio.CancelledError:
        print(f"❌ Таймер остановлен для чата {chat_id}")
    except Exception as e:
        print(f"Ошибка: {e}")

async def stop(update: Update, context):
    chat_id = update.effective_chat.id
    
    if chat_id in active_timers:
        active_timers[chat_id].cancel()
        del active_timers[chat_id]
        await update.message.reply_text("⏹️")
    else:
        await update.message.reply_text("Нет активного отсчета. Запустите /live")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("live", live))
    app.add_handler(CommandHandler("stop", stop))
    
    print("🚀 БОТ ЗАПУЩЕН!")
    print(f"📅 Отсчет до: {TARGET_DATE.strftime('%d.%m.%Y %H:%M')}")
    print("💬 Напишите /live в личном чате с ботом")
    
    app.run_polling()

if __name__ == "__main__":
    main()
