from hesburgh import heslog, hestest
import json
from lambdaRequests.requester import Requester

hestest.init(__file__, "testdata")

# need to figure out what is secret in aleph + how to handle secrets in lambda
def borrowed(event, context):
  heslog.addLambdaContext(event, context, fn="borrowed")
  netid = event.get("requestContext", {}).get("authorizer", {}).get("netid", None)
  heslog.info("Starting request")

  if netid is None:
    heslog.error("No netid found")
    return {"statusCode": 404}

  trace = context.aws_request_id if context else None

  requester = Requester(netid, trace)
  data = requester.checkedOut()

  heslog.info("Success")
  response = {
    "statusCode": 200,
    "headers": {
      "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
    },
    "body": json.dumps(data)
  }

  return response


def pending(event, context):
  heslog.addLambdaContext(event, context, fn="pending")
  netid = event.get("requestContext", {}).get("authorizer", {}).get("netid", None)
  heslog.info("Starting request")

  if netid is None:
    heslog.error("No netid found")
    return {"statusCode": 404}

  trace = context.aws_request_id if context else None

  requester = Requester(netid, trace)
  data = requester.pending()

  heslog.info("Success")
  response = {
    "statusCode": 200,
    "headers": {
      "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
    },
    "body": json.dumps(data)
  }

  return response
