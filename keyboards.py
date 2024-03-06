from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

command_list = KeyboardButton(text="Список команд")
giveup = KeyboardButton(text="Сдаться")
newtask = KeyboardButton(text="Новый вопрос")
top_players = KeyboardButton(text="Список лучших")

kb_default = ReplyKeyboardMarkup(resize_keyboard=True)
kb_no_giveup = ReplyKeyboardMarkup(resize_keyboard=True)

kb_default.add(newtask, giveup).add(command_list, top_players)
kb_no_giveup.add(newtask).add(command_list, top_players)