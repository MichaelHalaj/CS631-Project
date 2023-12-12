BEGIN;

INSERT INTO CUSTOMER (FName, LName, EMail, Address, Phone, Status)
VALUES ('Frank', 'Gad', 'f@f', 'hadaksd', '29032840', null);

SET @main_table_id = LAST_INSERT_ID();

INSERT INTO CREDIT_CARD (CCNumber, SecNumber, OwnerName, CCType, BilAddress, ExpDate, StoredCardCID)
VALUES (21312312, 564, 'dajsd', 'hasjd', 'asdasd', '2028-11-20', @main_table_id);

COMMIT;


BEGIN;

INSERT INTO CUSTOMER (FName, LName, EMail, Address, Phone, Status)
VALUES ('Sam', 'Jasd', 's@j', 'hjioerw', '409342', null);

SET @main_table_id = LAST_INSERT_ID();

INSERT INTO CREDIT_CARD (CCNumber, SecNumber, OwnerName, CCType, BilAddress, ExpDate, StoredCardCID)
VALUES (123123890, 342, 'Sam', 'hasjd', 'asdasd', '2029-11-20', @main_table_id);

COMMIT;