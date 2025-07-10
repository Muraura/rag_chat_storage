pipeline {
    agent any

    environment {
        IMAGE_NAME = "galboss/rag_chat_storage"
        DOCKER_CREDENTIALS_ID = 'rag_chat_dockerhub-creds-id'  // Jenkins DockerHub creds id
    }

    stages {
        stage('Clone Repo') {
            steps {
                git 'https://github.com/Muraura/rag_chat_storage.git'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest tests/'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME:$BUILD_NUMBER .'
            }
        }

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                    sh """
                        echo $PASSWORD | docker login -u $USERNAME --password-stdin
                        docker push $IMAGE_NAME:$BUILD_NUMBER
                    """
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'ragchatclust_correct', variable: 'KUBECONFIG')]) {
                    sh """
                        kubectl set image deployment/fastapi-app-deployment fastapi-app=$IMAGE_NAME:$BUILD_NUMBER --kubeconfig=$KUBECONFIG
                    """
                }
            }
        }
    }
}
