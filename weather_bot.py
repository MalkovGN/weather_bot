from aiogram import Bot, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import API_KEY, BOT_TOKEN
from main import get_weather, get_forecast, get_country
from utils import get_forecast_days

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

button_weather = KeyboardButton('Погода сейчас')
button_forecast = KeyboardButton('Прогноз на несколько дней')
button_add_city = KeyboardButton('Ввести новый город')

buttons = ReplyKeyboardMarkup(resize_keyboard=True)
buttons.add(button_weather)
buttons.add(button_forecast)
buttons.add(button_add_city)


class Info(StatesGroup):
    city = State()
    days = State


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await Info.city.set()
    await message.answer('Привет, напиши название города, в котором хочешь узнать погоду :)')


@dp.message_handler(Text(equals='Ввести новый город'))
async def new_city(message: types.Message):
    await Info.city.set()
    await message.answer('Привет, напиши название города, в котором хочешь узнать погоду :)')


@dp.message_handler(state=Info.city)
async def get_city(message: types.Message, state: FSMContext):
    if get_country(message.text) == 'None':
        await message.answer('Проверь название города, что-то не могу найти :)')
    else:
        async with state.proxy() as data:
            data['city'] = message.text
        await Info.next()
        await message.answer('Выбери вид прогноза \U0001F643', reply_markup=buttons)


@dp.message_handler(Text(equals='Погода сейчас'))
@dp.message_handler(state=Info.days)
async def get_weather_now(message: types.Message, state: FSMContext):
    await message.answer('Минутку... \U0001F914')
    async with state.proxy() as data:
        data['days'] = None
    output = get_weather(data['city'], API_KEY)
    await message.answer(output, reply_markup=buttons)


@dp.message_handler(Text(equals='Прогноз на несколько дней'))
@dp.message_handler(state=Info.days)
async def get_days(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['days'] = None
    await message.answer('Введите количество дней (до 16)')


@dp.message_handler(state='*')
async def get_forecast_weather(message: types.Message, state: FSMContext):
    await message.answer('Минутку... \U0001F914')
    forecast_days = get_forecast_days()

    try:
        if message.text not in forecast_days:
            await message.answer('Прогноз возможен только до 16 дней. Введите целое число от 1 до 16')
        else:
            async with state.proxy() as data:
                data['days'] = int(message.text)
            output = get_forecast(data['city'], data['days'], API_KEY)
            for day in output:
                await message.answer(day, reply_markup=buttons)
            await message.answer('Выбери действие на кнопках :) \nИли введи другое количество дней')
    except Exception:
        await message.answer('Выбери действие на кнопках:)', reply_markup=buttons)


if __name__ == '__main__':
    executor.start_polling(dp)
