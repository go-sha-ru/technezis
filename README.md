# Тестовое задание Python
## Технезис


## Установка uv 

### Для Windows:
```shell
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Для linux:
```shell
  curl -LsSf https://astral.sh/uv/install.sh | sh
```


### Склонировать репозиторий

### Установить все зависимости

```shell
    uv sync
```

### Скопировать файл .env.example в .env и заполнить данными

### Запустить бота

```shell
uv run main.py
```

### Зайти в канал телеграм бота и выполнить команду /start

### Прикрепить документ excel в телеграм. Для примера есть файл [data.xlsx](data.xlsx)