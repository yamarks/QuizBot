import datetime
import logging
import os
import re
import db
import pytz
import pymongo


def remove_comments(answer: str) -> str:
	return re.sub(r"[\(\[].*?[\)\]]", "", answer).strip()


def get_answer_question(user_id: int, db: pymongo.database.Database, source='tg') -> str:
	# Get the collection
	coll = db['users']

	# Find the user's document in the collection
	user_doc = coll.find_one({'id': f'user_{source}_{user_id}'})
	# Get the last_asked_question field from the document
	question_num = user_doc.get('last_asked_question')
	print(question_num)

	# Find the question document in the questions collection
	coll = db['questions']
	qa = coll.find_one({'id': question_num})
	# Get the answer field from the question document
	answer = qa.get('answer')

	return answer



def _create_database() -> None:
	# try to create .db file
	if not os.path.isfile("score.db"):
		file = open("score.db", "x")
		file.close()
	# try to connect to the database
	try:
		db.sqlite3.connect(db.db_name)
		db.cursor.execute(
			"SELECT name FROM sqlite_master WHERE type='table' AND name='players'").fetchone()[0]
		logging.debug(f"Database '{db.db_name}' is ok.")
	except:
		logging.debug(f"Table 'players' was not found.")
		logging.debug(f"Creating...")
		db.cursor.execute("CREATE TABLE players (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER UNIQUE NOT NULL, score INTEGER DEFAULT (0) NOT NULL, jointime DATETIME DEFAULT ((DATETIME('now'))) NOT NULL, profile_name TEXT, username TEXT UNIQUE ON CONFLICT ABORT, attempt INTEGER NOT NULL DEFAULT (0), attempt_time DATETIME NOT NULL DEFAULT ((DATETIME('now'))), is_skip INTEGER DEFAULT (0) NOT NULL)")
		logging.debug(f"Created.")


def _create_user(user_id: int, username: str, fullname: str) -> None:
	"""Проверяет наличие игрока и добавляет его в базу, если игрока нет"""
	if (not db.user_exists(user_id)):
		db.add_user(user_id, username, fullname)


def _get_now_datetime() -> datetime.datetime:
	"""Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
	moscow_timezone = pytz.timezone("Europe/Moscow")
	moscow_time = datetime.datetime.now(moscow_timezone)
	# moscow_time_str = moscow_time.strftime("%Y-%m-%d %H:%M:%S")
	return moscow_time

def format_text(text: str) -> str:
	# Regex pattern correction
	return re.sub(r'\\n', '\n', text)


def has_extra_attempts(user_id: int) -> bool:
	"""Проверяет оставшиеся попытки пользователя с учётом времени и общих попыток"""
	current_time = _get_now_datetime()
	database_time_str = db.get_time(user_id)
	attempt_count = db.get_attempts(user_id)

	# Convert the string to a datetime object
	database_time = datetime.datetime.strptime(
		database_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone("Europe/Moscow"))
	# Calculate the difference between the current time and the time in the database
	time_difference = current_time.minute - database_time.minute
	delta = datetime.timedelta(minutes=3)
	if (attempt_count == 0 or attempt_count < 3):
		return True
	elif (time_difference < int(delta.total_seconds()/60) and attempt_count >= 3):
		return False
	else:
		db.reset_attempt(user_id)
		return True