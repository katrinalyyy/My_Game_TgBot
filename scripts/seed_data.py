import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
import os
from dotenv import load_dotenv

from app.store.database.models import Category, Question

load_dotenv()

DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)


async def seed_database():
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(func.count()).select_from(Category))
        count = result.scalar()
        
        if count > 0:
            print(f"⚠️  В базе уже есть {count} категорий. Пропускаем заполнение.")
            return
        
        print("📝 Добавляем категории...")
        
        categories_data = [
            Category(name='История', description='Вопросы по истории России и мира'),
            Category(name='География', description='Вопросы о странах, городах и природе'),
            Category(name='Наука', description='Физика, химия, биология'),
            Category(name='Спорт', description='Всё о спорте и спортсменах'),
            Category(name='Культура', description='Литература, музыка, живопись'),
        ]
        
        session.add_all(categories_data)
        await session.commit()
        
        print("✅ Категории добавлены!")
        print("📝 Добавляем вопросы...")
        
        questions_data = [
            Question(category_id=1, question_text='В каком году началась Великая Отечественная война?', 
                    answer_text='1941', difficulty=100),
            Question(category_id=1, question_text='Кто был первым президентом России?', 
                    answer_text='Борис Ельцин', difficulty=200),
            Question(category_id=1, question_text='В каком году пал Берлинский Мур?', 
                    answer_text='1989', difficulty=300),
            
            Question(category_id=2, question_text='Столица Австралии?', 
                    answer_text='Канберра', difficulty=100),
            Question(category_id=2, question_text='Самая длинная река в мире?', 
                    answer_text='Амазонка', difficulty=200),
            Question(category_id=2, question_text='На каком материке нет рек?', 
                    answer_text='Антарктида', difficulty=300),
            
            Question(category_id=3, question_text='Что тяжелее: килограмм железа или килограмм ваты?', 
                    answer_text='Одинаково', difficulty=100),
            Question(category_id=3, question_text='Химический символ золота?', 
                    answer_text='Au', difficulty=200),
            Question(category_id=3, question_text='Сколько планет в Солнечной системе?', 
                    answer_text='8', difficulty=300),
            
            Question(category_id=4, question_text='Сколько игроков в футбольной команде на поле?', 
                    answer_text='11', difficulty=100),
            Question(category_id=4, question_text='В каком виде спорта используется шайба?', 
                    answer_text='Хоккей', difficulty=200),
            Question(category_id=4, question_text='Кто выиграл чемпионат мира по футболу 2018?', 
                    answer_text='Франция', difficulty=300),
            
            Question(category_id=5, question_text='Кто написал "Война и мир"?', 
                    answer_text='Лев Толстой', difficulty=100),
            Question(category_id=5, question_text='Кто нарисовал "Мону Лизу"?', 
                    answer_text='Леонардо да Винчи', difficulty=200),
            Question(category_id=5, question_text='В каком городе находится Эрмитаж?', 
                    answer_text='Санкт-Петербург', difficulty=300),
        ]
        
        session.add_all(questions_data)
        await session.commit()
        
        print("✅ Вопросы добавлены!")
        print(f"✅ Всего добавлено: {len(categories_data)} категорий, {len(questions_data)} вопросов")
    
    await engine.dispose()


if __name__ == "__main__":
    print("🚀 Запуск заполнения базы данных...")
    asyncio.run(seed_database())
    print("🎉 Готово!")