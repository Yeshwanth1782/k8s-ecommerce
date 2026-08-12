pipeline {

    agent any

    environment {
        BACKEND_IMAGE  = 'yeshwanth13/ecommerce-backend'
        FRONTEND_IMAGE = 'yeshwanth13/ecommerce-frontend'
        NAMESPACE      = 'ecommerce'
    }

    stages {

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

        stage('Create Kubernetes Namespace') {
            steps {
                sh '''
                    kubectl create namespace ${NAMESPACE} \
                        --dry-run=client \
                        -o yaml | kubectl apply -f -
                '''
            }
        }

        stage('Create Kubernetes Secrets') {
            steps {

                withCredentials([
                    string(
                        credentialsId: 'ecommerce-db-password',
                        variable: 'DB_PASSWORD'
                    )
                ]) {

                    sh '''
                        kubectl create secret generic mysql-secret \
                            --namespace=${NAMESPACE} \
                            --from-literal=MYSQL_ROOT_PASSWORD="$DB_PASSWORD" \
                            --dry-run=client \
                            -o yaml | kubectl apply -f -

                        kubectl create secret generic backend-secret \
                            --namespace=${NAMESPACE} \
                            --from-literal=MYSQL_PASSWORD="$DB_PASSWORD" \
                            --dry-run=client \
                            -o yaml | kubectl apply -f -
                    '''
                }
            }
        }

        stage('Deploy MySQL') {
            steps {
                sh '''
                    kubectl apply \
                        -f k8s/mysql-pvc.yaml \
                        -n ${NAMESPACE}

                    kubectl apply \
                        -f k8s/mysql-service.yaml \
                        -n ${NAMESPACE}

                    kubectl apply \
                        -f k8s/mysql-statefulset.yaml \
                        -n ${NAMESPACE}

                    kubectl rollout status statefulset/mysql \
                        -n ${NAMESPACE} \
                        --timeout=180s
                '''
            }
        }

        stage('Deploy Backend') {
            steps {
                sh '''
                    kubectl apply \
                        -f k8s/backend-configmap.yaml \
                        -n ${NAMESPACE}

                    kubectl apply \
                        -f k8s/backend-service.yaml \
                        -n ${NAMESPACE}

                    kubectl apply \
                        -f k8s/backend-deployment.yaml \
                        -n ${NAMESPACE}

                    kubectl set image deployment/backend \
                        backend=${BACKEND_IMAGE}:${BUILD_NUMBER} \
                        -n ${NAMESPACE}

                    kubectl rollout status deployment/backend \
                        -n ${NAMESPACE} \
                        --timeout=180s
                '''
            }
        }

        stage('Deploy Frontend') {
            steps {
                sh '''
                    kubectl apply \
                        -f k8s/frontend-service.yaml \
                        -n ${NAMESPACE}

                    kubectl apply \
                        -f k8s/frontend-deployment.yaml \
                        -n ${NAMESPACE}

                    kubectl set image deployment/frontend \
                        frontend=${FRONTEND_IMAGE}:${BUILD_NUMBER} \
                        -n ${NAMESPACE}

                    kubectl rollout status deployment/frontend \
                        -n ${NAMESPACE} \
                        --timeout=180s
                '''
            }
        }

        stage('Deploy HPA') {
            steps {
                sh '''
                    kubectl apply \
                        -f k8s/hpa.yaml \
                        -n ${NAMESPACE}
                '''
            }
        }

        stage('Deploy Ingress') {
            steps {
                sh '''
                    kubectl apply \
                        -f k8s/ingress.yaml \
                        -n ${NAMESPACE}
                '''
            }
        }

        stage('Verify Application') {
            steps {
                sh '''
                    echo "===== PODS ====="
                    kubectl get pods -n ${NAMESPACE}

                    echo "===== SERVICES ====="
                    kubectl get svc -n ${NAMESPACE}

                    echo "===== DEPLOYMENTS ====="
                    kubectl get deployments -n ${NAMESPACE}

                    echo "===== HPA ====="
                    kubectl get hpa -n ${NAMESPACE}

                    echo "===== INGRESS ====="
                    kubectl get ingress -n ${NAMESPACE}
                '''
            }
        }
    }

    post {

        success {
            echo '========================================'
            echo 'CI/CD PIPELINE SUCCESSFUL'
            echo '========================================'
            echo "Backend:  ${BACKEND_IMAGE}:${BUILD_NUMBER}"
            echo "Frontend: ${FRONTEND_IMAGE}:${BUILD_NUMBER}"
            echo "Namespace: ${NAMESPACE}"
        }

        failure {
            echo '========================================'
            echo 'CI/CD PIPELINE FAILED'
            echo 'Check the failed stage in Console Output'
            echo '========================================'
        }
    }
}
