import os
import json
import uuid
import requests
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

# Docker container endpoints
SEMGREP_CONTAINER_URL = "http://semgrep_container:5000/"
TESTSSL_CONTAINER_URL = "http://testssl_container:5000/"

# MySQL Configuration
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "testssl_db"
}

def setup_database():
    # Connect to MySQL server without specifying a database
    connection = mysql.connector.connect(
        host=MYSQL_CONFIG["host"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"]
    )
    cursor = connection.cursor()

    # Create the database if it doesn't exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
    connection.close()

    # Now connect to the database
    connection = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = connection.cursor()

    # Create the tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS testssl_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_uuid VARCHAR(255) NOT NULL,
            scan_date DATE NOT NULL,
            results LONGTEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS semgrep_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_uuid VARCHAR(255) NOT NULL,
            scan_date DATE NOT NULL,
            results LONGTEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

@app.route('/analyze', methods=['POST'])
def analyze():
    # Get the customer UUID from the request
    customer_uuid = request.form.get('customer_uuid')

    # Run semgrep and testssl based on the input received
    if 'source_code' in request.files:
        # Save the source code file locally
        source_code = request.files['source_code']
        source_code_path = os.path.join("/tmp", str(uuid.uuid4()) + ".zip")
        source_code.save(source_code_path)

        # Run semgrep on the source code
        run_semgrep(source_code_path, customer_uuid)

    if 'source_url' in request.form:
        # Get the source URL from the request
        source_url = request.form.get('source_url')

        # Run testssl on the source URL
        run_testssl(source_url, customer_uuid)

    return jsonify({"status": "success"})

def run_semgrep(source_code_path, customer_uuid):
    # Run semgrep on the source code and parse the results
    # TODO: Implement this function

    pass

def run_testssl(source_url, customer_uuid):
    # Run testssl on the source URL and parse the results
    # TODO: Implement this function

    pass

if __name__ == '__main__':
    setup_database()
    app.run(host='0.0.0.0', port=8000)

