# Bot.py
# -*- coding: utf8 -*-

from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from BotToken import bot_token
from qrgenerator import qr_generate_transactions, qr_generate_personal
from ScanQR import scan_qr
from headline import create_headline
import os
from datetime import datetime
import sqlite3
import curs, curs_usd
import importlib


storage = MemoryStorage()

bot = Bot(token = bot_token)
db = Dispatcher(bot, storage = storage)


# Дефолтные кнопки
kb1 = types.KeyboardButton("Создать свой QR-код")
kb2 = types.KeyboardButton("Создать QR-код для транзакции")
kb3 = types.KeyboardButton("Отсканировать QR-код 📷")
kb_default = types.ReplyKeyboardMarkup(resize_keyboard = True)
kb_default.add(kb1).insert(kb2).add(kb3)

# Кнопка "Отмена"
kb4 = types.KeyboardButton("Отмена")
kb_cancel = types.ReplyKeyboardMarkup(resize_keyboard = True)
kb_cancel.add(kb4)

# Кнопка "Пропустить"
kb5 = types.KeyboardButton("Пропустить")
kb_continue = types.ReplyKeyboardMarkup(resize_keyboard = True)
kb_continue.add(kb5)

# Две кнопки "Отмена" и "Пропустить"
cancel_and_continue = types.ReplyKeyboardMarkup(resize_keyboard = True)
cancel_and_continue.add(kb4).insert(kb5)

# Кнопки с выбором валют
kb6 = types.KeyboardButton("Ввести в рублях(₽)")
kb7 = types.KeyboardButton("Ввести в долларах($)")
kb_currencies = types.ReplyKeyboardMarkup(resize_keyboard = True)
kb_currencies.add(kb6).insert(kb7).add(kb4).insert(kb5)

# Удаление кнопки
kb_delete = types.ReplyKeyboardRemove()


# Класс состояния генератора личного QR-кода
class GenerateQR(StatesGroup):
	get_data = State()


# Класс состояния получения реквизитов
class Requisites(StatesGroup):
	address = State()
	public_key = State()
	amount = State()
	amount_dollars = State()
	amount_rubles = State()
	comment = State()


# Класс состояния скана QR-кода
class Scan(StatesGroup):
	get_photo = State()


# Приветствие нового пользователя
@db.message_handler(commands = ["start"])
async def welcome(message: types.Message):
	await message.answer(f"Приветствую вас, {message.from_user.first_name}!\nЯ — QR-prizm, бот, который создаёт QR-коды с данными о переводе криптовалюты PRIZM.\nВведите адрес кошелька, его публичный ключ, количество переводимых монет и комментарий. И тогда я создам QR-код, отсканировав который можно будет перевести криптовалюту.",
					reply_markup = kb_default)

	try:
		connect = sqlite3.connect("QR-prizm users.db")
		db = connect.cursor()
		db.execute(f'INSERT INTO Пользователи VALUES("{message.from_user.id}", "@{message.from_user.username}")')
		connect.commit()
		connect.close()
		print(f"@{message.from_user.username} запустил бота")
	
	except sqlite3.IntegrityError:
		pass



# Дефолтное состояние бота
@db.message_handler(state = None)
async def get_command(message: types.Message):
	if message.text == "Создать свой QR-код":
		await message.answer("Пришлите данные", reply_markup = kb_cancel)
		await GenerateQR.get_data.set()

	elif message.text == "Создать QR-код для транзакции":
		await message.answer("Пришлите адрес кошелька(Address)", reply_markup = kb_cancel)
		await Requisites.address.set()

	elif message.text == "Отсканировать QR-код 📷":
		await message.answer("Пришлите изображение с QR-кодом", reply_markup = kb_cancel)
		await Scan.get_photo.set()

	else:
		await message.answer("Пришлите мне одну из команд ниже👇", reply_markup = kb_default)



# Состояние получения данных и генерация личного QR-кода
@db.message_handler(state = GenerateQR.get_data)
async def generate_personal_qr(message: types.Message, state: FSMContext):
	if message.text == "Отмена":
		await state.reset_state()
		await message.answer("Создание QR-кода отменено", reply_markup = kb_default)

	else:
		await message.answer("QR-код создаётся...", reply_markup = kb_delete)
		qr_generate_personal(message.text, f"{message.from_user.id}.png")
		
		with open(f"{message.from_user.id}.png", "rb") as photo:
			await bot.send_photo(message.chat.id, photo, reply_markup = kb_default)

		os.remove(f"{message.from_user.id}.png")
		await state.finish()



# Получение адреса
@db.message_handler(state = Requisites.address)
async def get_address(message: types.Message, state: FSMContext):
	if message.text == "Отмена":
		await state.reset_state()
		await message.answer("Создание QR-кода отменено", reply_markup = kb_default)
	
	else:
		address = message.text
		await state.update_data(address = address)
		await message.answer("Его публичный ключ(Public key)", reply_markup = cancel_and_continue)
		await Requisites.next()


# Получение публичного ключа
@db.message_handler(state = Requisites.public_key)
async def get_public_key(message: types.Message, state: FSMContext):
	if message.text == "Пропустить":
		await state.update_data(pk = "")
		await message.answer("Количество PRIZM(Amount)", reply_markup = kb_currencies)
		await Requisites.next()
	
	elif message.text == "Отмена":
		await state.reset_state()
		await message.answer("Создание QR-кода отменено", reply_markup = kb_default)
	
	else:
		public_key = message.text
		await state.update_data(pk = public_key)
		await message.answer("Количество монет(Amount)", reply_markup = kb_currencies)
		await Requisites.next()


