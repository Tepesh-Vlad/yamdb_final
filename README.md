![workflow](https://github.com/Tepesh-Vlad/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
# API_YamDB
REST API для сервиса YaMDb — базы отзывов о фильмах, книгах и музыке.

## Описание
Проект YaMDb собирает отзывы пользователей на произведения. Произведения делятся на категории: «Книги», «Фильмы», «Музыка».
Произведению может быть присвоен жанр. Добавлять произведения, категории и жанры может только администратор
Читатели оставляют к произведениям текстовые отзывы и выставляют произведению рейтинг (оценку в диапазоне от одного до десяти).
из множества оценок автоматически высчитывается средняя оценка произведения.

## Стек технологий
- Python с использованием Django REST Framework
- Simple JWT
- django-filter 
- SQLite3
- система управления версиями - git

### Запуск проекта в dev-режиме
Склонируйте репозиторий. Находясь в папке с кодом создайте виртуальное окружение `python -m venv venv`, активируйте его (Windows: `source venv\scripts\activate`; Linux/Mac: `sorce venv/bin/activate`), установите зависимости `python -m pip install -r requirements.txt`.

Для запуска сервера разработки,  находясь в директории проекта выполните команды:
```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Проект запущен и доступен по адресу (http://127.0.0.1:8000/)
Полная документация доступна по адресу http://127.0.0.1/redoc/

## Алгоритм регистрации пользователей
- Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами email и username на эндпоинт /api/v1/auth/signup/
- YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на адрес email
- Пользователь отправляет POST-запрос с параметрами username и confirmation_code на эндпоинт /api/v1/auth/token/, в ответе на запрос ему приходит token (JWT-токен).

## Ресурсы API YaMDb
- Ресурс AUTH: аутентификация.
- Ресурс USERS: пользователи.
- Ресурс TITLES: произведения, к которым пишут отзывы (определённый фильм, книга или песня).
- Ресурс CATEGORIES: категории (типы) произведений («Фильмы», «Книги», «Музыка»).
- Ресурс GENRES: жанры произведений. Одно произведение может быть привязано к нескольким жанрам.
- Ресурс REVIEWS: отзывы на произведения. Отзыв привязан к определённому произведению.
- Ресурс COMMENTS: комментарии к отзывам. Комментарий привязан к определённому отзыву.

## Примеры запросов к API

### Добавление нового отзыва:
```
url = 'http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/'
data = {"text": "string", "score": 1}
headers = {'Authorization': 'Bearer your_token'}
```
### Ответ API_YamDB:
```
Статус- код 200
{
  "id": 0,
  "text": "string",
  "author": "string",
  "score": 1,
  "pub_date": "2019-08-24T14:15:22Z"
}
```
### Получение комментария к отзыву:
```
url = 'http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/'
```
### Ответ API_YamDB:
```
Статус- код 200
{
  "id": 0,
  "text": "string",
  "author": "string",
  "pub_date": "2019-08-24T14:15:22Z"
}
```

### итоговый проект курса выполнили:
- Виктор Баранов
- Владислав Широков
- Елизавета Огай

ip: 51.250.6.32
