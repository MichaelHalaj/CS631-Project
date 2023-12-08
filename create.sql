CREATE DATABASE IF NOT EXISTS OnlineComputerStore;
USE OnlineComputerStore;

CREATE TABLE IF NOT EXISTS CUSTOMER (
    CID INT,
    FName varchar(25),
    LName varchar(25),
    EMail varchar(255),
    Address varchar(255),
    Phone varchar(15),
    Status varchar(20),
    PRIMARY KEY (CID)
);

CREATE TABLE IF NOT EXISTS SILVER_AND_ABOVE (
    CID INT,
    CreditLine varchar
);
