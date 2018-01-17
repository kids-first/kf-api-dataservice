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
   stage('Test') {
     steps {
       slackSend (color: '#ddaa00', message: ":construction_worker: TESTING STARTED: Branch '${env.BRANCH} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
       sh '''
       PATH=$WORKSPACE/venv/bin:/usr/local/bin:$PATH
       if [ ! -d "venv" ]; then
               virtualenv -p python3 venv
       fi
       . venv/bin/activate
       which python
       which pip
       python -m pip install -r dev-requirements.txt
       python -m pip install -r requirements.txt
       python -m pip install -e .
       export FLASK_APP=manage
       python -m flask test
       '''
       slackSend (color: '#41aa58', message: ":white_check_mark: TESTING COMPLETED: Branch '${env.BRANCH} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
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
       docker push 538745987955.dkr.ecr.us-east-1.amazonaws.com/kf-api-dataservice:latest
       '''
       slackSend (color: '#41aa58', message: ":arrow_up: PUSHED IMAGE: Branch '${env.BRANCH} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
     }
   }
   stage('Deploy Dev') {
     when {
       expression {
         return env.BRANCH_NAME != 'master';
       }
     }
     steps {
       slackSend (color: '#005e99', message: "DEPLOYING TO DEVELOPMENT: Branch '${env.BRANCH} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
       sh '''
       rm -rf aws-ecs-service-*
       git clone git@github.com:kids-first/aws-ecs-service-type-1.git
       cd aws-ecs-service-type-1/
       echo "Setting up backend"
       echo 'key        = "dev/kf-dev-pi-dataservice-us-east-1-RSF"' >> dev.conf
       terraform init -backend=true -backend-config=dev.conf
       terraform validate -var 'image=538745987955.dkr.ecr.us-east-1.amazonaws.com/kf-api-dataservice:latest' -var 'application=dataservice-api' -var 'service_name="kf-api-dataservice"' -var 'owner="jenkins"' -var-file=dev.tfvar
       terraform apply --auto-approve -var 'image=538745987955.dkr.ecr.us-east-1.amazonaws.com/kf-api-dataservice:latest' -var 'application=dataservice-api' -var 'service_name="kf-api-dataservice"' -var 'owner="jenkins"' -var-file=dev.tfvar
       '''
       slackSend (color: '#41aa58', message: "DEPLOYED TO DEVELOPMENT: Branch '${env.BRANCH} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
     }
   }
   stage('Deploy QA') {
     when {
      expression {
          return env.BRANCH_NAME == 'master';
      }
    }
    steps {
      slackSend (color: '#005e99', message: "DEPLOYING TO QA: Branch '${env.BRANCH} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
      sh '''
      rm -rf aws-ecs-service-*
      git clone git@github.com:kids-first/aws-ecs-service-type-1.git
      cd aws-ecs-service-type-1/
      echo "Setting up backend"
      echo 'key        = "dev/kf-dev-api-dataservice-us-east-1-RSF"' >> dev.conf
      terraform init -backend=true -backend-config=dev.conf
      terraform validate -var 'image=538745987955.dkr.ecr.us-east-1.amazonaws.com/kf-api-dataservice:latest' -var 'application=dataservice-api' -var 'service_name="kf-dataservice-api"' -var 'owner="jenkins"' -var-file=dev.tfvar
      terraform apply --auto-approve -var 'image=538745987955.dkr.ecr.us-east-1.amazonaws.com/kf-api-dataservice:latest' -var 'application=dataservice-api' -var 'service_name="kf-api-dataservice"' -var 'owner="jenkins"' -var-file=dev.tfvar
      '''
      slackSend (color: '#41aa58', message: "DEPLOYED TO QA: Branch '${env.BRANCH} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
    }
   }
  }
}
