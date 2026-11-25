pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out EDMS source code'
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

        stage('Docker Image Build') {
            steps {
                withCredentials([file(credentialsId: 'edms-env-file',
                    variable: 'ENV_FILE')]) {
                    sh '''
                        set -eu
                        cp "$ENV_FILE" .env
                        chmod 600 .env
                        trap 'rm -f .env' EXIT
                        docker compose -p edms-flask-project build web
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([file(credentialsId: 'edms-env-file',
                    variable: 'ENV_FILE')]) {
                    sh '''
                        set -eu
                        cp "$ENV_FILE" .env
                        chmod 600 .env
                        trap 'rm -f .env' EXIT
                        docker compose -p edms-flask-project up -d --no-build
                    '''
                }
            }
        }

        stage('Verification') {
            steps {
                echo 'Checking EDMS website'
                sh '''
                    for attempt in $(seq 1 10); do
                        if curl -fsS http://localhost:5000/ > /dev/null; then
                            echo "EDMS website is responding successfully"
                            exit 0
                        fi
                        sleep 3
                    done

                    echo "EDMS website verification failed"
                    exit 1
                '''
            }
        }
    }
}
