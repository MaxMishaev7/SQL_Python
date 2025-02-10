import psycopg2

print('Hello!')
conn = psycopg2.connect(database='persons', user='postgres', password='hecQWk1974Gmr')

tables = """
    DROP TABLE IF EXISTS phones;
    DROP TABLE IF EXISTS persons;

    CREATE TABLE IF NOT EXISTS persons (
    person_id serial PRIMARY KEY NOT NULL, 
    first_name varchar(40) NOT NULL, 
    last_name varchar(40) NOT NULL,
    email varchar(40) UNIQUE NOT NULL 
    );

    CREATE TABLE IF NOT EXISTS phones (
    phone_number varchar(12) PRIMARY KEY NOT NULL CHECK (phone_number ~ '\\+79[0-9]{9}'),
    person_id integer NOT NULL REFERENCES persons(person_id) ON DELETE CASCADE
    );
    """
# Создание структуры БД
def create_tables(conn, table_str):    
    with conn.cursor() as curs:
        curs.execute(table_str)
        conn.commit()


# Добавление нового клиента  
def add_new_client(conn, first_name, last_name, email, phone_number):
    with conn.cursor() as curs:
        # проверяем, есть ли такой клиент в БД
        curs.execute("""
        SELECT person_id
        FROM persons
        WHERE first_name=%s AND last_name=%s AND email=%s;
        """, (first_name, last_name, email))
        person = curs.fetchone()
        print(person)     

        # если id для клиента с таким именем = None (не существует), добавляем клиента
        if person == None:
            print('Клиента нет в БД. Добавляем')
            curs.execute("""
            INSERT INTO persons(first_name, last_name, email) 
            VALUES (%s, %s, %s) RETURNING person_id, first_name, last_name, email;
            """, (first_name, last_name, email))
            added_client = curs.fetchone()
            print(added_client)
            print('Клиент {first_name} {last_name} добавлен в БД')
            conn.commit()

            # Проверяем, есть ли указанный телефон в БД
            curs.execute("""
            SELECT person_id FROM phones
            WHERE phone_number=%s;
            """, (phone_number,))
            pers_id = curs.fetchone()

            # если такого номера телефона в базе нет
            if pers_id == None: 
                print('Телефона нет в БД. Добавляем')
                # для добавления телефона в таблицу получаем id,
                # по которому только что записали клиента
                curs.execute("""
                SELECT person_id FROM persons
                WHERE first_name=%s AND last_name=%s AND email=%s;
                """, (first_name, last_name, email))
                id = curs.fetchone()
                print(id)  
                # добавление телефона в таблицу по полученному id
                curs.execute("""
                INSERT INTO phones(phone_number, person_id)
                VALUES (%s, %s) RETURNING phone_number, person_id;
                """, (phone_number, id[0]))
                print(curs.fetchone())
                print(f'\nКлиент {first_name} {last_name} с номером телефона {phone_number} добавлен')
                conn.commit()
            else:
                print(f'\nВНИМАНИЕ! Номер телефона {phone_number} для клиента {first_name} {last_name} не может быть добавлен,') 
                print('т.к. принадлежит другому клиенту')
        else:
            print(f'\nКлиент с именем {first_name} {last_name} и почтой {email} уже зарегистрирован в БД')



# Добавление телефона для существующего клиента
def add_client_phone(conn, first_name, last_name, email, phone_number):
    with conn.cursor() as curs:
    # Получаем id существующего клиента
        curs.execute("""
        SELECT * FROM persons
        """)
        print("DataBase: ", curs.fetchall())

        curs.execute("""
        SELECT person_id, first_name, last_name FROM persons
        WHERE first_name=%s AND last_name=%s AND email=%s;
        """, (first_name, last_name, email))
        pers_id = curs.fetchone()
        print("Client ID:", pers_id)

        if pers_id != None:
            curs.execute("""
            SELECT person_id FROM phones
            WHERE phone_number=%s;
            """, (phone_number,))
            id_person = curs.fetchone()
            print(id_person)
            if id_person == None:
                curs.execute("""
                INSERT INTO phones(phone_number, person_id) 
                VALUES (%s, %s);
                """, (phone_number, pers_id[0]))
                print(f'\nНомер телефона {phone_number} для клиента {first_name} {last_name} успешно добавлен')
                conn.commit()
            else:
                print(f"\nНомер телефона {phone_number} уже есть в базе")
        else:
            print(f'\nКлиента с именем {first_name} {last_name} нет в базе. Телефон не может быть добавлен')



