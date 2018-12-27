# j_searcher
Для запуска:
1. Открыть командную строку в директории с manage.py
2. Установить необходимые сторонние пакеты ``` pip install -r requirements.txt ```
3. Создать базу данных для приложения
``` 
python manage.py makemigrations
python manage.py migrate
```
4. Добавить в базу фикстуры
``` 
python manage.py dumpdata
```
5. Запустить сервер Django
``` 
python manage.py runserver
```
6. Открыть сайт по адресу указанному при запуске, стандартно http://127.0.0.1:8000/
