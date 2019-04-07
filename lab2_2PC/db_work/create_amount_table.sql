CREATE TABLE amounts
(
    amount_id serial NOT NULL,
    amount numeric CONSTRAINT amount CHECK (amount >= 0),
    CONSTRAINT amounts_pkey PRIMARY KEY (amount_id)
);

INSERT INTO amounts VALUES (1, 100);
