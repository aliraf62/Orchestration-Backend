CREATE DATABASE IF NOT EXISTS vulnerability_scanner;

USE vulnerability_scanner;

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(255) PRIMARY KEY,
    date DATE
);

CREATE TABLE IF NOT EXISTS testssl_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(255),
    host VARCHAR(255),
    finding_type VARCHAR(255),
    description TEXT,
    details_link TEXT,
    full_results JSON,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS semgrep_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(255),
    file_path VARCHAR(255),
    rule_id VARCHAR(255),
    description TEXT,
    full_results JSON,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
