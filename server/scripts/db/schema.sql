CREATE TABLE Person(
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(50),
    email               VARCHAR(100) UNIQUE,
    pw_hash             VARCHAR(100)
);

CREATE TABLE Document(
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(256),
    type            VARCHAR(100),
    img_url         VARCHAR(1024),
    uploaded_on     TIMESTAMP
);
