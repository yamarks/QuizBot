
# Бот-викторина

Бот-викторина для Telegram с базой данных для хранения результатов. 

## Как установить
Необходим Python 3.7-3.9, Python 3.10+ работать __не будет__.

1. Клонируем проект себе на ПК
```
git clone https://github.com/yamarks/QuizBot.git
```
2. Создаём виртуальное окружение в папке с проектом
```
cd QuizBot
python3 -m venv .venv
source .venv/Scripts/activate
```
3. Устанавливаем зависимости проекта
```
pip install -r requirements.txt
```
## Как запустить
1. Создать бота в Telegram. 
Бот в Telegram создается при помощи другого бота под названием [@BotFather](https://t.me/@Botfather). 
Отправляем ему команду /newbot, выбираем имя, которое будет отображаться в списке контактов, и адрес. 
BotFather пришлет в ответ сообщение с токеном.

2. Заведите аккаунт в Redislabs и создайте базу данных. После создания вы получите адрес базы данных вида: `redis-13965.f18.us-east-4-9.wc1.cloud.redislabs.com`, его порт вида: `16635` (порт указан прямо в адресе, через двоеточие) и его пароль.

3. Создайте `.env` файл c необходимыми параметрами, такими как:
```
TELEGRAM_TOKEN=
REDIS_HOST=
REDIS_PORT=
REDIS_PASSWORD=
```

## Добавление вопросов

Добавление вопросов для бота
Для хранения вопросов используется база данных Redis, которая распологается в облаке [Redislabs](https://app.redislabs.com/#/). Для загрузки вопросов в Redis используйте скрипт `redis_questions_upload.py`.

Вопросы для ботов должны размещаться в текстовых файлах с кодировкой `KOI-8R`. Сами файлы должны находиться в каталоге quiz-questions. Разделы файла (вопросы и ответы) должны быть разделены двумя символами перевода строки `\n\n`. Пример:

Вопрос 1:\
Герой фантастической книги Энди Уэйра "Марсианин" - можно сказать,
современный Робинзон: оставленный на Марсе с минимумом припасов, он
должен продержаться четыре года до прибытия экспедиции. Через несколько
месяцев герой выясняет, что, по современному земному законодательству,
является колонизатором Марса, поскольку первым стал заниматься на Марсе
ТАКИМИ работами. Какими именно?

Ответ:
Сельскохозяйственными.

Вопрос 2:\
Молодой джентльмен викторианской эпохи мог увидеться и перекинуться
словом с понравившейся девушкой в отсутствие свахи, тетушки, матушки или
служанки только во время прогулки по так называемой Rotten-Row
[рОттен-рОу] - посыпанной песком дорожке в Гайд-парке: девушек отпускали
без провожатого, считая, что они как бы находятся под присмотром... Кого?

Ответ:
Лошади.

