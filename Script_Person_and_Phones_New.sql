DROP TABLE IF EXISTS phones;
DROP TABLE IF EXISTS persons;

CREATE TABLE IF NOT EXISTS persons (
person_id serial PRIMARY KEY NOT NULL, 
first_name varchar(40) NOT NULL, 
last_name varchar(40) NOT NULL,
email varchar(40) UNIQUE NOT NULL 
);

CREATE TABLE IF NOT EXISTS phones (
phone_number varchar(12) PRIMARY KEY NOT NULL CHECK (phone_number ~ '\+79[0-9]{9}'),
person_id integer NOT NULL REFERENCES persons(person_id) ON DELETE CASCADE
);

SELECT person_id FROM persons WHERE first_name='Max', last_name='Mishaev';
SELECT * FROM phones;

SELECT person_id FROM phones
            WHERE EXISTS(SELECT person_id WHERE phone_number = '+79034200902');


/*
ALTER TABLE phones
ADD CONSTRAINT chk_digits_in_phone_number
CHECK (phone_number LIKE '+7[1-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'); -- '+7[0-9]{10}'
*/