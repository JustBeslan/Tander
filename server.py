import os
import sqlite3
from http.server import HTTPServer, CGIHTTPRequestHandler


# Из-за распространенности и известности мне был выбран способ решения данной задачи с помощью CGI
# (Common Gateway Interface)
# В cgi-bin(название зафиксировано) совершается вся работа с cgi (cgi скрипты)

# Класс для обработки запросов
class myHttpRequestHandler(CGIHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/table/':  # Обрабатываем, действия, происходящие при переходе по пути /table/
            template = '''  
                <tr>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
            '''  # Шаблон строки таблицы
            tbody = ''  # Здесь будут все строки таблицы peoples
            cursor = db.cursor()  # Создаем курсор перед выполением запроса
            cursor.execute('''
                SELECT p.surname, p.name, p.patronymic, r.region, c.city, p.telephone, p.email FROM peoples p
                JOIN regions r ON p.regionId = r.id
                JOIN cities c ON (p.cityId=c.id AND p.regionId = c.regionId)            
            ''')  # Выполняем запрос SQL
            peoples = cursor.fetchall()  # Забираем все найденные данные
            for person in peoples:
                tbody += template.format(
                    *person)  # Постепенно заполняем tbody, подставляя в шаблон строки полученные с запроса данные

            table = open('peoples.html',
                         encoding='utf-8').readlines()  # Считываем html файл, который сдержит в себе саму таблицу с шапкой, но пока без тела
            table = ('%s' * len(table) % tuple(table)).format(
                tbody)  # подставляем полученное тело таблицы tbody в таблицу, считанную из html файла
            self.send_response(200)  # ответ get запроса (ОК)
            self.send_header("Content-type", "text/html")  # Тип получаемых данных - html
            self.end_headers()  # конец заголовка ответа get запроса
            self.wfile.write(table.encode(
                'cp1251'))  # Записываем тело ответа get запроса (это весь сформированный выше html файл с таблицей)
        else:
            CGIHTTPRequestHandler.do_GET(self)  # Если пользователь перешел не по /table/, то изменений нет


def settingServer():
    server_address = ('', 8000)  # (host, port) = ("localhost", 8000) = http://localhost:8000
    h = HTTPServer(server_address,
                   myHttpRequestHandler)  # создается сервер по указанным адресу и обработчиком сценариев cgi
    h.serve_forever()  # Включена обработка запросов


def settingsDb():
    dbFileName = 'Peoples.db'
    create = os.path.exists(dbFileName)
    db = sqlite3.connect(dbFileName)  # Соединяемся с БД SQLite
    if not create:      # Если файла БД нет, то создаем его и выполняем скрипт
        cursor = db.cursor()
        with open('db.sql', 'r', encoding='utf-8') as sqlFile:
            sqlScript = sqlFile.read()
        cursor.executescript(sqlScript)  # Выполняем скрипт для создания и заполнения таблиц БД
        db.commit()  # Фиксируем изменения
        print("DB created")
    print('DB ready')
    return db


db = settingsDb()  # Настройка БД (создание и заполнение таблиц)
settingServer()  # Настройка сервера (создание и запуск)
