from hesburgh import heslog
from serviceRequests.aleph import Aleph
import json

def _error():
  return {
    "statusCode": 404,
  }

def _success(data):
  return {
    "statusCode": 200,
    "body": json.dumps(data)
  }

def findItem(event, context):
  itemId = event.get("pathParameters", {}).get("systemId")
  heslog.addLambdaContext(event, context, sysId=itemId)

  if not itemId:
    heslog.error("No system id provided")
    return _error()

  aleph = Aleph(None)
  parsed = aleph.findItem(itemId)

  record = parsed.get("record", {}).get("metadata", {}).get("oai_marc", {})
  name = record.get("varfield_245_0", {}).get("subfield_a", "").strip()
  desc = record.get("varfield_520", {}).get("subfield_a", "").strip()
  url = record.get("varfield_856_0", {}).get("subfield_u", "").strip()

  return _success({
      "name": name,
      "description": desc,
      "purl": url,
    })
