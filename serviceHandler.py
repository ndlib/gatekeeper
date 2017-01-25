import json
from serviceRequests.aleph import Aleph
from serviceRequests.illiad import Illiad

# need to figure out what is secret in aleph + how to handle secrets in lambda

netid = "rfox2"
# netid = "lajamie"

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


def _requestType(path):
  for k,v in requestTypes.iteritems():
    if k in path:
      return k
  return None


def aleph(event, context):
  requestType = _requestType(event["path"])
  data = _handle(Aleph(netid), requestType)

  return _success(data)


def illiad(event, context):
  requestType = _requestType(event["path"])
  data = _handle(Illiad(netid), requestType)

  return _success(data)

