pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out EDMS source code from GitHub'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Checking Python syntax'
                sh 'python3 -m py_compile app.py'
            }
        }

        stage('Test') {
            steps {
                echo 'Validating project files'
                sh 'test -f Dockerfile'
                sh 'test -f docker-compose.yml'
            }
        }

    }
}
