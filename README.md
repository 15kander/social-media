# Social-Media

Веб-платформа социальной сети на Django с поддержкой публикаций, мгновенных лайков без перезагрузки страниц, личных чатов и гибких настроек приватности.

🔗 **Живое демо:** [Посмотреть сайт](https://social.pythonanywhere.com/)

## ✨ Что умеет проект

* **Умный поиск:** поиск по пользователям и постам. Закрытые посты видны только одобренным подписчикам.
* **AJAX-лайки:** сердечки ставятся и убираются мгновенно без перезагрузки всей страницы.
* **Приватность:** возможность закрыть профиль от посторонних, принимать или отклонять заявки на подписку и блокировать пользователей.
* **Публикации и общение:** создание постов с фото, редактирование, удаление, комментарии и личные сообщения.

## 🛠 Технологии

* **Backend:** Python 3, Django 5
* **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript (Fetch API / AJAX)
* **База данных:** SQLite
* **Хостинг:** PythonAnywhere

## 🚀 Как запустить проект локально

1. Клонируйте репозиторий:
```bash
git clone https://github.com/15kander/social-media.git
cd social-media
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Установите зависимости и запустите сервер:
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 📂 Структура проекта

```text
├── config/             # Настройки Django (settings.py, urls.py)
├── core/               # Основное приложение (models.py, views.py)
├── templates/          # HTML-шаблоны страниц
├── static/             # CSS и JS файлы
├── manage.py
└── requirements.txt
```