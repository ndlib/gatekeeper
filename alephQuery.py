from hesburgh import heslog, hesutil
from serviceRequests.aleph import Aleph
from string import punctuation
import json

def _error(code):
  return {
    "statusCode": code,
    "headers": {
      "Access-Control-Allow-Origin": "*",
      "x-nd-version": hesutil.getEnv("VERSION", 0),
    },
  }

def _success(data):
  return {
    "statusCode": 200,
    "body": json.dumps(data),
    "headers": {
      "Access-Control-Allow-Origin": "*",
      "x-nd-version": hesutil.getEnv("VERSION", 0),
    },
  }

# helper so we don't have to have if logic on every field below
def iterate(field):
  if isinstance(field, list):
    for i in field:
      yield i
  else:
    yield field

# helper to get first (or only) element of a field
def first(field):
  for x in iterate(field):
    return x


def findItem(event, context):
  itemId = event.get("pathParameters", {}).get("systemId")
  heslog.addLambdaContext(event, context, sysId=itemId)

  outData = {}

  if not itemId:
    heslog.error("No system id provided")
    return _error(400)

  aleph = Aleph(None)
  parsed = aleph.findItem(itemId)
  heslog.info("Got response from aleph")
  if not parsed:
    heslog.error("Nothing in parsed information")
    return _error(500)

  record = parsed.get("record", {}).get("metadata", {}).get("oai_marc", {})

  # name
  outData["name"] = record.get("varfield_245_0", {}).get("subfield_a", "").strip()

  # description
  recordDescription = record.get("varfield_520", {})
  description = first(recordDescription)
  for instance in iterate(recordDescription):
    # If there's a 520 with subfield 9 of value g, that's the one we want
    if instance.get("subfield_9", "") == "g":
      description = instance
      break
  outData["description"] = description.get("subfield_a", "").strip()

  # url
  outData["url"] = first(record.get("varfield_856_0", {})).get("subfield_u", "").strip()

  # access data
  access = record.get("varfield_506", {})
  for letter in ['f', 'a', 'c']:
    for a in iterate(access):
      accessValue = a.get("subfield_" + letter)
      if accessValue:
        outData["access"] = "%s%s\n" % (outData.get("access", ""), accessValue.strip())
  outData["access"] = outData.get("access", "").strip()

  # restrictions
  outData["restrictions"] = record.get("varfield_540", {}).get("subfield_a", "").strip()

  # includes
  for inc in iterate(record.get("varfield_740_2", {})):
    outData["includes"] = "%s%s\n" % (outData.get("includes", ""), inc.get("subfield_a", "").strip().strip(punctuation))
  outData["includes"] = outData.get("includes", "").strip().title().strip(punctuation)

  # meta (platform, publisher, provider)
  for meta in iterate(record.get("varfield_710")):
    sub4 = meta.get("subfield_4", "")
    metaValue = meta.get("subfield_a", "").strip()

    if sub4 == "pltfrm":
      outData["platform"] = metaValue
    elif sub4 == "pbl":
      outData["publisher"] = metaValue
    elif sub4 == "prv":
      outData["provider"] = metaValue

  heslog.info("Returning success")
  return _success(outData)


def renewItem(event, context):
  params = event.get("headers", {})
  barcode = params.get("barcode")
  heslog.addLambdaContext(event, context, barcode=barcode)

  alephId = params.get("aleph-id")

  if not barcode:
    heslog.error("No barcode provided")
    return _error(400)

  if not alephId:
    heslog.error("No aleph id provided")
    return _error(400)

  aleph = Aleph(alephId)
  renewData = aleph.renew(barcode)
  heslog.info("Returning success %s" % renewData)
  return _success(renewData)


def updateUser(event, context):
  params = event.get("headers", {})
  library = params.get("library")
  heslog.addLambdaContext(event, context, library=library)

  alephId = params.get("aleph-id")

  if not library:
    heslog.error("No library provided")
    return _error(400)

  if not alephId:
    heslog.error("No aleph id provided")
    return _error(400)

  aleph = Aleph(alephId)
  updateSuccess = aleph.updateHomeLibrary(library)
  if updateSuccess:
    heslog.info("Returning success")
    return _success({})
  return _error(500)
