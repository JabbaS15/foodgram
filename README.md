# Foodgram

![example workflow](https://github.com/JabbaS15/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)
![django version](https://img.shields.io/badge/Django-3.2.13-green)
![python version](https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9-green)
## Описание проетка [jabba.ddns.net](http://127.0.0.1:8000/api/):

## Tecnhologies:
- Python 3.7
- Django 3.2.13
- Django REST framework 3.13
- Nginx
- Docker
- Postgres


## Как запустить проект:
- - Загрузите проект с помощью SSH
```
git@github.com:JabbaS15/foodgram-project-react.git
```
- Подключиться к вашему серверу:
```
ssh <server user>@<server IP>
```
- Установите Докер на свой сервер
```
sudo apt install docker.io
```
- Получить разрешения для docker-compose
```
sudo chmod +x /usr/local/bin/docker-compose
```
- Создайте каталог проекта
```
mkdir foodgram && cd foodgram/
```
- Создайте env-файл
```
touch .env
```
- Заполните env-файл
```
DEBUG = False
SECRET_KEY = указываем секретный ключ
ALLOWED_HOSTS = указываем IP сервера
DB_ENGINE = указываем c nbgjv БД
DB_NAME = имя базы данных
POSTGRES_USER = логин для подключения к базе данных
POSTGRES_PASSWORD = пароль для подключения к БД (установите свой)
DB_HOST = название сервиса (контейнера)
DB_PORT = порт для подключения к БД
```
- Скопируйте файлы из 'infra/' с ПК на ваш сервер
```
scp infra/* <server user>@<server IP>:/home/<server user>/foodgram/
```
- Запустите docker-compose
```
sudo docker-compose up -d
```