orchestrator_ali
# README: Orchestrator
# Overview

The Orchestrator is a tool designed to automate and streamline security analyses. It integrates with testssl and semgrep to provide comprehensive vulnerability assessments and code analysis. The results are then parsed and stored in a MySQL database.

# Prerequisites

Docker and Docker Compose installed
Ensure that the ports 5000 and 3307 are free on your machine.
Getting Started

## 1. Clone the repository:
`gh repo clone aliraf62/Orchestration-Project`


## 2. Change directory into the orchestrator folder:

`cd orchestrator`


## 3. Build and run the Docker containers:

`docker-compose up --build`


# **Usage**

To trigger an analysis, use one of the following curl commands:

1 `curl -X POST -F "url=[target-url]" -F "customer_id=[id]" http://localhost:5000/analyze`

2 `curl -X POST -F "file=@path/to/zipfile" "customer_id=[id]" http://localhost:5000/analyze`

3 `curl -X POST -F  "url=[target-url]" file=@path/to/zipfile http://localhost:5000/run_testssl`

Replace `[target-url]` with the URL you want to analyze, `@path/to/zipfile` with the absolute path to the zip file and `[id]` with a customer identifier.

Note: The analyze route in the containerized flask api will detect whether there is a url, zip file path in the curl command and choose either of semgrep(1), testssl(2) routes or both(3).

# **View Logs**

To see the logs for a particular service, use the following command:

docker-compose logs [service-name]


For example, to view the logs for the app, you can use:

`docker-compose logs app`

How It Works

Upon receiving a request, the Orchestrator will:

Run testssl/semgrep/both against the provided URL/zipfile if a URL/zipfile is given.
If a file is provided, semgrep will be run for code analysis.
The results from these tools are then parsed using custom parsers and stored in the MySQL database.

# Troubleshooting

I am working to improve the parsers and to reduce redundancy of the data written to the db since testssl runs the same tests on multiple IPs for the same URL probably due to DNS load balancing or geographically distributed systems (Content Delivery Networks).

Special thanks to the testssl and semgrep projects for providing the tools integrated into this project. Special thanks to Andrei Agape for his patience.

# License

This project is licensed under the MIT License. 
