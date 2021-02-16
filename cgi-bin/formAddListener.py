import cgi
import sqlite3

form = cgi.FieldStorage()       # Подсоединяемся к БД

surname = form.getfirst('surnameEdit', '-')     # Получаем значения с post запроса обработки формы добавления
name = form.getfirst('nameEdit', '-')
patronymic = form.getfirst('patronymicEdit', '-')
idRegion = form.getfirst('region', 1)
idCity = form.getfirst('city', 1)
telephone = form.getfirst('telephoneEdit', '-')
email = form.getfirst('emailEdit', '-')

db = sqlite3.connect("Peoples.db")
cursor = db.cursor()
request = "INSERT INTO peoples VALUES({},{},{},{},{},{},{})".format(
    "\'{}\'".format(surname),
    "\'{}\'".format(name),
    "\'{}\'".format(patronymic),
    int(idRegion),
    int(idCity),
    "\'{}\'".format(telephone),
    "\'{}\'".format(email)
)
cursor.executescript(request)       # Вставляем полученные с формы данные в таблицу peoples
db.commit()     # Фиксируем изменения
print('''
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0.3; URL=/table/"/>
</head>
<script>alert("Данные добавлены");</script>
''')    # Уведомляем пользователя о том, что данные уже добавлены и возвращаемя обратно к таблице

