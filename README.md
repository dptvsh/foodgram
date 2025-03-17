[![Main Foodgram workflow](https://github.com/dptvsh/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/dptvsh/foodgram/actions/workflows/main.yml)

#  Проект Foodgram

Сайт [food-gram.sytes.net](https://food-gram.sytes.net/) позволяет выкладывать различные рецепты, подписываться на других авторов, добавлять рецепты в избранное или список покупок, а также скачать собственный список покупок в формате txt.

## Отличие версий

В проекте представлено две версии, обычная (для разработки) и production, для каждой из которых написан свой compose файл (docker-compose и docker-compose.production соответственно). Основное их различие заключается в том, что в версии для разработки образы билдятся при каждом запуске, что удобно при отладке, в то время как production версия подтягивает готовые и протестированные образы из Docker Hub.

Поэтому, если вы хотите внести какие-либо изменения в код, лучше использовать версию для разработки, чтобы внесенные изменения были отражены в пересобранных образах. Во всех остальных случаях следует использовать production версию.

## Установка проекта

1. Клонировать репозиторий и перейти в него в командной строке:

   ```git clone https://github.com/dptvsh/foodgram.git```

   ```cd foodgram```

2. Создать и заполнить .env файл по образцу.

3. Установить Docker, если он еще не установлен.

## Запуск проекта

### Локально

1. Перейти в папку infra:

   ```cd infra```

2. Запустить контейнеры в фоновом режиме:
  
   ```docker compose up -d``` *# Обычная версия*

   ```docker compose -f docker-compose.production.yml up -d``` *# Production версия*

3. Последовательно собрать и скопировать статику:

   *Для обычной версии:*

   ```docker compose exec backend python manage.py collectstatic```

   ```docker compose exec backend cp -r /app/collected_static/. /backend_static/static/```

   *Для production версии:*

   ```docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic```

   ```docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/```

4. Применить миграции:

   ```docker compose exec backend python manage.py migrate``` *# Обычная версия*

   ```docker compose -f docker-compose.production.yml exec backend python manage.py migrate``` *# Production версия*

### Удаленно

1. Запустить контейнеры в фоновом режиме:
  
   ```sudo docker compose -f docker-compose.production.yml up -d```

2. Последовательно собрать и скопировать статику:

   ```sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic```

   ```sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/```

3. Применить миграции:

   ```sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate```

## Технологический стек

- **Django**: Веб-фреймворк для разработки бэкенд части.
- **React**: Библиотека для разработки фронтенд части.
- **PostgreSQL**: СУБД для хранения и использования информации.
- **Nginx**: ПО для организации веб-сервера.
- **Docker**: ПО для контейнеризации приложений.

### Автор

Дарина Потапова