# Удаление телефона для существующего клиента
def delete_client_phone(conn, first_name, last_name, email):
    with conn.cursor() as curs:
        curs.execute("""
        SELECT person_id FROM persons
        WHERE first_name=%s AND last_name=%s AND email=%s;
        """, (first_name, last_name, email))
        client_id = curs.fetchone()
        print('Client_ID for DELETE Client`s phone number:', client_id)
        if client_id != None:
            curs.execute("""
            DELETE FROM phones
            WHERE person_id=%s
            """, client_id)
            conn.commit()
            print(f'\nНомер телефона клиента {first_name} {last_name} успешно удалён')
        else:
            print('\nКлиента с такими данными нет. Телефон не удалён из БД')


# Изменение данных о клиенте
def update_client_data(conn, e_mail, **fields_values):
    print('\nРаботает UPDATE')
    print(fields_values)
    update_keys = fields_values.keys() # Получаем список ключей
    print(update_keys)
    fields_flag = True
    fields_list = ['first_name', 'last_name', 'email', 'phone_number']
    for key in update_keys:
        if key not in fields_list:
            fields_flag = False
            print('\nНекоторые имена полей не соответствуют полям БД')
            break
    if fields_flag:
        with conn.cursor() as curs:
        # Проверяем наличие клиента в БД
            curs.execute("""
            SELECT person_id FROM persons
            WHERE email=%s;
            """, (e_mail,))
            client_id = curs.fetchone()
            print('Client_ID for UPDATE:', client_id)

            # Клиент с таким email присутствует в БД. Обновляем данные
            if client_id != None:
                if 'phone_number' in list(update_keys):
                    # Меняем значение в таблице phones
                    curs.execute(""" 
                    UPDATE phones SET phone_number=%s
                    WHERE person_id=%s RETURNING phone_number, person_id;
                    """, (fields_values.get('phone_number'), client_id[0]))
                    print(fields_values.get('phone_number'), client_id[0])
                    updated = curs.fetchone()
                    print(updated)
                    del fields_values['phone_number'] 

                if len(list(update_keys)) != 0: 
                    fields_str = 'UPDATE persons SET ' # обновляем данные в таблице person
                    fields_list = []
                    for key in update_keys:                        
                        print('Type:', type(key))
                        fields_list.append(fields_values.get(key))
                        fields_str = fields_str + key + '=%s, '
                    fields_str = fields_str.rstrip(', ')                    
                    fields_str += ' WHERE person_id=%s RETURNING person_id, first_name, last_name;'
                    fields_list.append(client_id[0])
                    print(fields_str)
                    print(fields_list)
                    curs.execute(fields_str, tuple(fields_list))
                    print(curs.fetchone())                        
            else: # Если клиента нет в БД. Не обновляем данные   
                print('\nКлиент с такими данными не найден.')              
    else:
        print('Обновление отменено./n')


# Удаление существующего клиента
def delete_client(conn, first_name, last_name, email):
    with conn.cursor() as curs:
        curs.execute("""
        SELECT person_id FROM persons
        WHERE first_name=%s AND last_name=%s AND email=%s;
        """, (first_name, last_name, email))
        client_id = curs.fetchone()
        print('Client_ID for DELETE Client:', client_id)
        if client_id != None:
            curs.execute("""
            DELETE FROM persons 
            WHERE person_id=%s;
            """, client_id)
            print(f'\nВсе данные о клиенте {first_name} {last_name} удалены')


