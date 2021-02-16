from json import JSONEncoder
import sqlite3
import cgi

form = cgi.FieldStorage()
idRegion = form.getfirst("idRegion", '-1')      # Получаем из формы добавления по ajax id выбранного региона

db = sqlite3.connect("Peoples.db")
cursor = db.cursor()
cursor.execute("SELECT id, city FROM cities WHERE regionId={}".format(idRegion))
data = cursor.fetchall()    # Получаем все города данного региона, которые есть в таблице
print('Status: 200 OK')     # Возвращаем эти данные обратно в форму в виде json
print('Content-Type: json')
print('')
print(JSONEncoder().encode(data))
