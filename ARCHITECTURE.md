# EDMS – CI/CD Pipeline Architecture

**1. Project Overview**

The Electronic Device Management System (EDMS) is an existing Flask-based web application integrated with an automated CI/CD pipeline.

The main objective of this project is to automate application building, testing, and deployment using GitHub, Jenkins, Docker, and Docker Compose.

The application and database are deployed locally in Ubuntu WSL.

**2. Technologies Used**

- **Python Flask:** Backend web application.
- **MySQL 8.0:** Database management.
- **Git and GitHub:** Source code management and version control.
- **Jenkins:** Continuous Integration and Continuous Deployment automation.
- **Docker:** Application and database containerization.
- **Docker Compose:** Management of multiple containers.
- **Gunicorn:** WSGI server for running the Flask application.
- **Ubuntu WSL:** Local development and deployment environment.

**3. Project Architecture**

The project consists of the following major components:

1. **Developer:** Makes changes to the application source code.
2. **GitHub:** Stores and manages the project source code in the main branch.
3. **Jenkins:** Monitors the GitHub repository using Poll SCM and executes the pipeline.
4. **Docker:** Builds the Flask application image.
5. **Docker Compose:** Manages and deploys the Flask and MySQL containers.
6. **Flask Application:** Handles user requests and application functionality.
7. **MySQL Database:** Stores users, products, orders, and payments.
8. **Docker Volume:** Provides persistent storage for database records.

**4. CI/CD Pipeline Workflow**

The automated CI/CD process follows these steps:

1. The developer makes changes to the application code.
2. Changes are committed and pushed to GitHub.
3. Jenkins periodically checks the GitHub repository using Poll SCM.
4. Jenkins detects a new commit.
5. Jenkins automatically triggers the pipeline.
6. Jenkins retrieves the latest source code from GitHub.
7. The pipeline performs build and validation checks.
8. Docker builds the updated Flask application image.
9. Docker Compose deploys the updated application.
10. Jenkins verifies whether the website is responding successfully.

**5. Jenkins Pipeline Stages and Their Purposes**

The Jenkinsfile contains six stages:

1. Checkout – Retrieves the latest source code from the GitHub repository.

2. Build – Checks Python syntax using `python3 -m py_compile app.py`.

3. Test – Validates the presence of required files, including Dockerfile and docker-compose.yml.

4. Docker Image Build – Builds the updated Flask application Docker image using Docker Compose.

5. Deploy – Deploys or updates the application containers using Docker Compose.

6. Verification – Uses curl to check whether the application website is responding successfully.

**6. Docker Configuration**

**Dockerfile**

The Dockerfile defines how the Flask application Docker image is created. It uses Python 3.12, installs the required dependencies, copies the application files, exposes port 5000, and runs the application using Gunicorn.

**Docker Compose**

The docker-compose.yml file manages two services:

- **web:** Runs the Flask application.
- **db:** Runs the MySQL 8.0 database.

The Flask application connects to MySQL using the Docker Compose service name `db`.

The application waits for the database health check to succeed before starting.

**7. Database Persistence**

MySQL data is stored in a named Docker volume:

`edms_mysql_data`

The volume is mounted at:

`/var/lib/mysql`

This ensures that database records remain available when containers are restarted or recreated, provided the volume is retained.

Database persistence was verified by restarting the Docker Compose services and checking the database records afterward.

**8. Environment Configuration and Security**

Database credentials and the Flask secret key are stored in a local `.env` file.

- The `.env` file is excluded from Git using `.gitignore`.
- Jenkins accesses the environment configuration through a Secret File credential with ID `edms-env-file`.
- The Jenkins pipeline uses the environment file during Docker image building and deployment.
- Temporary `.env` copies are removed from the Jenkins workspace after use.

Sensitive credentials must never be committed to GitHub or printed in Jenkins console logs.

**9. Application Access**

The application runs locally and can be accessed using:

**EDMS Website:** http://localhost:5000

**Jenkins Dashboard:** http://localhost:8080

**10. Project Outcome**

This project demonstrates the implementation of an automated CI/CD pipeline for an existing Flask-based web application.

Whenever the developer pushes code changes to GitHub, Jenkins detects the changes through Poll SCM and automatically executes the pipeline.

The pipeline checks the source code, validates project files, builds the Docker image, deploys the updated application using Docker Compose, and verifies the website.

The Flask application and MySQL database run in Docker containers locally in Ubuntu WSL, with persistent database storage configured through a Docker volume.

This project demonstrates practical knowledge of Git, GitHub, Jenkins, Docker, Docker Compose, containerization, and CI/CD automation.

**Note:** The CI/CD pipeline is deployed locally using Ubuntu WSL, Jenkins, Docker, and Docker Compose. AWS EC2 was avoided due to the cost of running a cloud server 24/7, which may not be practical for a student project.
