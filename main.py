import logging
import os
import random

import pymongo
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv

import db
from keyboards import kb_default, kb_no_giveup
from utils import (_create_database, _create_user, format_text,
				   get_answer_question, has_extra_attempts, remove_comments)

load_dotenv()

bot = Bot(os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher(bot)

client = pymongo.MongoClient(os.getenv("MONGODB"))
mongodb = client['telegram']

logging.basicConfig(level=logging.DEBUG)

HELP_COMMAND = """
/start — запуск бота
/help — список команд
/task — сыграть в викторину
/top — список лучших игроков
"""


async def on_startup(_) -> None:
	print("All systems nominal.")


@dp.message_handler(commands=["start", "старт", "начать"])
async def start_command(message: types.Message) -> None:
	_create_user(message.from_user.id, message.from_user.username,
				 message.from_user.full_name)
	await message.answer(
		text="Привет! Нажми «Новый вопрос» для игры в викторину.\nЛибо введи /task",
		reply_markup=kb_no_giveup)
	await message.delete()


@dp.message_handler(regexp="^Список лучших$|/top")
async def top_command(message: types.Message) -> None:
	top_list = db.show_top()
	answer = "Хорошо, что спросил!\n\n🌟 Аллея славы 🌟\n"
	for place, (username, score) in enumerate(top_list):
		answer += f"{place+1} место — @{username} ({score})\n"
	await message.reply(text=answer)


@dp.message_handler(regexp="^Список команд$|/help|/помощь|/команды")
async def help_command(message: types.Message) -> None:
	await message.answer(text=HELP_COMMAND)


@dp.message_handler(regexp="^Новый вопрос$|/task")
async def task_command_btn(message: types.Message) -> types.Message | None:
	if (not has_extra_attempts(message.from_user.id)):
		return await message.answer("Ты израсходовал все попытки. Возьми перерыв на 3 минуты.")
	db.give_answer(message.from_user.id, 0)
	await handle_new_question_request(message, mongodb)


@dp.message_handler(Text(equals="Сдаться"))
async def handle_give_up(message: types.Message) -> None:
	user_id = message.from_user.id
	answer = get_answer_question(user_id, mongodb)
	await message.answer(
		text=f"Вот тебе правильный ответ: {answer}\n\nЧтобы продолжить нажми «Новый вопрос»",
		reply_markup=kb_no_giveup
	)
	db.add_attempt(user_id)
	db.give_answer(user_id, 1)


@dp.message_handler()
async def handle_solution_attempt(message: types.Message) -> None:
	user_id = message.from_user.id
	# Early return, проверяем отвечал ли игрок на вопрос и есть ли у него попытки
	if db.is_skip(user_id):
		return
	if not has_extra_attempts(user_id):
		return await message.answer("Ты израсходовал все попытки. Возьми перерыв.")
	answer = get_answer_question(user_id, mongodb)
	user_response = message.text
	correct_answer = remove_comments(answer).lower().strip('.')
	logging.debug(
		f"{message.from_user.username}'s response: {user_response.lower()} |"
		f"correct_answer: {correct_answer}"
	)
	if user_response.lower() == correct_answer.lower():
		await message.reply(
			text="Правильно! Поздравляю!\nДля следующего вопроса нажми «Новый вопрос».",
			reply_markup=kb_no_giveup
		)
		db.add_score(user_id)
		db.give_answer(user_id, 1)
	else:
		await message.answer("Неправильно! Подумай ещё.")
	db.add_attempt(user_id)


async def handle_new_question_request(message: types.Message, mongodb: pymongo.database.Database) -> None:
	# Get the collection
	coll = mongodb['questions']

	# Choose a random question from the collection
	questions_count = coll.count_documents({})
	question_num = random.randint(1, questions_count)

	# Retrieve the question and answer from the collection
	question_doc = coll.find_one({'id': question_num})
	question = question_doc.get('question')
	# Save the question number in the user's data in the collection
	coll = mongodb["users"]
	coll.update_one(
		{'id': f"user_tg_{message.from_user.id}"},
		{'$set': {'last_asked_question': question_num}},
		upsert=True
	)
	
	# Console debug messages
	logging.debug(
		f"question: {question} "
		f"answer: {question_doc.get('answer')}"
	)
	# Send the question to the user
	await message.answer(text=format_text(question), reply_markup=kb_default)

if __name__ == "__main__":
	_create_database()
	executor.start_polling(
		dispatcher=dp,
		skip_updates=True,
		on_startup=on_startup)