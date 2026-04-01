# FileProcessingService

Асинхронный сервис для обработки PDF и JPG файлов.  
Стэк: FastAPI, PostgreSQL, Redis, RabbitMQ, Celery, S3.  
Использует LLM для обработки

Основные endpoint'ы
```
POST /api/v1/files
Принимает multipart/form-data
Отправляет файл на обработку, возвращает file_id

GET /api/v1//files/{file_id}/status
Статусы: uploaded, processing. done, failed

GET /api/v1//files/{file_id}/result
Отправляет результат обработки файла в формате JSON
```

## Установка (Linux)
1. Клонирование репозитория 

```
git clone https://github.com/hellart1/FileProcessingService.git
cd FileProcessingService
cp .env.example .env
```

2. Создать .env файл на основе .env.example
```
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
POSTGRES_DB=fileproc

RABBITMQ_DEFAULT_VHOST=rabbit
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
REDIS_URL=redis://redis:6379/0

LLM_API_URL=http://127.0.0.1:1234/v1

AWS_ACCESS_KEY_ID=access_key
AWS_SECRET_ACCESS_KEY=secret_key
AWS_BUCKET_NAME=fileprocessing
AWS_ENDPOINT_URL=https://storage.yandexcloud.net
AWS_REGION_NAME=ru-central1
```
Важно: Отредактируйте .env, указав доступы к S3 и URL локальной LLM

4. Запустить Docker Compose

```docker-compose up --build```

4. API DOCS будет доступен на:

```http://localhost:8000/docs```
