import json
from requests.requester import Requester

# need to figure out what is secret in aleph + how to handle secrets in lambda

def loanedItems(event, context):
  # print event
  netid = "rfox2"

  requester = Requester(netid)

  data = {
    'checkedOut': requester.checkedOut(),
    'web': requester.web(),
    'pending': requester.pending(),
  }

  # print json.dumps(data, indent=2)

  response = {
    "statusCode": 200,
    "body": json.dumps(data)
  }

  return response

