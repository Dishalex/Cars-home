# Коротка інформація щодо запуску сервера

1. Створити локальну копію гілки із вказанням імені користувача та фічі що міняється
2. Ініціалізувати віртуальне оточення **poetry shell**
3. Оновити залежності **poetry update**

   Подальші дії виконувати з кореневого каталогу: **CARS-HOME**
5. За потреби виконати міграції БД **alembic upgrade head**
6. Запуск серверу однією з команд:
   **uvicorn backend.main:app --host localhost --port 8000 --reload**

   або з використанням логування:
   **uvicorn backend.main:app --host localhost --port 8000 --reload --log-level debug > logs.txt**


# Cars-home
Team 4 Python Data Science project

Загальний опис проєкту:

****Система управління паркуванням на основі моделі комп'ютерного зору****

**Огляд:**

_Розробити веб-застосунок, який автоматично може:_
1. визначати номери автомобільних знаків на зображеннях;
2. відстежити тривалість паркування для кожного унікального транспортного засобу;
3. розраховувати накопичені паркувальні витрати.
   
_Додатково:_

5. Інтеграція веб камери
6. Інтеграція управління воротами для відкриття за допомогою визначення номерного знака
7. Real Time мобільні сповіщення для подій в'їзду/виїзду для кожного користувача
8. Графіки та звіти про кількість вільних та зайнятих паркомісць.

**Необхідні функції:**
1. Управління обліковими записами користувачів.
2. Ролі адміністратора та звичайного користувача.
3. Функції адміністратора - додавання/видалення зареєстрованих номерних знаків, налаштування тарифів на паркування та можливість створення чорного списку транспортних засобів.
4. Функції користувача - перегляд власної інформації про номерний знак та історії паркування
5. Приймання зображень від користувача. Детекція номерного знаку. Виявлення та виділення області з номерним знаком із зображень.
6. Оптичне розпізнавання символів для ідентифікації тексту номерного знаку.
7. Пошук номера авто у базі даних зареєстрованих транспортних засобів.
8. Відстеження тривалості паркування.
9. Запис часу в'їзду/виїзду кожного разу, коли визначається номерний знак.
10. Розрахунок загальної тривалості паркування для кожного унікального номерного знаку.
11. Зберігання даних про тривалість, пов'язаних із номерними знаками в базі даних. Розрахунок вартості паркування.
12. Сповіщення користувача, якщо накопичені парковочні витрати перевищують встановлені ліміти.
13. Генерація звітів про розрахунки, які можна експортувати у форматі CSV.

**Технічна реалізація:**
- Розробка веб-сервісу на основі фреймворку FastAPI
- При розробці веб-сервісу дотримуйтесь використання корпоративних кольорів (по можливості)
- Модель компʼютерного зору реалізована за допомогою Tensorflow/Keras та OpenCV
- База даних Postgres для постійного зберігання номерних знаків та даних
**Створення Dockerfile:**
- розробити Dockerfile для створення образу Docker, який дозволить розміщувати та запускати програму в контейнеризованому середовищі.
- Dockerfile має включати всі необхідні інструкції для створення образу, включаючи:
- - вибір базового образу,
  - копіювання вихідного коду програми до контейнера,
  - встановлення необхідних залежностей та визначення команди для запуску програми.
**Використання Docker Compose**:
- Інтегрувати інструмент Docker Compose для спрощення процесу розгортання та управління проєктом у середовищі Docker.
- Створити файл docker-compose.yml, який описує послуги, мережі та томи, необхідні для проєкту.
- Файл повинен дозволяти запускати весь проєкт за допомогою однієї команди docker-compose up, автоматизуючи створення та запуск необхідних Docker контейнерів.

- Створення докладної покрокової інструкції щодо встановлення та використання вашого проєкту.

# Database relations scheme:
![car_park6 - public-diagram](https://github.com/Dishalex/Cars-home/assets/131618968/fb9d735b-00ea-4f83-a75c-7152f87d6962)
