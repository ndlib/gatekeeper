from hesburgh import heslog
import json
from lambdaRequests.requester import Requester

# need to figure out what is secret in aleph + how to handle secrets in lambda
def borrowed(event, context):
  netid = event.get("requestContext", {}).get("authorizer", {}).get("netid", None)
  if netid is None:
    return {"statusCode": 404}

  requester = Requester(netid)
  data = requester.checkedOut()

  response = {
    "statusCode": 200,
    "body": json.dumps(data)
  }

  return response


def pending(event, context):
  netid = event.get("requestContext", {}).get("authorizer", {}).get("netid", None)
  if netid is None:
    return {"statusCode": 404}

  requester = Requester(netid)
  data = requester.pending()

  response = {
    "statusCode": 200,
    "body": json.dumps(data)
  }

  return response
