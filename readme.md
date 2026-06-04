# Интернет-магазин мебели

## Описание проекта
Интернет-магазин мебели с бэкендом на Django REST Framework и десктопным клиентом на Tkinter.

## Функциональность
- Авторизация и регистрация клиентов (пароли в виде хеша)
- Просмотр каталога с фильтрацией (SQL и ORM)
- Добавление товаров в корзину
- Расчет скидок (паттерн Стратегия)
- Управление складом (поступление, остатки, списание)
- Выполнение заказов администратором
- Отчеты (топ товаров, статистика по категориям)

## Технологии
- Backend: Django 4.2, Django REST Framework
- Database: PostgreSQL
- Client: Python Tkinter, Requests
- Testing: Django Test Framework

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/luckerman-tech/furniture_store.git
cd furniture_store
```

### 2. Переключение на нужную ветку
```bash
git checkout dev
git checkout main
```

### 3. Настройка виртуального окружения
```bash
python -m venv venv
venv\Scripts\activate (Windows)
source venv/bin/activate (Linux/Mac)
```

### 4. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 5. Применение миграций
```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### 6. Запуск сервера
```bash
python manage.py runserver
```

### 7. Запуск клиента
```bash
cd desktop_client
python client.py
```

## Структура проекта
```text
furniture_store/
├── backend/           (Django бэкенд)
│   ├── api/          (Основное приложение)
│   ├── furniture_store/  (Настройки Django)
│   └── manage.py
├── desktop_client/   (Tkinter клиент)
```
├── requirements.txt  (Зависимости)
└── README.md
