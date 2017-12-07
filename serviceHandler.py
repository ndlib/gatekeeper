import json
from hesburgh import heslog, hesutil, hestest
from serviceRequests.aleph import Aleph
from serviceRequests.illiad import Illiad
from serviceRequests.primo import Primo

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
  data = Aleph(netid, library).request(requestType)

  if data is None:
    heslog.info("No information returned from request")
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
  data = Illiad(netid).request(requestType)

  if data is None:
    heslog.info("No information returned from request")
  return _success(data)


def primo(event, context):
  queryParams = event.get("queryStringParameters", {})
  requestType = queryParams.get("type", None)
  userId = queryParams.get("userId", None)

  heslog.addLambdaContext(event, context, fn="primo", requestType=requestType)

  if userId is None:
    heslog.error("no userId")
    return _error(400)

  if requestType is None:
    heslog.error("no query type specified")
    return _error(400)

  heslog.info("Starting request")
  data = Primo(userId).request(requestType)

  if data is None:
    heslog.info("No information returned from request")
  return _success(data)

