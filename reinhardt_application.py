from infrastructure.db.postgres import init_database


def main():
    # Инициализация БД
    init_database()

    # Дальнейший запуск приложения
    # ...


if __name__ == "__main__":
    main()