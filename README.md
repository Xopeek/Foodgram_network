# Всем привет!
### Сервис Foodgram - это продуктовый помощник, который упрощает жизнь многим людям, начиная с обычных студентов и заканчивая профессиональными поварами.
### Чем же он так полезен? Вот список:
- Здесь можно публиковать свои рецепты.
- Следить за друзьями и близкими, чтобы узнать, что они готовят.
- Быстро найти рецепт на обед или ужин.
- Главное — все ингредиенты можно скачать одним кликом и смело идти в магазин.

### Как же запустить этот чудесный сервис у себя?
1. Клонируйте репозиторий:
git clone git@github.com:Xopeek/foodgram-project-react.git
2. Настройте свой сервер:
- Переместите свой docker-compose.yml на сервер.
- Переместите файл nginx.
- Создайте и наполните файл .env.
3. Установите Docker на сервере:
- sudo apt update
- sudo apt install curl
- curl -fSL https://get.docker.com -o get-docker.sh
- sudo sh ./get-docker.sh
- sudo apt-get install docker-compose-plugin 
4. Создайте и загрузите данные на DockerHub (на локальном ПК):
- cd backend
- docker build -t ваш_username/foodgram_backend .
- docker push ваш_username/foodgram_backend
- cd ..
- cd frontend
- docker build -t ваш_username/foodgram_frontend .
- docker push ваш_username/foodgram_frontend
5. На сервере поднимите контейнеры командой:
- docker-compose up -d --build
6. Далее создайте миграции, соберите статику и создайте суперпользователя:
- docker-compose exec backend python manage.py makemigrations
- docker-compose exec backend python manage.py migrate
- docker-compose exec backend python manage.py collectstatic
- docker-compose exec backend python manage.py createsuperuser
7. Пользуйтесь на здоровье!

# Пример заполнения файла .env:
```python
POSTGRES_DB='foodgram'
POSTGRES_USER='foodgram_u'
POSTGRES_PASSWORD='foodgram_u_pass'
DB_HOST='db'
DB_PORT='5432'
SECRET_KEY='secret'  
ALLOWED_HOSTS='127.0.0.1, backend'
DEBUG = False
```

# Технологии:
- Django
- DRF
- Docker
- Postgres
- Pillow
- Nginx
- Gunicorn
- Djoser

# Вечно ваш Семляков Игорь (Xopek) :)
