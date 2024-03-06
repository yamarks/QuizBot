import os

import pymongo
from dotenv import load_dotenv


def read_quiz_files(directory='quiz-questions') -> None:
    for file in os.listdir(os.path.abspath(directory)):
        with open(f'{directory}/{file}', 'r', encoding='utf-8') as file:
            text = file.read()
            yield text


def upload_questions_into_mongodb(db, coll) -> None:
    for text in read_quiz_files():
        counter = coll.count_documents({})

        sections_text = text.split('\n\n')

        for section in sections_text:
            if section.strip().startswith('Вопрос'):
                question = ' '.join(section.strip().splitlines()[1:])
                continue

            if section.strip().startswith('Ответ'):
                answer = ' '.join(section.strip().splitlines()[1:])
                counter += 1
                coll.insert_one({
                    'id': counter,
                    'question': question,
                    'answer': answer
                })


def main() -> None:
    load_dotenv()
    client = pymongo.MongoClient(os.getenv("MONGODB"))
    db = client["telegram"]
    coll = db["questions"]
    upload_questions_into_mongodb(db, coll)
    # Create the users collection if it doesn't exist
    if 'users' not in db.list_collection_names():
        coll = db.create_collection('users')

    # Close the connection
    client.close()


if __name__ == '__main__':
    main()