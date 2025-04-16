from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import json

# Заменить токен на актуальный
TOKEN = '7269073941:AAFwoUkGpUfa1XK8b_4xvxZEkU8XE4MRWlI'
print("Файл реально запустился!")

def load_bartenders():
    with open("/Users/zanadzigitov/Desktop/bottg/bartenders.json", "r", encoding="utf-8") as f:
        return json.load(f)["bartenders"]

def save_bartenders(data):
    with open("/Users/zanadzigitov/Desktop/bottg/bartenders.json", "w", encoding="utf-8") as f:
        json.dump({"bartenders": data}, f, ensure_ascii=False, indent=2)

def set_bartender_id(name, chat_id):
    print(f"[DEBUG] Сохраняю chat_id {chat_id} для бармена {name}")
    bartenders = load_bartenders()
    for b in bartenders:
        if b["name"] == name:
            b["id"] = chat_id
            break
    save_bartenders(bartenders)

def set_current_bartender(name):
    bartenders = load_bartenders()
    for b in bartenders:
        b["on_shift"] = False  # Снимаем всех барменов со смены
        if b["name"] == name:
            b["on_shift"] = True  # Устанавливаем смену для указанного бармена
    save_bartenders(bartenders)

def get_current_bartender():
    bartenders = load_bartenders()
    for b in bartenders:
        if b["on_shift"]:
            return b
    return None

def start(update: Update, context: CallbackContext):
    # Укажи здесь ссылку на свой WebApp (локальную или размещённую)
    webapp_url = 'https://zhanaddzhigitov.github.io/menu2/'
    keyboard = [
        [KeyboardButton("Открыть меню", web_app=WebAppInfo(url=webapp_url))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Нажми кнопку ниже, чтобы открыть меню:", reply_markup=reply_markup)

def handle_webapp_data(update: Update, context: CallbackContext):
    order = update.message.web_app_data.data
    update.message.reply_text(f"✅ Заказ получен:\n\n{order}")
    current_bartender = get_current_bartender()
    if current_bartender and current_bartender["id"]:
        context.bot.send_message(chat_id=current_bartender["id"], text=f"📦 Новый заказ:\n\n{order}")
    else:
        update.message.reply_text("⚠️ Нет бармена на смене. Заказ не может быть обработан.")

def start_shift(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("⚠️ Укажи имя бармена: /shift Зубаир")
        return

    name = " ".join(context.args)
    bartenders = load_bartenders()

    # Проверяем, существует ли бармен с указанным именем
    bartender = next((b for b in bartenders if b["name"] == name), None)
    if not bartender:
        update.message.reply_text(f"⚠️ Бармен с именем {name} не найден. Проверьте имя.")
        return

    # Устанавливаем бармена на смену
    set_current_bartender(name)
    set_bartender_id(name, update.effective_chat.id)

    print(f"[DEBUG] Бармен {name} получил chat_id {update.effective_chat.id}")
    update.message.reply_text(f"✅ Бармен {name} теперь на смене.")

def end_shift(update: Update, context: CallbackContext):
    current_bartender = get_current_bartender()
    if not current_bartender:
        update.message.reply_text("⚠️ Никто не находится на смене.")
        return

    # Снимаем текущего бармена со смены
    bartenders = load_bartenders()
    for b in bartenders:
        if b["name"] == current_bartender["name"]:
            b["on_shift"] = False
            break
    save_bartenders(bartenders)

    update.message.reply_text(f"✅ Бармен {current_bartender['name']} вышел со смены.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("shift", start_shift))
    dp.add_handler(CommandHandler("end_shift", end_shift))
    dp.add_handler(MessageHandler(Filters.status_update.web_app_data, handle_webapp_data))

    print("Бот запущен.")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
