# -*- coding: utf-8 -*-
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram import Bot, types
from ctypes import *
from config import *
import pyautogui, asyncio, logging, keyboard, win32api, win32gui, win32con, getpass, psutil, random, mss, sys, os, io, re
#################################################################################################################################
storage = MemoryStorage()
bot = Bot(token=telegram_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO,)
#################################################################################################################################


class Is_access(BoundFilter):
	async def check(self, message: types.Message):
		if message.from_user.id in users_ids: return True
		await message.answer('<b>Ди нахуй э</b>')
		return False

class MadebyXENOBLADE(StatesGroup):
	keybind = State()
	settings = State()

def kb_menu():
	keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
	s=['🖼 Медиа','⚙ Управление ПК','Нажать кнопку','Настройки']
	for x in s: keyboard.insert(KeyboardButton(x))
	return keyboard

def kb_control():
	keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
	s=['🖼 Блокировка','⚙ Перезагрузка','🚫 Выключение ПК','🖼 Скрин','❌ Закрыть','🪛 Список процессов']
	for x in s: keyboard.insert(KeyboardButton(x))
	keyboard.add(KeyboardButton('🛡 Меню'))
	return keyboard

def kb_media():
	keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
	s=['🔊','🔇','🔉','⏪','⏯️','⏩']
	for x in s: keyboard.insert(KeyboardButton(x))
	keyboard.add(KeyboardButton('🛡 Меню'))
	return keyboard

def kb_keybinds():
	keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
	s=['Enter','Esc','Del','Backspace','Capslock','Space','Ctrl+Shift+Esc']
	for x in s: keyboard.insert(KeyboardButton(x))
	keyboard.add(KeyboardButton('🛡 Меню'))
	return keyboard

