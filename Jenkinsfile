pipeline {
    agent any
    
    environment {
        AWS_REGION = 'ap-southeast-1'
        IMAGE_NAME = 'lambdacicd'
        ECR_REPOSITORY_URI = 'xxxxx.dkr.ecr.ap-southeast-1.amazonaws.com/lambdacicd'
        IMAGE_TAG = 'latest'
        LAMBDA_FUNCTION_NAME = 'lambdacicd'
        EVENT_RULE_NAME = 'daily-trigger-lambdacicd'
        IAM_ROLE = 'arn:aws:iam::xxxxxx:role/LambdaAdminxxxxxxx'
        ACCOUNT_ID = 'xxxxxx'
    }

    stages {
        stage('Build and Push Docker Image') {
            steps {
                // script {
                //     docker.build("${ECR_REPOSITORY_URI}:${IMAGE_TAG}")
                // }
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'AWS_CREDENTIALS']]) {
                    script {
                        sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY_URI}"
                        sh "docker build -t lambdacicd ."
                        sh "docker tag lambdacicd:${IMAGE_TAG} ${ECR_REPOSITORY_URI}:${IMAGE_TAG}"
                        sh "docker push ${ECR_REPOSITORY_URI}:${IMAGE_TAG}"
                        }
                    }
                }
            }
        

        stage('Deploy to AWS Lambda') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'AWS_CREDENTIALS']]) {
                    script {
                        def lambdaExists = sh(script: "aws lambda get-function --function-name ${LAMBDA_FUNCTION_NAME} --region ${AWS_REGION}", returnStatus: true)
                        if (lambdaExists == 0) {
                            echo "Lambda function ${LAMBDA_FUNCTION_NAME} exists. Proceeding to update."
                            // Code to update the existing Lambda function
                            sh "aws lambda update-function-code --function-name ${LAMBDA_FUNCTION_NAME} --image-uri ${ECR_REPOSITORY_URI}:${IMAGE_TAG} --region ${AWS_REGION} --architectures x86_64"
                        }
                        else {
                        echo "Lambda function ${LAMBDA_FUNCTION_NAME} does not exist. Proceeding to create."
                            // Code to create a new Lambda function
                            sh """
                            aws lambda create-function --function-name ${LAMBDA_FUNCTION_NAME} \
                                --package-type Image \
                                --timeout 30 \
                                --memory-size 256 \
                                --role ${IAM_ROLE} \
                                --code ImageUri=${ECR_REPOSITORY_URI}:${IMAGE_TAG} \
                                --region ${AWS_REGION} \
                                --architectures x86_64
                            """
                        } 
                    }
                }
            }
        }

        stage('Create EventBridge Rule') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'AWS_CREDENTIALS']]) {
                    script {
                        sh """
                        aws events put-rule --name ${EVENT_RULE_NAME} --schedule-expression 'cron(0 4 * * ? *)' --region ${AWS_REGION}
                        aws events put-targets --rule ${EVENT_RULE_NAME} --targets "Id"="1","Arn"="arn:aws:lambda:${AWS_REGION}:${ACCOUNT_ID}:function:${LAMBDA_FUNCTION_NAME}"
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            // Clean the workspace
            cleanWs()
        }
    }
}
