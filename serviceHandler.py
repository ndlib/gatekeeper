import json
from hesburgh import heslog
from serviceRequests.aleph import Aleph
from serviceRequests.illiad import Illiad

# need to figure out what is secret in aleph + how to handle secrets in lambda

requestTypes = {
  "borrowed": ["checkedOut", "web"],
  "pending": ["pending"],
}

def _handle(service, requestType):
  data = {
    'user': service.request("user")
  }

  toGet = requestTypes[requestType]
  for key in toGet:
    data[key] = service.request(key)

  return data


def _success(data):
  heslog.info("success")
  return data


def _error():
  return {
    "statusCode": 404,
  }


def aleph(event, context):
  requestType = event.get("type", None)
  heslog.addContext(fn="aleph", trace=event.get("trace", ""), requestType=requestType)
  heslog.info("Starting request")

  netid = event.get("netid", None)
  if netid is None:
    heslog.error("no netid")
    return _error()

  data = _handle(Aleph(netid), requestType)
  return _success(data)


def illiad(event, context):
  requestType = event.get("type", None)
  heslog.addContext(fn="illiad", trace=event.get("trace", ""), requestType=requestType)
  heslog.info("Starting request")

  netid = event.get("netid", None)
  if netid is None:
    heslog.error("no netid")
    return _error()

  data = _handle(Illiad(netid), requestType)
  return _success(data)

