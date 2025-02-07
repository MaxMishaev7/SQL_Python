INSERT INTO persons(person_id, first_name, last_name, email) VALUES 
(1, 'Max', 'Mishaev', 'max@gmail.com'),
(2, 'Anna', 'Fuks', 'ann_fuks@mail.ru'),
(3, 'Elena', 'Bravova', 'bravo-va@yandex.ru'),
(4, 'Ivan', 'Ivanov', 'iviv@yahoo.com');

INSERT INTO phones(phone_number, person_id) VALUES 
('+79267856500', 1),
('+79267699831', 1),
('+79034200902', 2),
('+79167552444', 3),
('+79448889929', 4),
('+79257653852', 4);


/*
SELECT * FROM persons;

SELECT * FROM phones;

SELECT first_name, last_name, ph.phone_number
FROM persons per
LEFT JOIN phones ph ON per.person_id = ph.person_id
WHERE first_name = 'Anna';

DELETE FROM persons WHERE first_name = 'Ivan' AND last_name = 'Ivanov';
*/

