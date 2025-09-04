
python -m venv venv                         - создание среды
source venv/Scripts/activate                - активация среды
pip install -r requirements.txt             - Установка всего нужного


python manage.py makemigrations             - создание миграций
python manage.py migrate                    - применение миграций
python manage.py showmigrations             - просмотр миграций
python manage.py migrate contenttypes zero  - отмена всех миграций

python manage.py makemigrations main_app
python manage.py migrate main_app

python manage.py createsuperuser            - создание супер пользователя
python manage.py runserver                  - запуск проекта

git add .
git commit -m 'текст комментария'
git push

1. Расчеты

- Почасовой заработок
- расходы


2. Настрой статические файлы в Django:

- Создай папку static/js для JavaScript файлов
- Реализуй представления (views) для обработки данных и рендеринга шаблонов
- Настрой маршруты (urls) для всех страниц
- Реализуй формы Django для обработки данных из модальных окон
* Добавь аутентификацию и авторизацию для защиты доступа к системе