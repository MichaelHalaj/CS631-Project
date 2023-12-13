DELIMITER //

CREATE PROCEDURE InsertRandomData()
BEGIN
  DECLARE i INT DEFAULT 0;

  WHILE i < 20 DO
    BEGIN
      -- Insert random data into CUSTOMER table
      INSERT INTO CUSTOMER (FName, LName, EMail, CAddress, Phone, CStatus)
      VALUES (
        CONCAT('FirstName', FLOOR(RAND() * 100)),
        CONCAT('LastName', FLOOR(RAND() * 100)),
        CONCAT('email', i, '@example.com'),
        CONCAT('CAddress', FLOOR(RAND() * 100)),
        FLOOR(RAND() * 1000000000),
        1
      );

      -- Get the last inserted ID
      SET @CID = LAST_INSERT_ID();
      SET @CCNumber = FLOOR(RAND() * 1000000000000);
      -- Insert random data into CREDIT_CARD table
      INSERT INTO CREDIT_CARD (CCNumber, SecNumber, OwnerName, CCType, BilAddress, ExpDate, StoredCardCID)
      VALUES (
        @CCNumber,
        FLOOR(RAND() * 1000),
        CONCAT('Owner', FLOOR(RAND() * 100)),
        CONCAT('Type', FLOOR(RAND() * 100)),
        CONCAT('BillingAddress', FLOOR(RAND() * 100)),
        DATE_ADD(NOW(), INTERVAL FLOOR(RAND() * 365) DAY), -- Random expiration date within the next year
        @CID
      );
    
      SET @SAName = CONCAT('ShippingAddress', FLOOR(RAND() * 100));
      -- Insert random data into SHIPPING_ADDRESS table
      INSERT INTO SHIPPING_ADDRESS (CID, SAName, RecipientName, Street, SNumber, City, Zip, State, Country)
      VALUES (
        @CID,
        @SAName,
        CONCAT('Recipient', FLOOR(RAND() * 100)),
        CONCAT('Street', FLOOR(RAND() * 100)),
        FLOOR(RAND() * 100),
        CONCAT('City', FLOOR(RAND() * 100)),
        LPAD(FLOOR(RAND() * 100000), 5, '0'), -- Pad Zip with leading zeros
        CONCAT('State', FLOOR(RAND() * 100)),
        CONCAT('Country', FLOOR(RAND() * 100))
      );
      
      INSERT INTO BASKET (CID)
      VALUES (@CID);


      SET @BID = LAST_INSERT_ID();

      SET @PID = (SELECT PID FROM PRODUCT
                  ORDER BY RAND()
                  LIMIT 1);

      SET @PriceSold = (SELECT
                            LEAST(P.PPrice, COALESCE(OP.OfferPrice, P.PPrice)) AS MinPrice
                        FROM
                            PRODUCT P
                        LEFT JOIN
                            OFFER_PRODUCT OP ON P.PID = OP.PID
                        WHERE 
                            P.PID = @PID);

      SET @Quantity = FLOOR(RAND() * 4);
      INSERT INTO APPEARS_IN(BID, PID, Quantity, PriceSold)
      VALUES (
        @BID,
        @PID,
        @Quantity,
        @PriceSold * @Quantity
      );

      INSERT INTO TRANSACTIONS (BID, CCNumber, CID, SAName, Tdate, TTag)
      VALUES (
        @BID,
        @CCNumber,
        @CID,
        @SAName,
        DATE_ADD('2022-01-01', INTERVAL FLOOR(RAND() * 365) DAY),
        'delivered'
      );
      SET i = i + 1;
    END;
  END WHILE;
END //

DELIMITER ;

-- Call the stored procedure
CALL InsertRandomData();
