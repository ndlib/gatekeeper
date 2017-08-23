from hesburgh import heslog, hestest, hesutil
import json
from lambdaRequests.requester import Requester

hestest.init(__file__, "testdata")

def _success(data):
  heslog.info("Success")
  return {
    "statusCode": 200,
    "headers": {
      "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
      "x-nd-version": hesutil.getEnv("VERSION", 0),
    },
    "body": json.dumps(data)
  }


def _error():
  return {
    "statusCode": 404,
    "headers": {
      "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
      "x-nd-version": hesutil.getEnv("VERSION", 0),
    },
  }


# need to figure out what is secret in aleph + how to handle secrets in lambda
def borrowed(event, context):
  heslog.addLambdaContext(event, context, fn="borrowed")
  netid = event.get("requestContext", {}).get("authorizer", {}).get("netid", None)
  heslog.info("Starting request")

  if netid is None:
    heslog.error("No netid found")
    return _error()

  trace = context.aws_request_id if context else None

  requester = Requester(netid, trace)
  data = requester.checkedOut()

  response = _success(data)

  return response


def pending(event, context):
  heslog.addLambdaContext(event, context, fn="pending")
  netid = event.get("requestContext", {}).get("authorizer", {}).get("netid", None)
  heslog.info("Starting request")

  if netid is None:
    heslog.error("No netid found")
    return _error()

  trace = context.aws_request_id if context else None

  requester = Requester(netid, trace)
  data = requester.pending()

  response = _success(data)

  return response
