import json
from hesburgh import heslog, hesutil, hestest
from serviceRequests.aleph import Aleph
from serviceRequests.illiad import Illiad

hestest.init(__file__, "testdata")

requestTypes = {
  "borrowed": ["checkedOut", "web"],
  "pending": ["pending"],
  "user": ["user"],
}

def _handle(service, requestType):
  data = {}
  toGet = requestTypes[requestType]
  for key in toGet:
    data[key] = service.request(key)

  return data


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


def _error(code):
  return {
    "statusCode": code,
    "headers": {
      "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
      "x-nd-version": hesutil.getEnv("VERSION", 0),
    },
  }


def aleph(event, context):
  requestType = event.get("queryStringParameters", {}).get("type", None)
  netid = event.get("requestContext", {}).get("authorizer", {}).get("netid", None)

  heslog.addLambdaContext(event, context, fn="aleph", requestType=requestType)

  if netid is None:
    heslog.error("no netid")
    return _error(401)

  if requestType is None:
    heslog.error("no query type specified")
    return _error(400)

  heslog.info("Starting request")
  data = _handle(Aleph(netid), requestType)
  heslog.info("Success")
  return _success(data)


def illiad(event, context):
  requestType = event.get("queryStringParameters", {}).get("type", None)
  netid = event.get("requestContext", {}).get("authorizer", {}).get("netid", None)

  heslog.addLambdaContext(event, context, fn="illiad", requestType=requestType)

  if netid is None:
    heslog.error("no netid")
    return _error(401)

  if requestType is None:
    heslog.error("no query type specified")
    return _error(400)

  heslog.info("Starting request")
  data = _handle(Illiad(netid), requestType)
  heslog.info("Success")
  return _success(data)

