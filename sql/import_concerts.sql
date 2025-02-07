SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS concerts;

CREATE TABLE concerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    artist VARCHAR(255) NOT NULL,
    genres VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    venue VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    capacity INT NOT NULL,
    number_of_songs INT NOT NULL
);

LOAD DATA INFILE '/var/lib/mysql-files/cleaned_concerts_2.csv'
INTO TABLE concerts
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(artist, genres, date, venue, city, state, capacity, number_of_songs);

SET FOREIGN_KEY_CHECKS = 1;