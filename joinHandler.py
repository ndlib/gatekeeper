import json
from lambdaRequests.requester import Requester

# need to figure out what is secret in aleph + how to handle secrets in lambda

netid = "rfox2"
# netid = "lajamie"

def borrowed(event, context):
  # print event

  requester = Requester(netid)
  data = requester.checkedOut()

  response = {
    "statusCode": 200,
    "body": json.dumps(data)
  }

  return response


def pending(event, context):
  requester = Requester(netid)
  data = requester.pending()

  response = {
    "statusCode": 200,
    "body": json.dumps(data)
  }

  return response
