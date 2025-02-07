DROP TABLE IF EXISTS phones;
DROP TABLE IF EXISTS person;

CREATE TABLE IF NOT EXISTS person (
person_id serial PRIMARY KEY NOT NULL,
name varchar(40) NOT NULL,
surname varchar(40) NOT NULL,
email varchar(60) NOT NULL
);

CREATE TABLE IF NOT EXISTS phones (
phone_id integer PRIMARY KEY NULL REFERENCES person(person_id),
phone_number varchar(14)
);

