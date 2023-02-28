import mysql.connector
from mysql.connector import errorcode
from flask_bcrypt import generate_password_hash
import config

print("Conectando...")
try:
    conn = mysql.connector.connect(
        host=config.SQL_host,
        user=config.SQL_user,
        password=config.SQL_password
    )

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('Existe algo errado no nome de usuário ou senha')
    else:
        print(err)

cursor = conn.cursor()

cursor.execute("DROP DATABASE IF EXISTS `car_app`;")

cursor.execute("CREATE DATABASE `car_app`;")

cursor.execute("USE `car_app`;")

# criando tabelas
TABLES = {}
TABLES['Cars'] = ('''
      CREATE TABLE `cars` (
      `name` varchar(50) NOT NULL,
      `plate` varchar(10) NOT NULL,
      `model` varchar(20) NOT NULL,
      `ownerNickname` varchar(15) NOT NULL,
      PRIMARY KEY (`plate`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

TABLES['Trips'] = ('''
      CREATE TABLE `trips` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `initialAddress` varchar(100) NOT NULL,
      `initialTime` DATETIME NOT NULL,
      `endAddress` varchar(100),
      `endTime` DATETIME,
      `userNickname` varchar(15) NOT NULL,
      `carPlate` varchar(10) NOT NULL,

      PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

TABLES['Users'] = ('''
      CREATE TABLE `users` (
      `name` varchar(20) NOT NULL,
      `nickname` varchar(15) NOT NULL,
      `password` varchar(100) NOT NULL,
      `masterUserNickname` varchar(20) NOT NULL,
      `email` varchar(100) NOT NULL,
      PRIMARY KEY (`nickname`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')


TABLES['UsersCars'] = ('''
      CREATE TABLE `users_cars` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `userNickname` varchar(20) NOT NULL,
      `carPlate` varchar(15) NOT NULL,
      PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')


for tabel_name in TABLES:
    tabel_sql = TABLES[tabel_name]
    try:
        print('Criando tabela {}:'.format(tabel_name), end=' ')
        cursor.execute(tabel_sql)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print('Já existe')
        else:
            print(err.msg)
    else:
        print('OK')

# inserindo usuarios
user_sql = 'INSERT INTO users (name, nickname, password, masterUserNickname,email) VALUES (%s, %s, %s, %s, %s)'
users = [
    ("Albert Mazuz", "Bertimaz", generate_password_hash("albert123").decode('utf-8'), "Bertimaz",
     "albert.mazuz@gmail.com"),
    ("Jessica Machado", "Jess", generate_password_hash("jess123").decode('utf-8'), "Jess", "jessica.machado1991@gmail.com"),
    ("dummyUser", "dummy", generate_password_hash("dummy").decode('utf-8'), "dumy", "dummy"),

]
cursor.executemany(user_sql, users)

cursor.execute('select * from bertimaz$default.users')
print(' -------------  Usuários:  -------------')
for user in cursor.fetchall():
    print(user[1])
#
# id` int(11) NOT NULL AUTO_INCREMENT,
#       `name` varchar(50) NOT NULL,
#       `plate` varchar(40) NOT NULL,
#       `ownerNickname` varchar(20) NOT NULL,

# inserindo carros
cars_sql = 'INSERT INTO cars (name, plate, model, ownerNickname) VALUES (%s, %s, %s, %s)'
cars = [
    ('Etios', 'FLI-4781', 'Toyota Etios', 'Bertimaz'),
    ('Hilux', 'aaa-1111', 'Toyota Hilux', 'Avner'),
    ('Dummy Car','DDD-1111','Dummy Model', 'dummy')

]
cursor.executemany(cars_sql, cars)

cursor.execute('select * from bertimaz$default.cars')
print(' -------------  Carros:  -------------')
for car in cursor.fetchall():
    print(car[1])

# inserindo viagens
trips_sql = 'INSERT INTO trips (initialAddress, initialTime, endAddress, endTime, userNickname, carPlate) VALUES (%s, %s, %s, %s, %s, %s)'
trips = [
    ('Rua Mourato Coelho, n 1430', '2002-10-25 10:00:00', 'Rua Iguatemi, n 100', '12:00', 'Bertimaz', 'FLI-4781'),
    ('Rua Leopoldo, n 1400', '2022-10-26 14:00:00', 'Avenida Brigadeiro Faria Lima, n 100', '15:00', 'Avner', 'aaa-1111'),
    ('Rua Dummy,n dummy', '2022-10-26 14:00:00', 'Rua Dummy, n dummy', '2022-10-26 14:00:00', 'dummy', 'DDD-1111')
]
cursor.executemany(trips_sql, trips)

cursor.execute('select * from bertimaz$default.trips')
print(' -------------  Trips:  -------------')
for trip in cursor.fetchall():
    print(trip[1])



usersCars_sql = 'INSERT INTO users_cars (userNickname, carPlate) VALUES (%s, %s)'
usersCars = [
    ('Bertimaz', 'FLI-4781'),
    ('Jess','FLI-4781'),
    ('dummy','DDD-1111'),
    ('Avner', 'FLI-4781'),
    ('Avner', 'aaa-1111')
]
cursor.executemany(usersCars_sql, usersCars)

cursor.execute('select * from bertimaz$default.users_cars')
print(' -------------  UserCars:  -------------')
for trip in cursor.fetchall():
    print(trip[1])


# commitando se não nada tem efeito
conn.commit()

cursor.close()
conn.close()
