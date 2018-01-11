#!groovy
properties([
    pipelineTriggers([[$class:"SCMTrigger", scmpoll_spec:"H/2 * * * *"]])
])

pipeline {
  agent { label 'docker-slave' }
stages{
      stage('Get Code') {
        steps {
            checkout scm
        }
      }
     stage('Build') {
       steps {
          sh '''
          passwd=`aws ecr get-login --region us-east-1 | awk '{ print \$6 }'`
          docker login -u AWS -p \$passwd 538745987955.dkr.ecr.us-east-1.amazonaws.com/kf-api-dataservice:latest
          docker build -t 538745987955.dkr.ecr.us-east-1.amazonaws.com/kf-api-dataservice:latest .
          '''
       }
     }
     stage('Publish') {
       steps {
          sh '''
          docker push 538745987955.dkr.ecr.us-east-1.amazonaws.com/kf-api-service:latest
          '''
       }
     }
     stage('Deploy Dev') {
        steps {
           sh '''
           rm -rf aws-ecs-service-*
           git clone git@github.com:kids-first/aws-ecs-service-type-1.git
           cd aws-ecs-service-type-1/
           echo "Setting up backend"
           echo 'key        = "dev/kf-dev-api-dataservice-us-east-1-RSF"' >> dev.conf
           terraform init -backend=true -backend-config=dev.conf
           terraform validate -var 'application=api-dataservice' -var 'service_name="kf-api-dataservice"' -var 'owner="jenkins"' -var-file=dev.tfvar
           terraform apply --auto-approve -var 'application=api-dataservice' -var 'service_name="kf-api-dataservice"' -var 'owner="jenkins"' -var-file=dev.tfvar
           '''
        }
     }
   }
}
