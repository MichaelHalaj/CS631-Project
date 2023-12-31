CREATE DATABASE IF NOT EXISTS OnlineComputerStore;
USE OnlineComputerStore;

CREATE TABLE IF NOT EXISTS CUSTOMER (
    CID INT NOT NULL AUTO_INCREMENT,
    FName varchar(25),
    LName varchar(25),
    EMail varchar(255) UNIQUE,
    CAddress varchar(255),
    Phone varchar(15),
    CStatus INT NOT NULL DEFAULT 0,
    PRIMARY KEY (CID)
);

CREATE TABLE IF NOT EXISTS SILVER_AND_ABOVE (
    CID INT NOT NULL,
    CreditLine INT,
    PRIMARY KEY (CID),
    FOREIGN KEY (CID) REFERENCES CUSTOMER(CID)
);

CREATE TABLE IF NOT EXISTS CREDIT_CARD (
    CCNumber varchar(20) NOT NULL,
    SecNumber INT,
    OwnerName varchar(50),
    CCType varchar(20),
    BilAddress varchar(50),
    ExpDate DATE,
    StoredCardCID INT,
    PRIMARY KEY (CCNumber),
    FOREIGN KEY (StoredCardCID) REFERENCES CUSTOMER(CID)
);

CREATE TABLE IF NOT EXISTS SHIPPING_ADDRESS (
    CID INT NOT NULL,
    SAName varchar(50) NOT NULL,
    RecipientName varchar(50),
    Street varchar(25),
    SNumber INT,
    City varchar(25),
    Zip char(5),
    State varchar(20),
    Country varchar(40),
    PRIMARY KEY (CID, SAName),
    FOREIGN KEY (CID) REFERENCES CUSTOMER(CID)
);

CREATE TABLE IF NOT EXISTS BASKET (
    CID INT,
    BID INT NOT NULL AUTO_INCREMENT,
    FOREIGN KEY (CID) REFERENCES CUSTOMER(CID),
    PRIMARY KEY (BID)
);

CREATE TABLE IF NOT EXISTS TRANSACTIONS (
    BID INT NOT NULL,
    CCNumber varchar(20) NOT NULL, 
    CID INT NOT NULL, 
    SAName varchar(50) NOT NULL,
    TDate date,
    TTag varchar(20) NOT NULL,
    PRIMARY KEY (BID, CCNumber, CID, SAName),
    FOREIGN KEY (BID) REFERENCES BASKET(BID),
    FOREIGN KEY (CCNumber) REFERENCES CREDIT_CARD(CCNumber),
    FOREIGN KEY (CID, SAName) REFERENCES SHIPPING_ADDRESS(CID, SAName)
);

CREATE TABLE IF NOT EXISTS PRODUCT (
    PID INT NOT NULL AUTO_INCREMENT,
    PType varchar(30),
    PName varchar(30),
    PPrice decimal(7, 2) NOT NULL,
    Description TEXT,
    PQuantity INT DEFAULT 0,
    PRIMARY KEY (PID)
);

CREATE TABLE IF NOT EXISTS APPEARS_IN (
    BID INT NOT NULL,
    PID INT NOT NULL,
    Quantity INT DEFAULT 0,
    PriceSold decimal(10,2) NOT NULL,
    PRIMARY KEY (BID, PID),
    FOREIGN KEY (BID) REFERENCES BASKET(BID),
    FOREIGN KEY (PID) REFERENCES PRODUCT(PID)
);

CREATE TABLE IF NOT EXISTS OFFER_PRODUCT (
    PID INT NOT NULL,
    OfferPrice decimal(7,2),
    PRIMARY KEY (PID),
    FOREIGN KEY (PID) REFERENCES PRODUCT(PID)
);

CREATE TABLE IF NOT EXISTS COMPUTER (
    PID INT NOT NULL,
    CPUType varchar(50),
    PRIMARY KEY (PID),
    FOREIGN KEY (PID) REFERENCES PRODUCT(PID)
);

CREATE TABLE IF NOT EXISTS LAPTOP (
    PID INT NOT NULL,
    BType varchar(50),
    Weight decimal(6,3),
    PRIMARY KEY (PID),
    FOREIGN KEY (PID) REFERENCES COMPUTER(PID)
);

CREATE TABLE IF NOT EXISTS PRINTER (
    PID INT NOT NULL,
    PrinterType varchar(50),
    Resolution varchar(20),
    PRIMARY KEY (PID),
    FOREIGN KEY (PID) REFERENCES PRODUCT(PID)
);

