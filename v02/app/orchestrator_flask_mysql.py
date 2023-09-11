from flask import Flask, request, jsonify
import os
import subprocess
import mysql.connector
from testssl_parser import testssl_parser
from semgrep_parser import semgrep_parser
import time

app = Flask(__name__)

# Database Configuration
db_config = {
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PSWD', 'password'),
    'host': os.environ.get('DB_HOST', 'db'),
    'database': os.environ.get('DB_NAME', 'vulnerability'),
    'raise_on_warnings': True
}

# Ensure database connection on startup
try:
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        print("Connected to MySQL database")
except Exception as e:
    print("Error while connecting to MySQL", e)


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        url = request.form['url']
        customer_id = request.form['customer_id']

        # Run testssl and wait for its completion
        with open("testssl_results.txt", "w") as outfile:
            subprocess.run(["docker", "run", "--rm", "-t", "drwetter/testssl.sh", "--jsonfile-", url], stdout=outfile)
            # Ensuring the command completes and the file is written before reading
            time.sleep(5)

        with open("testssl_results.txt", "r") as file:
            testssl_data = file.read()

        # Parse testssl data
        parsed_testssl_data = testssl_parser(testssl_data)

        # Here, you can save `parsed_testssl_data` to your MySQL database

        # For semgrep - save the uploaded file, if it exists
        uploaded_file = request.files.get('file')
        if uploaded_file:
            uploaded_file.save("temp.zip")
            # Run semgrep and wait for its completion
            with open("semgrep_results.txt", "w") as outfile:
                subprocess.run(["docker", "run", "--rm", "-v", "${PWD}:/src", "returntocorp/semgrep", "--config", "p/r2c-ci", "--output", "semgrep_results.txt", "temp.zip"], stdout=outfile)
                # Ensuring the command completes and the file is written before reading
                time.sleep(5)

            with open("semgrep_results.txt", "r") as file:
                semgrep_data = file.read()

            # Parse semgrep data
            parsed_semgrep_data = semgrep_parser(semgrep_data)

            # Here, you can save `parsed_semgrep_data` to your MySQL database

        return jsonify({"status": "success", "message": "Analysis complete."}), 200

    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)}), 500


@app.route('/get_results/<customer_id>', methods=['GET'])
def get_results(customer_id):
    # Here, fetch the results from the database for the given customer_id and return them
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

