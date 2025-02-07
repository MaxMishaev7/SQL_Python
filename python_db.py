import psycopg2

print('Hello!')
conn = psycopg2.connect(database='test', user='postgres', password='hecQWk1974Gmr')

tables = """
    DROP TABLE IF EXISTS phones;
    DROP TABLE IF EXISTS persons;

    CREATE TABLE IF NOT EXISTS persons (
    person_id serial PRIMARY KEY NOT NULL, 
    first_name varchar(40) NOT NULL, 
    last_name varchar(40) NOT NULL,
    email varchar(40) NOT NULL 
    );

    CREATE TABLE IF NOT EXISTS phones (
    phone_number varchar(12) PRIMARY KEY NOT NULL CHECK (phone_number ~ '\\+79[0-9]{9}'),
    person_id integer NOT NULL REFERENCES persons(person_id) ON DELETE CASCADE
    );
    """
# Создание структуры БД
def create_tables(cursor, table_str):
    #with conn.cursor() as curs:
    cursor.execute(table_str)
    conn.commit()

# Добавление нового клиента  
def add_new_client(cursor, first_name, last_name, email, phone_number):
    # with conn.cursor() as curs:
    # проверяем, есть ли такой человек в БД
    cursor.execute("""
    SELECT person_id
    FROM persons
    WHERE first_name=%s AND last_name=%s AND email=%s;
    """, (first_name, last_name, email))
    person = cursor.fetchone()
    print(person)
        
    # если id для человека с таким именем - None, добавляем
    if person == None:
        print('Ветка None')
        cursor.execute("""
        INSERT INTO persons(first_name, last_name, email) 
        VALUES (%s, %s, %s) RETURNING first_name, last_name, email;
        """, (first_name, last_name, email))
        added = cursor.fetchone()
        print(added)

    # Проверяем, есть ли телефон в БД
        cursor.execute("""
        SELECT person_id FROM phones
        WHERE EXISTS(SELECT phone_number FROM phones 
              WHERE phone_number=%s);
        """, (phone_number,))
        pers_id = cursor.fetchone()
        if pers_id == None: 
            print('Ветка после EXISTS()')
            # для добавления телефона в таблицу нам нужно получить id,
            # по которому сделана запись данного человека

            cursor.execute("""
            SELECT person_id FROM persons
            WHERE first_name=%s AND last_name=%s;
            """, (first_name, last_name))
            id = cursor.fetchone()
            print(id)  

            # добавление телефона в таблицу по полученному id
            cursor.execute("""
            INSERT INTO phones(phone_number, person_id)
            VALUES (%s, %s) RETURNING phone_number, person_id;
            """, (phone_number, id[0]))
            print(cursor.fetchone())
        else:
            print('Такой телефон уже зарегистрирован в БД. Попробуйте другой')
    else:
        print('Сотрудник с таким именем уже зарегистрирован в БД')



# Добавление телефона для существующего клиента
def phone_for_client(first_name, last_name, email, phone_number):
    with conn.cursor() as curs:
        curs.execute("""
        SELECT person_id FROM persons
        WHERE first_name = %s AND last_name = %s AND email = %s;
        """, (first_name, last_name, email))
        pers_id = curs.fetchone()
        print(pers_id)
        if pers_id != None:
            curs.execute("""
            SELECT phone_number FROM phones
            WHERE phone_number = %s
            """, (phone_number,))
            phone = curs.fetchone()
            print(phone)
            if phone == None:
                curs.execute("""
                INSERT INTO phones(phone_number, person_id) 
                VALUES (%s, %s);
                """, (phone[0], pers_id))
            else:
                print("Такой телефон уже есть в базе")
        else:
            print('Такого клиента нет в базе')




# create_tables(tables)



# add_new_client(first_name='Max', last_name='Mishaev', email='max@gmail.com', phone_number='+79067676548')

with conn.cursor() as curs:
    create_tables(curs, tables)
    
    add_new_client(curs, 'Semen', 'Semenych', 'sec@semsem.ru', '+79034556888')
    add_new_client(curs, 'Max', 'Mishaev', 'max@gmail.com', '+79034556778')
    add_new_client(curs, 'Max', 'Mishaev', 'max@gmail.com', '+79035719146')
    add_new_client(curs, 'Max', 'Mishaev', 'mmm@gmail.com', '+79024565689')
    add_new_client(curs, 'Ivan', 'Ivanov', 'iviv@gmail.com', '+79034556888')

    curs.execute("""
    SELECT * FROM persons;
    """)
    print(curs.fetchall())
    
    

# phone_for_client('Semen', 'Semenych', 'sec@semsem.ru', '+79034556778')
# phone_for_client('Max', 'Mishaev', 'max@gmail.com', '+79034556778')

    # curs.execute("INSERT INTO phones(phone_id, phone_number) VALUES (1, '79267652434'), (2, '7916081149')")
    
    # curs.execute("""
    # INSERT INTO persons(person_id, first_name, last_name, email) VALUES 
    # (1, 'Max', 'Mishaev', 'max@gmail.com'),
    # (2, 'Anna', 'Fuks', 'ann_fuks@mail.ru'),
    # (3, 'Helen', 'Bravova', 'bravo-va@yandex.ru'),
    # (4, 'Ivan', 'Ivanov', 'iviv@yahoo.com') RETURNING person_id, first_name, last_name;
    # """)
    # print (curs.fetchone())

    # curs.execute("""
    # INSERT INTO phones(phone_number, person_id) VALUES 
    # ('+79267856500', 1),
    # ('+79267699831', 1),
    # ('+79034506772', 2),
    # ('+79167552444', 3),
    # ('+79448889929', 4),
    # ('+79257653852', 4)
    # RETURNING phone_number, person_id;
    # """)    
    # print(curs.fetchone())

conn.close()