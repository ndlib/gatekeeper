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

  # Description is more complicated. We need 520 which could just be 1 record or multiple
  # If there's a 520 with subfield 9 of value g, that's the one we want
  recordDescription = record.get("varfield_520", {})
  description = None
  if isinstance(recordDescription, list):
    for i in recordDescription:
      if i.get("subfield_9", "") == "g":
        description = i
        break
    if not description:
      description = recordDescription[0]
  else:
    description = recordDescription
  description = description.get("subfield_a", "").strip()

  url = record.get("varfield_856_0", {})
  if isinstance(url, list):
    url = url[0]
  url = url.get("subfield_u", "").strip()

  return _success({
      "name": name,
      "description": description,
      "purl": url,
    })
