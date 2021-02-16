PRAGMA encoding = "UTF-8";
CREATE TABLE peoples (
    surname text NOT NULL,
    name text NOT NULL,
    patronymic text,
    regionId INTEGER,
    cityId INTEGER,
    telephone text,
    email text,
    FOREIGN KEY (regionId) REFERENCES regions(id)
    FOREIGN KEY (cityId) REFERENCES cities(id));
INSERT INTO peoples VALUES (
    'Иванов',
    'Иван',
    'Иванович',
    1,
    1,
    '(861)9999999',
    'email@mail.com');
CREATE TABLE regions (
    id INTEGER PRIMARY KEY,
    region text);
INSERT INTO regions(region) VALUES
    ('Краснодарский край'),
    ('Ростовская область'),
    ('Ставропольский край');
CREATE TABLE cities (
    id INTEGER PRIMARY KEY,
    regionId INTEGER,
    city text,
    FOREIGN KEY (regionId) REFERENCES regions(id));
INSERT INTO cities(regionId, city) VALUES
    (1, 'Краснодар'), (1, 'Кропоткин'), (1, 'Славянск'),
    (2, 'Ростов'), (2, 'Шахты'), (2, 'Батайск'),
    (3, 'Ставрополь'), (3, 'Пятигорск'), (3, 'Кисловодск');