def kb_settings():
	keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
	gg=re.findall(r'notice_on_startup=[\S]{0,}',open('./config.py','r').read())[0]
	if 'True' in gg: s={'Выключить уведомления при старте':'act:disable_tg'}
	else: s={'Включить уведомления при старте':'act:enable_tg'}
	if os.path.exists(r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\MadebyXENOBLADE.bat'%getpass.getuser()): s['Удалить бота из автозапуска'] = 'act:del_from_auto'
	else: s['Добавить бота в автозапуск'] = 'act:add_to_auto'
	for x in s: keyboard.insert(InlineKeyboardButton(x,callback_data=s[x]))
	keyboard.add(InlineKeyboardButton('🛡 Меню',callback_data='act:close'))
	return keyboard
def kb_active_processes():
	keyboard = InlineKeyboardMarkup(row_width=1)
	s=[MadebyXENOBLADE for MadebyXENOBLADE in getWindowSizes()]
	for x in s: keyboard.insert(InlineKeyboardButton(x['text'],callback_data='act:close_proccess:%s'%x['hwnd']))
	keyboard.add(InlineKeyboardButton('🛡 Меню',callback_data='act:close'))
	return keyboard
def kb_processes():
	keyboard = InlineKeyboardMarkup(row_width=3)
	for x in set([p.name() for p in psutil.process_iter()]): keyboard.insert(InlineKeyboardButton(x,callback_data=f'act:close_process:{x}'))
	keyboard.add(InlineKeyboardButton('🛡 Меню',callback_data='act:close'))
	return keyboard
#################################################################################################################################
async def lock_user(): windll.LoadLibrary('user32.dll').LockWorkStation()
async def restart(): os.system('shutdown -r -t 0')
async def off(): os.system('shutdown -s -t 0')
async def screenshot():
	i='./%s.png'%random.randint(111111,9999999)
	mss.mss().shot(mon=-1, output=i)
	return i
async def up_volume(): keyboard.send('volume up')
async def mute_volume(): keyboard.send('volume mute')
async def down_volume(): keyboard.send('volume down')
async def prev_track(): keyboard.send("previous track")
async def resume_or_pause_track(): keyboard.send("play/pause media")
async def next_track(): keyboard.send("next track")
async def rewind_back_track(): keyboard.send("seekbackward")
async def rewind_forward_track(): keyboard.send("seekforward")
async def close(hwnd): 
	try:win32gui.CloseWindow(hwnd)
	except Exception as error: return {'status':False,'error_msg':error}
	return {'status':True}
def isRealWindow(hWnd):
	if not win32gui.IsWindowVisible(hWnd) or win32gui.GetParent(hWnd) != 0: return False
	if (((win32gui.GetWindowLong(hWnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOOLWINDOW) == 0 and win32gui.GetWindow(hWnd, win32con.GW_OWNER) == 0) or ((win32gui.GetWindowLong(hWnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_APPWINDOW != 0) and not win32gui.GetWindow(hWnd, win32con.GW_OWNER) == 0)):
		if win32gui.GetWindowText(hWnd): return True
	else: return False
def getWindowSizes():
	def callback(hWnd, windows):
		if not isRealWindow(hWnd): return
		windows.append({'text':win32gui.GetWindowText(hWnd),'hwnd':hWnd})
	windows = []
	win32gui.EnumWindows(callback, windows)
	return windows
async def use_keybind(keybind):
	try: keyboard.send(keybind)
	except Exception as error:	return {'status':False,'error_msg':error}
	return {'status':True}
async def add_to_startup(file_path=""):
	try:
		if file_path == "":
			file_path = os.path.abspath(__file__)
		with open(r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\MadebyXENOBLADE.bat'%getpass.getuser(), "w+") as bat_file:
			bat_file.write('python "%s" MadebyXENOBLADE'%file_path)
	except Exception as error: return {'status':False,'error_msg':error}
	return {'status':True}
async def del_from_startup():
	try:
		os.remove(r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\MadebyXENOBLADE.bat'%getpass.getuser())
	except Exception as error: return {'status':False,'error_msg':error}
	return {'status':True}
#################################################################################################################################
@dp.message_handler(CommandStart(), Is_access())
async def start(message: types.Message):
	uid=message.from_user.id
	uum=message.from_user.username
	await message.answer('<b>🛡 Меню</b>', reply_markup=kb_menu())

@dp.message_handler(Is_access(), content_types=['text'])
async def on_text(message: types.Message):
	mt=message.text
	await message.delete()

	if mt == '🛡 Меню':
		await message.answer('<b>🛡 Меню</b>', reply_markup=kb_menu())
		return
	elif mt == '🖼 Медиа':
		await message.answer('<b>🖼 Медиа</b>', reply_markup=kb_media())
		return
	elif mt == '⚙ Управление ПК':
		await message.answer('<b>⚙ Управление ПК</b>', reply_markup=kb_control())
		return
	elif mt == 'Нажать кнопку':
		await MadebyXENOBLADE.keybind.set()
		await message.answer('<b>Нажми кнопку из списка или отправь сообщением свою\n(Если хочешь нажать эту кнопку несколько раз, то после кнопки введи <code>*количествоповторений</code>, например: Backspace*7)</b>', reply_markup=kb_keybinds())
		return
	elif mt == 'Настройки':
		await message.answer('<b>Настройки</b>', reply_markup=kb_settings())
	elif mt == '🖼 Блокировка':
		await lock_user()
	elif mt == '⚙ Перезагрузка':
		await restart()
	elif mt == '🚫 Выключение ПК':
		await off()
	elif mt == '🖼 Скрин':
		path=await screenshot()
		await message.answer_document(open(path,'rb'))
		os.remove(path)
	elif mt == '❌ Закрыть':
		await message.answer('<b>Выберите <code>процесс</code> для завершения</b>', reply_markup=kb_active_processes())
	elif mt == '🪛 Список процессов':
		await message.answer('<b>Выберите <code>процесс</code> для завершения</b>', reply_markup=kb_processes())
	elif mt == '🔊':
		await up_volume()
	elif mt == '🔇':
		await mute_volume()
	elif mt == '🔉':
		await down_volume()
	elif mt == '⏪':
		await prev_track()
	elif mt == '⏯️':
		await resume_or_pause_track()
	elif mt == '⏩':
		await next_track()
	elif mt == '⬅️':
		await rewind_back_track()
	elif mt == '➡':
		await rewind_forward_track()

@dp.callback_query_handler()
async def callback(call: types.CallbackQuery):
	cd=call.data.split(':')
	if cd[0] == 'act':
		
		if cd[1] == 'close':
			await call.message.delete()
		
		elif cd[1] == 'close_proccess':
			gg = await close(int(cd[2]))
			if gg['status']:
				await call.answer('Закрыл')
			else:
				await call.message.answer('<b>Неудалось закрыть процесс.\nОписание ошибки: <code>%s</code></b>'%gg['error_msg'])

		elif cd[1] == 'close_process':
			try:
				for x in psutil.process_iter():
					if x.name() == cd[2]: x.kill()
				await call.answer('Закрыл все процессы')
				await call.message.edit_text('<b>Выберите <code>процесс</code> для завершения</b>',reply_markup=kb_processes())
			except psutil.AccessDenied: await call.message.answer('<b>Неудалось закрыть процесс.\nОписание ошибки: <code>Access Denied (Недостаточно прав)</code></b>')
			except Exception as error: await call.message.answer('<b>Неудалось закрыть процесс.\nОписание ошибки: <code>%s</code></b>'%error)

		elif cd[1] == 'add_to_auto':
			gg = await add_to_startup()
			if gg['status']:
				await call.answer('Добавил в автозапуск')
				await call.message.edit_text('<b>Настройки</b>',reply_markup=kb_settings())
			else: await call.message.answer('Неудалось добавить в автозапуск: %s'%gg['error_msg'])

		elif cd[1] == 'del_from_auto':
			gg = await del_from_startup()
			if gg['status']:
				await call.answer('Убрал из автозапуска')
				await call.message.edit_text('<b>Настройки</b>',reply_markup=kb_settings())
			else: await call.message.answer('Неудалось убрать из автозапуска: %s'%gg['error_msg'])

		elif cd[1] == 'enable_tg':
			try:
				with open('./config.py','r') as f:
					f=f.read()
					open('./config.py','w').write(f.replace('notice_on_startup=False','notice_on_startup=True'))
				await call.answer('Включил уведомления')
				await call.message.edit_text('<b>Настройки</b>',reply_markup=kb_settings())
			except Exception as error: await call.message.answer('Неудалось включить уведомления: %s'%error)

		elif cd[1] == 'disable_tg':
			try:
				with open('./config.py','r') as f:
					f=f.read()
					open('./config.py','w').write(f.replace('notice_on_startup=True','notice_on_startup=False'))
				await call.answer('Выключил уведомления')
				await call.message.edit_text('<b>Настройки</b>',reply_markup=kb_settings())
			except Exception as error: await call.message.answer('Неудалось выключить уведомления: %s'%error)

@dp.message_handler(state=MadebyXENOBLADE.keybind)
async def MadebyXENOBLADE_keybind(message: types.Message, state: FSMContext):
	keybind=message.text.replace(' ','+')
	
	if keybind == '🛡+Меню':
	
		await state.finish()
		await message.answer('<b>🛡 Меню</b>', reply_markup=kb_menu())
		return

	if keybind.find('*') >= 0:
		for x in range(int(keybind.split('*')[1])):
			act=await use_keybind(keybind.split('*')[0])
	else: act=await use_keybind(keybind)
	await message.delete()
	
	if act['status']:
		pass
	else:
		await message.answer('<b>Неудалось нажать "{}", причина ошибки: {}</b>'.format(keybind,act['error_msg']))
#################################################################################################################################
async def on_startup(dp):
	global bot_info
	bot_info=await bot.get_me()
	async def set_default_commands(dp):
		await dp.bot.set_my_commands([types.BotCommand("start", "Запустить бота")])
	await set_default_commands(dp)
	if len(sys.argv) >= 2:
		start_text='<b>ПК был запущен</b>'
	else:
		start_text='<b>Бот был запущен, не через автозапуск</b>'
	for id in users_ids:
		try: await bot.send_message(id, start_text)
		except: pass
if __name__ == '__main__':
	os.system('cls')
	try: executor.start_polling(dp, on_startup=on_startup)
	except Exception as error:
		print(error)
		logging.critical('Неверный токен бота!')