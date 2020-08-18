
def create_tables(cursor):
    cursor.execute("""CREATE TABLE users (
                        user_id integer primary key autoincrement,
                        user_name text
                      )""")

    cursor.execute("""CREATE TABLE translates (
                        word_id integer primary key autoincrement,
                        ru_word text,
                        en_word text
                      )""")

    translates = [
        ("Арбуз", "Watermelon"),
        ("Волк", "Wolf"),
        ("Звезда", "Star"),
        ("Блин", "Pancake"),
        ("Поток", "Flow"),
        ("Палатка", "Tent"),
        ("Потолок", "Ceiling"),
        ("Доска", "Board"),
        ("Собака", "Dog"),
        ("Слон", "Elephant"),
        ("Стол", "Table"),
        ("Шкаф", "Cupboard"),
        ("Лес", "Forest"),
        ("Тарелка", "Plate"),
        ("Лифт", "Elevator"),
        ("Лестница", "Stairs"),
        ("Зоопарк", "Zoo"),
        ("Кот", "Cat")
    ]

    cursor.executemany("""INSERT INTO translates(ru_word, en_word) values(?,?);""", translates)
