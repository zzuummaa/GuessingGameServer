# Берем нужный базовый образ
FROM python:3.8-alpine
# Копируем все файлы из текущей директории в /app контейнера
COPY ./ /app
# Устанавливаем все зависимости
RUN apk update && apk add --no-cache build-base openssl-dev libffi-dev && pip install -r /app/requirements.txt --no-cache-dir
# Говорим контейнеру какой порт слушай
EXPOSE 80
# Монтируем папку /db для совместного использования с контейнером
VOLUME /db
# В качестве альтернативы distutils можно просто указать что выполнить
CMD python /app/app.py