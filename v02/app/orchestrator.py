from flask import Flask, request, jsonify
import mysql.connector
import os
from semgrep_parser import semgrep_parser
from testssl_parser import testssl_parser
import docker
import time
import json

app = Flask(__name__)

# MySQL configurations
db_config = {
    'user': os.getenv('DB_USER', 'user'),
    'password': os.getenv('DB_PSWD', 'password'),
    'host': os.getenv('DB_HOST', 'db'),
    'database': os.getenv('DB_NAME', 'orchestrator'),
    'raise_on_warnings': True
}

MAX_RETRIES = 5
RETRY_DELAY = 5  # 5 seconds

# Create a MySQL connection pool with a retry mechanism
for _ in range(MAX_RETRIES):
    try:
        pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=10, **db_config)
        break
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        time.sleep(RETRY_DELAY)
else:
    raise ConnectionError("Could not establish connection to the database after multiple retries.")


def get_db_connection():
    """Utility function to get a database connection from the pool."""
    return pool.get_connection()


@app.route('/')
def hello():
    return "Root endpoint is called. Please use analyze route. URL and/or source code zip file path should be provided."


@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form.get('url')
    customer_id = request.form.get('customer_id')
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    # Check if a URL was provided for testssl
    if url:
        try:
            container = client.containers.run('testssl-image', ['--jsonfile', '/data/', url],
                                              volumes={'/tmp': {'bind': '/data', 'mode': 'rw'}}, remove=True)
            parsed_data = testssl_parser(container.decode('utf-8'))
            save_to_db(customer_id, parsed_data, "testssl")
        except Exception as e:
            print(f"Error with testssl analysis: {e}")
            return jsonify({"message": "Error during testssl analysis."}), 500


    # Check if a file was provided for semgrep
    file = request.files.get('file')
    if file:
        file_path = "/tmp/temp.zip"
        file.save(file_path)
        try:
            container = client.containers.run('semgrep', ['semgrep', '--config', 'auto'],
                                              volumes={file_path: {'bind': '/src/semgrep2', 'mode': 'ro'}}, remove=True)
            parsed_data = semgrep_parser(container.decode('utf-8'))
            save_to_db(customer_id, parsed_data, "semgrep")
        except Exception as e:
            print(f"Error with semgrep analysis: {e}")
        finally:
            os.remove(file_path)

    return jsonify({"message": "Analysis completed."})


def save_to_db(customer_id, parsed_data, analysis_type):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        if analysis_type == "testssl":
            print("Committing testssl results to db")
            full_results = json.dumps(parsed_data['full_results'])
            findings = parsed_data['findings']
            for finding in findings:
                host = finding['host']
                finding_type = finding['finding_type']
                description = finding['description']
                details_link = finding['details_link']
                query = ("INSERT INTO testssl_results (customer_id, host, finding_type, description, details_link, full_results) "
                         "VALUES (%s, %s, %s, %s, %s, %s)")
                cursor.execute(query, (customer_id, host, finding_type, description, details_link, full_results))

        elif analysis_type == "semgrep":
            print("Committing semgrep results to db")
            for data in parsed_data:
                query = "INSERT INTO semgrep (customer_id, data) VALUES (%s, %s)"
                cursor.execute(query, (customer_id, str(data)))

        connection.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()  # Important: Rollback in case of error to maintain database consistency

    finally:
        cursor.close()
        connection.close()  # Release the connection back to the pool


@app.route('/report', methods=['GET'])
def report():
    customer_id = request.args.get('customer_id')
    connection = get_db_connection()
    cursor = connection.cursor()
    results = []

    try:
        # Fetch testssl data
        cursor.execute("SELECT host, finding_type, description, details_link, full_results FROM testssl_results WHERE customer_id = %s", (customer_id,))
        testssl_data = cursor.fetchall()
        for record in testssl_data:
            results.append({
                "type": "testssl",
                "host": record[0],
                "finding_type": record[1],
                "description": record[2],
                "details_link": record[3],
                "full_results": record[4]  # This is the full JSON data
            })

        # Fetch semgrep data (unchanged as no modifications were made to semgrep schema)
        cursor.execute("SELECT file_path, rule_id, description, full_results FROM semgrep_results WHERE customer_id = %s", (customer_id,))
        semgrep_data = cursor.fetchall()
        for record in semgrep_data:
            results.append({
                "type": "semgrep",
                "file_path": record[0],
                "rule_id": record[1],
                "description": record[2],
                "full_results": record[3]  # This is the full JSON data
            })

    finally:
        cursor.close()
        connection.close()

    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
