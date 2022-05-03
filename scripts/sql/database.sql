DROP TABLE IF EXISTS commands;

CREATE TABLE IF NOT EXISTS command (
    command VARCHAR(32) PRIMARY KEY,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alias (
    alias VARCHAR(32) PRIMARY KEY,
    command VARCHAR(32) NOT NULL,
    FOREIGN KEY(command) REFERENCES command(command)
);
