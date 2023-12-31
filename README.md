![<-foodgram workflow](https://github.com/iffilippov/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg)
## Foodgram, «Продуктовый помощник»

## Описание проекта
На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии
[![Python](https://img.shields.io/badge/-Python-464641?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![DjangoREST](https://img.shields.io/badge/Django-REST-464646?style=flat-square&logo=django&logoColor=white&color=ff1709&labelColor=gray)](https://www.django-rest-framework.org/)
[![Postgres](https://img.shields.io/badge/Postgres-464646?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)

##  Запуск проекта в Docker
Клонировать репозиторий:

```
git clone git@github.com:iffilippov/foodgram-project-react.git
```

Создать infra/.env
Пример заполнения infra/.env:

```
SECRET_KEY=Секретный_ключ
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

Запустить docker-compose:

```
docker-compose up -d
```

Будут созданы и запущены в фоновом режиме необходимые для работы приложения
контейнеры (foodgram-db, foodgram-backend, foodgram-frontend, foodgram-nginx).

Внутри контейнера foodgram-backend выполнить миграции, создать суперпользователя и собрать статику:

```
docker-compose exec foodgram-backend python manage.py migrate
docker-compose exec foodgram-backend python manage.py createsuperuser
docker-compose exec foodgram-backend python manage.py collectstatic --no-input 
```

## Запуск проекта локально
Клонируем проект
```
git clone git@github.com:iffilippov/foodgram-project-react.git
```

Добавляем файл infra/.env с настройками БД. Например:
```
SECRET_KEY=Секретный_ключ
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

Переходим в папку с бэкендом.
Создаем и активируем виртуальное окружение
```
cd .../foodgram-project-react/backend
python -m venv venv
source venv/Scripts/activate
```

Устанавливаем зависимости из файла requirements.txt
```
pip install -r requirements.txt
```

При необходимости создаем и выполняем миграции, заполняем базу ингредиентов, создаем суперпользователя
```
cd foodgram/
python manage.py makemigrations
python manage.py migrate
python manage.py import_csv
python manage.py createsuperuser
```

Запускаем проект

из папки infra выполняем
```
docker-compose up -d db
```

из папки frontend выполняем
```
npm i
npm run start
```

из папки foodgram выполняем
```
python manage.py runserver
```

### Автор проекта
[Иван Филиппов](https://www.linkedin.com/in/iffilippov/)