# Найти клиента по его данным
def search_client(conn, **fields):
    print('\nFIELDS_FOR_SEARCHING:', fields)
    # print('Value from Fields:', fields.get('person_id'))
    flag = True
    fields_list = ['person_id', 'first_name', 'last_name', 'email', 'phone_number']
    query_string = ''
    for key in fields:
        if key not in fields_list:
            flag = False
            print(f'В списке полей содержится несуществующее поле {key}/ Поиск отменён')
            break
    if flag:
        with conn.cursor() as curs:
            if 'person_id' in fields:
                print('\nSEARCHING WITH person_id')
                curs.execute("""
                SELECT persons.person_id, persons.last_name, persons.first_name, persons.email, phones.phone_number
                FROM persons
                INNER JOIN phones ON persons.person_id = phones.person_id
                WHERE persons.person_id = %s;            
                """, (fields.get('person_id'),))
                data = curs.fetchall()
                print(data)
            elif 'phone_number' in fields:
                print('\nSEARCHING WITH phone_number')
                curs.execute("""
                SELECT persons.person_id, persons.last_name, persons.first_name, persons.email, phones.phone_number
                FROM persons
                INNER JOIN phones ON persons.person_id = phones.person_id
                WHERE phones.phone_number = %s;
                """, (fields.get('phone_number'),))
                data = curs.fetchall()
                if data == []:
                    print(f'Клиент с номером {fields.get('phone_number')} в БД отсутствует')
                else: 
                    print(data)
            else:
                # Собираем все переданные поля в запрос и строим кортеж значений
                query_string = 'SELECT person_id FROM persons WHERE '
                value_list = []
                for key in fields:
                    part_of_query = key + ' = %s AND '
                    value_list.append(fields.get(key))
                    query_string += part_of_query
                query_string = query_string.rstrip(' AND ')
                query_string += ';'
                print(query_string)
                print(value_list)

                curs.execute(query_string, tuple(value_list))
                id_tuple = curs.fetchall()
                print(type(id_tuple), id_tuple)

                if id_tuple != []:
                    print('\nSEARCHING WITH person_id')
                    for tuple_value in id_tuple:
                        # print(tuple_value)
                        curs.execute("""
                        SELECT persons.person_id, persons.last_name, persons.first_name, persons.email, phones.phone_number
                        FROM persons
                        INNER JOIN phones ON persons.person_id = phones.person_id
                        WHERE persons.person_id = %s;            
                        """, tuple_value)
                        data = curs.fetchall()
                        print(data)
                else:
                    print('Данные по клиенту не найдены')             
    else:
        print('Поиск отменён')




    





# РАБОТА С ФУНКЦИЯМИ

create_tables(conn, tables)
    
add_new_client(conn, 'Semen', 'Semenych', 'sec@semsem.ru', '+79034556888')
add_new_client(conn, 'Max', 'Mishaev', 'max@gmail.com', '+79034556778')
add_new_client(conn, 'Max', 'Mishaev', 'max@gmail.com', '+79035719146')
add_new_client(conn, 'Max', 'Mishaev', 'mmm@gmail.com', '+79024565689')
add_new_client(conn, 'Ivan', 'Ivanov', 'iviv@gmail.com', '+79034556888')
add_new_client(conn, 'Andy', 'McDowell', 'andy@yahoo.com', '+79998885544')

add_client_phone(conn, 'Ivan', 'Ivanov', 'iviv@gmail.com', '+79253217890')
add_client_phone(conn, 'Julia', 'Roberts', 'july@gmail.com', '+79034553231')

update_client_data(conn, 'mmm@gmail.com', phone_number='+79012222222') 
update_client_data(conn, 'iviv@gmail.com', last_name='Ivanchenko', email='xxx@base.com')
delete_client_phone(conn, 'Ivan', 'Ivanchenko', 'xxx@base.com')  
delete_client(conn, 'Andy', 'McDowell', 'andy@yahoo.com')

search_client(conn, person_id=2)
search_client(conn, phone_number='+79998885544')
search_client(conn, phone_number='+79853445876')
search_client(conn, first_name='Max', last_name='Mishaev')
search_client(conn, last_name='Ivanchenko', email='iviv@yandex.ru')

with conn.cursor() as curs:
    curs.execute("""
    SELECT * FROM persons
    """)
    print('\n', curs.fetchall())

    curs.execute("""
    SELECT * FROM phones;
    """)
    print(curs.fetchall())



conn.commit()
conn.close()