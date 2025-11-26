CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    password TEXT
);

INSERT INTO users (id, password)
VALUES (1, 'hello');
