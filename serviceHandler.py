import json
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
  return {
    "statusCode": 200,
    "body": json.dumps(data),
  }


def _error():
  return {
    "statusCode": 404,
  }


def aleph(event, context):
  netid = event.get("netid", None)
  if netid is None:
    return _error()

  requestType = event.get("type", None)
  data = _handle(Aleph(netid), requestType)

  return _success(data)


def illiad(event, context):
  netid = event.get("netid", None)
  if netid is None:
    return _error()

  requestType = event.get("type", None)
  data = _handle(Illiad(netid), requestType)

  return _success(data)

