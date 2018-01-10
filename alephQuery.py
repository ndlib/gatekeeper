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
def iterateOnRecord(data, idToGet, i1=None, i2=None):
  # make sure our identifiers are strings
  idToGet = str(idToGet)
  if i1 is not None:
    i1 = str(i1)
  if i2 is not None:
    i2 = str(i2)

  # iterate over all fields, yielding only those that match our identifiers
  for field in data:
    if ((field["id"] == idToGet or field["label"] == idToGet) and
        (not i1 or (i1 and field["i1"] == i1)) and
        (not i2 or (i2 and field["i2"] == i2))
      ):
      yield field

# helper to get first (or only) element of a field
def fromRecord(data, idToGet=None, i1=None, i2=None, subfield=None):
  # ensure we're using strings
  if subfield is not None:
    subfield = str(subfield)

  # get the record, use given data if we don't have ids (gettings subfield)
  found = None
  if not idToGet:
    found = data
  else:
    # this allows us to reuse code, we have to start a loop to deref the iterator
    for x in iterateOnRecord(data, idToGet, i1, i2):
      found = x
      break

  # If we want to find a subfield of the above field
  if found and subfield:
    for sub in found.subfield:
      if sub["label"] == subfield:
        # Found the desired subfield, return it's data
        return sub.cdata.strip()
    # Didn't find the subfield, return failure
    return None
  return found

# helper to append to a string with a newline
def appendDataStr(data, key, toAppend):
  return toAppend.strip() if key not in data else ("%s\n%s" % (data.get(key, ""), toAppend.strip()))

def findItem(event, context):
  itemId = event.get("pathParameters", {}).get("systemId")
  heslog.addLambdaContext(event, context, sysId=itemId)

  outData = {}

  if not itemId:
    heslog.error("No system id provided")
    return _error(400)

  aleph = Aleph()
  parsed = aleph.findItem(itemId)
  heslog.info("Got response from aleph")
  if not parsed:
    heslog.error("Nothing in parsed information")
    return _error(500)

  # yay super nested xml documents!
  record = parsed.find_doc.record.metadata.oai_marc.varfield

  # As an example of what we're matching
  # This is the marc xml
  # <varfield id="730" i1="0" i2=" ">
  #   <subfield label="a">Literature online.</subfield>
  # </varfield>
  # often we don't care about i1 or i2, only id and the subfield with label "a"
  # but sometimes we must match i1 and/or i2 to make sure we're getting useful information to display
  # Some fields can have multiple entries, eg: 856
  # for this we must iterate over all the entires, hence "iterateOnRecord"

  # name
  outData["name"] = fromRecord(record, 245, subfield="a").strip().strip(punctuation)

  # description
  description = fromRecord(record, 520)
  for instance in iterateOnRecord(record, 520):
    # If there's a 520 with subfield 9 of value g, that's the one we want
    if fromRecord(instance, subfield="9") == "g":
      description = instance
      break
  outData["description"] = fromRecord(description, subfield="a")

  # url (legacy)
  outData["purl"] = fromRecord(record, 856, 4, 0, subfield="u")

  # all urls with titles and notes
  urls = []
  for url in iterateOnRecord(record, 856, 4, 0):
    urls.append({
      "url": fromRecord(url, subfield="u"),
      "title": fromRecord(url, subfield=3),
      "notes": fromRecord(url, subfield="z"),
    })
  outData["urls"] = urls

  # access data
  for letter in ['f', 'a', 'c']:
    for a in iterateOnRecord(record, 506):
      accessValue = fromRecord(a, subfield=letter)
      if accessValue:
        accessValue = accessValue.strip().strip(punctuation) \
                      .replace("Online access with authorization", "Notre Dame faculty, staff, and students") \
                      .replace("Access restricted to subscribers", "Notre Dame faculty, staff, and students") \
                      .replace("Unrestricted online access", "Public")
        outData["access"] = appendDataStr(outData, "access", accessValue)

  # includes
  for inc in iterateOnRecord(record, 740, i2=2):
    outData["includes"] = appendDataStr(outData, "includes", fromRecord(inc, subfield="a").strip(punctuation))

  # meta (platform, publisher, provider)
  for meta in iterateOnRecord(record, 710, i2=" "):
    sub4 = fromRecord(meta, subfield=4)
    metaValue = fromRecord(meta, subfield="a")

    if sub4 == "pltfrm":
      outData["platform"] = appendDataStr(outData, "platform", metaValue)
    elif sub4 == "pbl":
      outData["publisher"] = appendDataStr(outData, "publisher", metaValue)
    elif sub4 == "prv":
      outData["provider"] = appendDataStr(outData, "provider", metaValue)

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
  heslog.info("Returning %s" % renewData)
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
