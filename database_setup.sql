-- Create database
CREATE DATABASE IF NOT EXISTS lostfound;
USE lostfound;

-- Table for user login and registration
CREATE TABLE IF NOT EXISTS logindb11 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    enroll VARCHAR(10) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    contact VARCHAR(15) NOT NULL,
    password VARCHAR(255) NOT NULL,
    con_password VARCHAR(255) NOT NULL,
    branch VARCHAR(50),
    sem VARCHAR(10)
);

-- Table for found items
CREATE TABLE IF NOT EXISTS found11 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    dis_item TEXT,
    f_name VARCHAR(50) NOT NULL,
    contact VARCHAR(15) NOT NULL,
    email VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    item_img LONGBLOB
);

-- Table for lost items
CREATE TABLE IF NOT EXISTS lost11 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_namel VARCHAR(100) NOT NULL,
    dis_iteml TEXT,
    f_namel VARCHAR(50) NOT NULL,
    contactl VARCHAR(15) NOT NULL,
    emaill VARCHAR(100) NOT NULL,
    datel DATE NOT NULL,
    item_imgl LONGBLOB
);
