CREATE TABLE "role" (
    id SERIAL,
    role VARCHAR NOT NULL UNIQUE,
    PRIMARY KEY (id)
);
INSERT INTO "role"
VALUES (1, 'admin'),
    (2, 'user');
CREATE TABLE "user" (
    id SERIAL,
    role_id SERIAL NOT NULL,
    email VARCHAR NOT NULL UNIQUE,
    password VARCHAR NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT role_fk FOREIGN KEY (role_id) REFERENCES "role" (id)
);
