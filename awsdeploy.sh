#!/bin/bash
if [ -z ${1+x} ]; then echo "Stage name required. Ex: $0 dev testlibnd-serverless"; exit; else echo "Deploying to stage '$1'"; fi
if [ -z ${2+x} ]; then echo "Deploy bucket required. Ex: $0 dev testlibnd-serverless"; exit; else echo "Deploying to bucket '$2'"; fi
if [ -z ${ILLIAD_KEY+x} ]; then echo "Environment variable ILLIAD_KEY required"; exit; fi
if [ -z ${ALEPH_PATH+x} ]; then echo "Environment variable ALEPH_PATH required"; exit; fi
if [ -z ${AWS_ROLE_ARN+x} ]; then echo "Environment variable AWS_ROLE_ARN required"; exit; fi

STAGE_NAME=$1
DEPLOY_BUCKET=$2

serverless deploy --deployBucket $DEPLOY_BUCKET --stage $STAGE_NAME

# Encrypt contentful tokens and inject into the fetch function env
KMS_ARN="alias/portalResources-$STAGE_NAME"

ALEPH_PATH=`aws kms encrypt --key-id $KMS_ARN --plaintext $ALEPH_PATH | jq -r ".CiphertextBlob"`
aws lambda update-function-configuration \
  --function-name portalResources-$STAGE_NAME-aleph \
  --environment "Variables={ ALEPH_PATH='$ALEPH_PATH' }"

ILLIAD_KEY=`aws kms encrypt --key-id $KMS_ARN --plaintext $ILLIAD_KEY | jq -r ".CiphertextBlob"`
aws lambda update-function-configuration \
  --function-name portalResources-$STAGE_NAME-illiad \
  --environment "Variables={ ILLIAD_KEY='$ILLIAD_KEY' }"
