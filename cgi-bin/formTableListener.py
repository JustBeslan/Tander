import cgi
import sqlite3
import pandas as pd
import workPDF
import re
from fpdf import FPDF


form = cgi.FieldStorage()
db = sqlite3.connect("Peoples.db")  # Подсоединяемся к БД

if 'addButton' in form:  # Если нажата кнопка "Добавить"
    print("Content-type: text/html\n")  # В качестве ответа - html форма добавления информации о человеке в таблицу
    print("""
        <!DOCTYPE HTML>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Форма добавления</title>
        </head>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .form {
                padding: 32px;
                border-radius: 10px;
                box-shadow: 0 4px 16px #ccc;
                font-family: sans-serif;
                letter-spacing: 1px;
            }
            .pos {
                text-align: center;
                margin: 50px;
            }
            .form .req:invalid {
                border: 2px solid red;
            }
        </style>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
        <script type="text/javascript">
            function selectRegion(selectObject) {
                var idRegion = selectObject.value;
                if (idRegion != '') {
                    $.post('getCity.py', {'idRegion': idRegion}, onResponse);
                } else {
                    var citySelect = document.getElementById('city');
                    citySelect.innerHTML='<option value="">Выберите город</option>';
                }
            }
            function onResponse(data){
                html='<option value="">Выберите город</option>'
                for(var item in data)
                    html+='<option value="' + data[item][0] + '">' + data[item][1] + '</option>';
                var citySelect = document.getElementById('city');
                citySelect.innerHTML=html;
            }
        </script>
        <body>
            <form name='formAdd' action='formAddListener.py' method='post' class='form'>
                <h1 class='pos'>Форма добавления</h1>
                <div class='pos'>
                    <input type="text" name="surnameEdit" placeholder="Фамилия" class='req' required>
                    <input type="text" name="nameEdit" placeholder="Имя" class='req' required>
                    <input type="text" name="patronymicEdit" placeholder="Отчество">
                </div>
                <div class='pos'>
    """)
    # В этой части из таблицы regions берутся все строки и помещаются в выпадающий список
    select = """
        Регион <select id='region' name='region' onchange='selectRegion(this)' class='req' required>
            <option value=''>Выберите регион</option>
    """
    template = '<option value={}>{}</option>'
    cursor = db.cursor()
    cursor.execute("SELECT * from regions")
    peoples = cursor.fetchall()
    for person in peoples:
        select += template.format(*person)
    select += "</select>"
    print(select)
    print("""
                    Город <select id='city' name='city' class='req' required>
                        <option value=''>Выберите город</option>
                    </select>
                </div>
                <div class='pos'>
                    Телефон: +7<input type="text" name="telephoneEdit" placeholder="(___)___-__-__" class='req' pattern="[\(]{0,1}9[0-9]{2}[\)]{0,1}\s?\d{3}[-]{0,1}\d{2}[-]{0,1}\d{2}">
                </div>
                <div class='pos'>
                    E-mail<input type="text" name="emailEdit" placeholder="email@example.com" class='req' pattern='[A-Za-z]\S*@[a-z]{2,7}.[a-z]{2,}'>
                </div>
                <input type="button" value="Отмена" name="cancelButton" style='float:right;' onclick='history.back();'>
                <input type="submit" value="Сохранить" name="saveButton" style='float:right;'>
            </form>
        </body>
        </html>
    """)
elif 'exportExcelButton' in form:  # Если нажата кнопка "Экспортировать таблицу в Excel"
    tablePeoples = {"Surname": [],  # Собирается таблица для записи в файл (пока есть только шапка)
                    "Name": [],
                    "Patronymic": [],
                    "Region": [],
                    "City": [],
                    "Telephone": [],
                    "E-mail": []}
    cursor = db.cursor()
    cursor.execute('''
        SELECT p.surname, p.name, p.patronymic, r.region, c.city, p.telephone, p.email FROM peoples p
        JOIN regions r ON p.regionId = r.id
        JOIN cities c ON (p.cityId=c.id AND p.regionId = c.regionId)            
    ''')
    peoples = cursor.fetchall()  # Из таблицы peoples забираются все строки и постепенно наполняют tablePeoples
    for surname, name, patronymic, region, city, telephone, email in peoples:
        tablePeoples["Surname"].append(surname)
        tablePeoples["Name"].append(name)
        tablePeoples["Patronymic"].append(patronymic)
        tablePeoples["Region"].append(region)
        tablePeoples["City"].append(city)
        tablePeoples["Telephone"].append(telephone)
        tablePeoples["E-mail"].append(email)
    dataFrame = pd.DataFrame(tablePeoples)
    dataFrame.to_excel("Peoples.xlsx")  # Записываем таблицу в файл с именем Peoples.xlsx в директорию проекта
    print('''
        <head>
            <meta charset="utf-8">
        </head>
        <script>
            alert("Данные экспортированы в Peoples.xlsx");
            history.back();
        </script>
    ''')  # Уведомляем пользователя о том, что таблица peoples была экспортрована
