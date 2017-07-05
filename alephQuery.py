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
  heslog.info("Got %s from aleph" % parsed)
  if not parsed:
    return _error()

  record = parsed.get("record", {}).get("metadata", {}).get("oai_marc", {})
  name = record.get("varfield_245_0", {})
  if isinstance(name, list):
    name = name[0]
  name = name.get("subfield_a", "").strip()

  desc = record.get("varfield_520", {})
  if isinstance(desc, list):
    desc = desc[0]
  desc = desc.get("subfield_a", "").strip()

  url = record.get("varfield_856_0", {})
  if isinstance(url, list):
    url = url[0]
  url = url.get("subfield_u", "").strip()

  return _success({
      "name": name,
      "description": desc,
      "purl": url,
    })
