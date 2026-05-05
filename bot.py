import asyncio, json, time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import init_db, create_user, get_user, get_full_state, add_coins
from config import BOT_TOKEN, WEBAPP_URL

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

### BASE ###
@dp.message(Command("start"))
async def start_cmd(m: types.Message):
    await create_user(m.from_user.id, m.from_user.username)
    await m.answer("👋 Добро пожаловать на Супер-Ферму!\nЖми /farm чтобы открыть игру.")

@dp.message(Command("help"))
async def help_cmd(m: types.Message):
    await m.answer("""/farm — открыть ферму
/bonus — ежедневный бонус
/zoo — купить животных
/store — купить товары
/energy — энергия
/upgrade — улучшения
""")

@dp.message(Command("farm"))
async def farm_cmd(m: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🚜 Играть", web_app=types.WebAppInfo(url=WEBAPP_URL))
    await m.answer("Нажми кнопку, чтобы войти на ферму!", reply_markup=kb.as_markup())

@dp.message(Command("bonus"))
async def bonus_cmd(m: types.Message):
    user = await get_user(m.from_user.id)
    now = int(time.time())
    last_bonus = user[9] or 0  # daily_ts
    if now - last_bonus > 60*60*20:  # 1 раз в 20ч
        await add_coins(m.from_user.id, 50)
        await m.answer("🎁 Ты получил 50 монет! Заходи завтра ещё за наградой.")
    else:
        await m.answer("👉 Бонус уже получен. Возвращайся позже!")

### Динамический магазин ###
@dp.message(Command("store"))
async def store_cmd(m: types.Message):
    await m.answer("🛒 Магазин (поддержка в webapp — покупай в самой игре!)\nКупить можно зверей, грядки, ускорения.")

### WebAppData: Главный роутер ###
@dp.message(F.web_app_data)
async def webapp_data(message: types.Message):
    user_id = message.from_user.id
    try:
        data = json.loads(message.web_app_data.data)
    except:
        await message.answer("Ошибка JSON")
        return

    act = data.get("action")
    d = data.get("data", {})
    if act == "sync":
        await message.answer(json.dumps(await get_full_state(user_id)))
    elif act == "plant":
        await add_coins(user_id, -2)
        await message.answer("🌱 Ты посадил растение! -2 монеты.")
    elif act == "harvest":
        await add_coins(user_id, 8)
        await message.answer("🌾 Урожай собран! +8 монет.")
    elif act == "water":
        await message.answer("💧 Грядка политa (больше урожая)!")
    elif act == "buy_animal":
        await add_coins(user_id, -10)
        await message.answer("🐮 Новое животное! -10 монет.")
    elif act == "buy_building":
        await message.answer("🏡 Новое здание построено!")
    elif act == "buy_upgrade":
        await message.answer("⬆️ Улучшение куплено!")
    elif act == "event":
        await message.answer("🎯 Событие произошло!")
    elif act == "use_energy":
        await message.answer("⚡ Энергия использована!")
    elif act == "get_ticket":
        await message.answer("🎟️ Ты получил билет на ивент!")
    else:
        await message.answer("Неизвестное действие.")

### Запуск авто-ивентов в фоне ###
async def event_ticker():
    while True:
        try:
            await asyncio.sleep(30) # каждые 30 сек
            # тут можно делать рассылки, авто-уведомления, авто-полив, авто-урожай и т.д.
            # примеры: await bot.send_message(user_id, "🎁 Ежедневная награда!")
        except Exception as e:
            print("BG error:", e)

async def main():
    await init_db()
    asyncio.create_task(event_ticker())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())