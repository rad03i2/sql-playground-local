CREATE TABLE learners (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100)
);

INSERT INTO learners (name, score) VALUES
    ('Omar', 88),
    ('Layla', 95),
    ('Noor', 81);