# Получение количества призм
@db.message_handler(state = Requisites.amount)
async def get_amount_prizms(message: types.Message, state: FSMContext):
	if message.text == "Пропустить":
		await state.update_data(amount = "")
		await message.answer("Комментарий(Comment)", reply_markup = cancel_and_continue)
		await Requisites.last()
	
	elif message.text == "Отмена":
		await state.reset_state()
		await message.answer("Создание QR-кода отменено", reply_markup = kb_default)
		
	elif message.text == "Ввести в долларах($)":
		await message.answer("Введите сумму в долларах", reply_markup = cancel_and_continue)
		await Requisites.amount_dollars.set()

	elif message.text == "Ввести в рублях(₽)":
		await message.answer("Введите сумму в рублях", reply_markup = cancel_and_continue)
		await Requisites.amount_rubles.set()

	else:
		amount = message.text
		await state.update_data(amount = amount)
		await message.answer("Комментарий(Comment)", reply_markup = cancel_and_continue)
		await Requisites.last()


# Получение призм в долларах
@db.message_handler(state = Requisites.amount_dollars)
async def get_amount_dollars(message: types.Message, state: FSMContext):	
	if message.text == "Пропустить":
		await state.update_data(amount = "")
		await message.answer("Комментарий(Comment)")
		await Requisites.last()

	elif message.text == "Отмена":
		await state.reset_state()
		await message.answer("Создание QR-кода отменено", reply_markup = kb_default)

	else:
		importlib.reload(curs_usd)
		pzm = message.text
		try:
			amount = float(pzm) / float(curs_usd.pzm_curs)
			amount = round(amount, 2)
			await state.update_data(amount = str(amount))
			await message.answer(f"${message.text} = {amount} PZM")
			await message.answer("Комментарий(Comment)")
			await Requisites.last()
		except:
			await message.answer("Введите только число")


# Получение призм в рублях
@db.message_handler(state = Requisites.amount_rubles)
async def get_amount_rubles(message: types.Message, state: FSMContext):	
	if message.text == "Пропустить":
		await state.update_data(amount = "")
		await message.answer("Комментарий(Comment)")
		await Requisites.last()

	elif message.text == "Отмена":
		await state.reset_state()
		await message.answer("Создание QR-кода отменено", reply_markup = kb_default)

	else:
		importlib.reload(curs)
		pzm = message.text
		try:
			amount = float(pzm) / float(curs.pzm_curs)
			amount = round(amount, 2)
			await state.update_data(amount = str(amount))
			await message.answer(f"₽{message.text} = {amount} PZM")
			await message.answer("Комментарий(Comment)")
			await Requisites.last()
		except:
			await message.answer("Введите только число")


# Получение комментария, создание и отправка QR-кода
@db.message_handler(state = Requisites.comment)
async def get_comment(message: types.Message, state: FSMContext):
	if message.text == "Пропустить":
		await state.update_data(comment = "")
		data = await state.get_data()
		await message.answer("QR-код создаётся...", reply_markup = kb_delete)
	
	elif message.text == "Отмена":
		await state.reset_state()
		await message.answer("Создание QR-кода отменено", reply_markup = kb_default)
		return None
	
	else:
		comment = message.text
		await state.update_data(comment = comment)
		data = await state.get_data()
		await message.answer("QR-код создаётся...", reply_markup = kb_delete)

	pzm_site = "https://wallet.prizm.space/?to="
	
	if data["comment"] == "":
		qr_data = f"{pzm_site}{data['address']}:{data['pk']}:{data['amount']}"
	else:
		qr_data = f"{pzm_site}{data['address']}:{data['pk']}:{data['amount']}:{data['comment']}"
	
	qr_generate_transactions(qr_data, f"{message.from_user.id}.png")
	create_headline(data["address"], message.from_user.id)

	with open(f"{message.from_user.id}.png", "rb") as photo:
		await bot.send_photo(message.chat.id, photo, reply_markup = kb_default)

	os.remove(f"{message.from_user.id}.png")

	await state.finish()



# Состояние получения фотки, обработка и отправка данных юзеру
@db.message_handler(state = Scan.get_photo, content_types = ["photo", "text"])
async def get_photo(message, state: FSMContext):
	if message.text == "Отмена":
		await state.reset_state()
		await message.answer("Сканирование QR-кода отменено", reply_markup = kb_default)

	else:
		# C:\Users\User\AppData\Local\Programs\Python\Python38-32\Lib\site-packages\aiogram\types\mixins.py | line: 40
		await message.photo[-1].download(f"{message.from_user.id}.png")
		await message.answer("Обработка фотографии...", reply_markup = kb_delete)
		itog = scan_qr(f"{message.from_user.id}.png")
		await message.answer(itog, reply_markup = kb_default)
		os.remove(f"{message.from_user.id}.png")
		await state.finish()



time_now = datetime.today()
print(f"[{str(time_now)[:19]}]: Бот успешно запущен")

executor.start_polling(db, skip_updates = True)