elif 'importPdfButton' in form:     # Если нажата кнопка "Импорт данных из PDF"
    pdf = workPDF.openPDF()         # Открываем PDF
    text = workPDF.getText(pdf)     # Получаем текст из файла (с сохранененной структурой)
    text = text.split('\n')         # Получаем список строк из файла
    data = {}                       # Данные из резюме (пока пустой)

    fio = text[0].split(' ')        # Первой строчкой в резюме является ФИО, которое разделено пробелами. Считываем его.
    data["Surname"] = fio[0]
    data["Name"] = fio[1]
    data["Patronymic"] = '-'
    if len(fio) > 2:
        data["Patronymic"] = ' '.join(fio[1:])      # В случае, если в резюме есть и отчество, получаем и его (иначе, значение по умолчанию = "-")

    city = text[4].split(' ')       # Получаем строку про место проживания (известен только город)
    city = city[len(city) - 1]
    cursor = db.cursor()
    cursor.execute("SELECT id, regionId FROM cities WHERE city='{}'".format(city))
    location = cursor.fetchall()
    data["City"] = location[0][0]   # Получаем ИД города и региона из таблицы, исходя из названия города
    data["Region"] = location[0][1]

    telephone = text[2]     # Получаем строку с телефоном
    data["Telephone"] = re.sub(
        '[- ]*',
        '',
        re.findall(r'[(][0-9]{3,}[)]\s*[0-9]+[-\s]*[0-9]+[-\s]*[0-9]', telephone)[0]
    )       # Получаем сам номер телефона поиском в строке по шаблону номера телефона

    email = text[3]     # Получаем строку с почтой
    data["E-mail"] = re.findall(r'\w+@[A-Z0-9]+\.[A-Z]{2,4}', email, flags=re.IGNORECASE)[0]    # Получаем саму почту поиском в строке по шаблону почты
    cursor = db.cursor()
    request = "INSERT INTO peoples VALUES({},{},{},{},{},{},{})".format(
        "\'{}\'".format(data["Surname"]),
        "\'{}\'".format(data["Name"]),
        "\'{}\'".format(data["Patronymic"]),
        int(data["Region"]),
        int(data["City"]),
        "\'{}\'".format(data["Telephone"]),
        "\'{}\'".format(data["E-mail"])
    )       # Вставляем в таблицу полученные с резюме данные
    cursor.execute(request)
    db.commit()  # Фиксируем изменения
    print('''
    <head>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="0.3; URL=/table/"/>
    </head>
    <script>alert("Данные добавлены");</script>
    ''')  # Уведомляем пользователя о том, что данные уже добавлены и возвращаемя обратно к таблице
elif 'exportPdfButton' in form:     # Если нажата кнопка "Экспортировать таблицу в PDF"
    newPdf = FPDF()                 # Создаем pdf и добавляем шрифт для записи русских символов
    newPdf.add_font('Athena', '', 'font/new_athena_unicode.ttf', uni=True)
    cursor = db.cursor()  # Создаем курсор перед выполением запроса
    cursor.execute('''
        SELECT p.surname, p.name, p.patronymic, r.region, c.city, p.telephone, p.email FROM peoples p
        JOIN regions r ON p.regionId = r.id
        JOIN cities c ON (p.cityId=c.id AND p.regionId = c.regionId)
    ''')  # Получаем все данные с таблицы
    peoples = cursor.fetchall()                             # Забираем все найденные данные
    for i, person in enumerate(peoples):                    # Постепенно заполняем файл
        newPdf.add_page()                                   # Создаем новую страницу в файле (для резюме следующего человека из списка)
        newPdf.set_font(family="Athena", size=30)           # Устанавливаем шрифт
        newPdf.cell(0, 10, txt="Резюме {}".format(i+1), ln=1, align="C")    # Заголовок
        newPdf.cell(0, 10, txt="", ln=1, align="C")         # Новая строчка
        fio = ' '.join([person[0], person[1]])              # Имя и Фамилия соединятются через пробел
        if person[2] != '-':
            fio = ' '.join([fio, person[2]])                # Если указано и отчество, то присоединяем и отчество
        newPdf.cell(0, 10, txt=fio, ln=1, align="C")        # Вставляем строчку с ФИО
        newPdf.set_font(family="Athena", size=20)           # Устанавливаем шрифт (уменьшаем размер)
        location = ''
        if person[3] != '-' and person[4] == '-':
            location = person[3]
        elif person[3] == '-' and person[4] != '-':
            location = person[4]
        else:
            location = ', '.join([person[3], person[4]])
        newPdf.cell(0, 10, txt="Проживает в {}".format(location), ln=1, align="C")      # Вставляем строку с местом проживанием (если что-то не указано, то пропускаем его)
        if person[5] != '-':
            newPdf.cell(0, 10, txt="Телефон +7{}".format(person[5]), ln=1, align="C")   # Если указан телефон, то добавляем в резюме
        if person[6] != '-':
            newPdf.cell(0, 10, txt="Почта {}".format(person[6]), ln=1, align="C")       # Если указана почта, то добавляем в резюме
    newPdf.output("Peoples.pdf")         # Сохраняем все сформированные данные в файле pdf
    print('''
    <head>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="0.3; URL=/table/"/>
    </head>
    <script>alert("Данные экспортированы в Peoples.pdf");</script>
    ''')  # Уведомляем пользователя о том, что данные уже экспортированы в Peoples.pdf и возвращаемя обратно к таблице
