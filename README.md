# Выполнение тестового задания
[Ссылка на ТЗ](https://docs.google.com/forms/d/1MEA7sc91CsidkFMxDwCEZFbq4LgLqfbcXNoFIG-23yc/viewform?edit_requested=true)

Как выглядит config.py:
```python
import os
server_type = 'local'

os.environ['SSH_HOST'] = 'Server ID'
os.environ['SSH_PORT'] = '22'
os.environ['SSH_USER'] = 'ssh user'
os.environ['SSH_PASS'] = 'ssh password'
```

База данных PostgreSQL находится на сервере, поэтому было реализовано подключение к ней с помощью sshtunnel.

Запуск API с помощью команды:
```bash
uvicorn main:app
```

В папке cron находится скрипт для очистки неиспользуемых файлов

Команда установки для крона (в 00:00 каждый день):
```bash
0 0 * * * /usr/bin/python3 /path/to/cron/clean.py >> /path/to/cron/cleanup.log 2>&1
```