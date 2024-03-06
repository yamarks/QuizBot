import sqlite3
import datetime

from utils import _get_now_datetime


db_name = "score.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

def user_exists(user_id: int) -> bool:
	"""Проверяем есть ли пользователя в базе"""
	result = cursor.execute("SELECT user_id FROM players WHERE user_id = ?", (user_id,))
	return bool(len(result.fetchall()))

def get_user_id(user_id: int) -> int:
	"""Достаем id пользователя в базе по его user_id"""
	result = cursor.execute("SELECT id FROM players WHERE user_id = ?", (user_id,)).fetchone()[0]
	return result

def add_user(user_id: int, username: str, profile_name: str) -> None:
	"""Добавляем пользователя в базу"""
	cursor.execute("INSERT INTO players (user_id, username, profile_name) VALUES (?, ?, ?)", (user_id,username,profile_name))
	return conn.commit()

def add_score(user_id: int):
	"""Создаем запись о счёте пользователя"""
	cursor.execute("UPDATE players SET score = score + 10 WHERE id = ?", (get_user_id(user_id),))
	return conn.commit()

def show_top() -> list:
	"""Показывает список лучших"""
	top_player = cursor.execute("SELECT username, score FROM players ORDER BY score DESC LIMIT 10").fetchall()
	return top_player

def add_attempt(user_id: int) -> None:
	"""Записывает количество попыток пользователя и время последней"""
	cursor.execute("UPDATE players SET attempt = attempt + 1 WHERE id = ?", (get_user_id(user_id),))
	cursor.execute("UPDATE players SET attempt_time = ? WHERE id = ?", (_get_now_datetime().strftime("%Y-%m-%d %H:%M:%S"), get_user_id(user_id)))
	return conn.commit()

def is_skip(user_id: int) -> bool:
	"""Проверяет ответил ли пользователь на вопрос. Если да — пропускает ответы."""
	check = cursor.execute("SELECT is_skip FROM players WHERE id = ?", (get_user_id(user_id),)).fetchone()[0]
	return check

def give_answer(user_id: int, answer: int) -> None:
	"""Записывает если пользователь ответил на вопрос"""
	cursor.execute("UPDATE players SET is_skip = ? WHERE id = ?", (answer, get_user_id(user_id)))
	return conn.commit()

def reset_attempt(user_id: int) -> None:
	"""Обнуляет количество попыток пользователя"""
	cursor.execute("UPDATE players SET attempt = 0 WHERE id = ?", (get_user_id(user_id),))
	return conn.commit()

def get_attempts(user_id: int) -> int:
	"""Возвращает количество попыток пользователя"""
	db_attempts = cursor.execute("SELECT attempt FROM players WHERE id = ?", (get_user_id(user_id),)).fetchone()[0]
	return db_attempts

def get_time(user_id: int) -> datetime:
	"""Возвращает время последней попытки пользователя"""
	time = cursor.execute("SELECT attempt_time FROM players WHERE id = ?", (get_user_id(user_id),)).fetchone()[0]
	return time