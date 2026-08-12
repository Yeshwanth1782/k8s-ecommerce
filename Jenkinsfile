pipeline {

    agent any

    environment {
        BACKEND_IMAGE = 'yeshwanth13/ecommerce-backend'
        FRONTEND_IMAGE = 'yeshwanth13/ecommerce-frontend'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test Backend') {
            steps {
                sh '''
                    python3 -m py_compile app/backend/app.py
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    docker build \
                        -t ${BACKEND_IMAGE}:${BUILD_NUMBER} \
                        app/backend

                    docker build \
                        -t ${FRONTEND_IMAGE}:${BUILD_NUMBER} \
                        app/frontend
                '''
            }
        }

        stage('Push Docker Images') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login \
                            -u "$DOCKER_USERNAME" \
                            --password-stdin

                        docker push ${BACKEND_IMAGE}:${BUILD_NUMBER}
                        docker push ${FRONTEND_IMAGE}:${BUILD_NUMBER}

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl set image deployment/backend \
                        backend=${BACKEND_IMAGE}:${BUILD_NUMBER} \
                        -n ecommerce

                    kubectl set image deployment/frontend \
                        frontend=${FRONTEND_IMAGE}:${BUILD_NUMBER} \
                        -n ecommerce
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    kubectl rollout status deployment/backend \
                        -n ecommerce \
                        --timeout=180s

                    kubectl rollout status deployment/frontend \
                        -n ecommerce \
                        --timeout=180s
                '''
            }
        }

        stage('Verify Application') {
            steps {
                sh '''
                    kubectl get pods -n ecommerce
                    kubectl get svc -n ecommerce
                    kubectl get hpa -n ecommerce
                '''
            }
        }
    }

    post {

        success {
            echo 'CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD pipeline failed. Check the Jenkins console output.'
        }
    }
}
