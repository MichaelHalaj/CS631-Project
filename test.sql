CREATE DATABASE if not exists test_db1;
USE test_db1;

CREATE TABLE if not exists pet (name VARCHAR(20), owner VARCHAR(20),
species VARCHAR(20), sex CHAR(1), birth DATE, death DATE);

SHOW TABLES;
DESCRIBE PET;

INSERT INTO pet 
VALUES ('Puffball', 'Diane', 'hamster', 'f', '1990-03-30', NULL);

SELECT * FROM pet;