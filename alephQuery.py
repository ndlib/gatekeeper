from hesburgh import heslog, hesutil
from serviceRequests.aleph import Aleph
from serviceRequests.alephDirectSql import AlephOracle
from serviceRequests.helpers import xml, response
punctuation = " ."

def findItem(event, context):
  itemId = event.get("pathParameters", {}).get("systemId")
  heslog.addLambdaContext(event, context, sysId=itemId)

  outData = {}

  if not itemId:
    heslog.error("No system id provided")
    return response.error(400)

  aleph = Aleph()
  parsed = aleph.findItem(itemId)
  heslog.info("Got response from aleph")
  if not parsed:
    heslog.error("Nothing in parsed information")
    return response.error(500)

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
  outData["name"] = xml.fromRecord(record, 245, subfield="a").strip(punctuation)

  # description
  description = xml.fromRecord(record, 520)
  for instance in xml.iterateOnRecord(record, 520):
    # If there's a 520 with subfield 9 of value g, that's the one we want
    if xml.fromRecord(instance, subfield="9") == "g":
      description = instance
      break
  outData["description"] = xml.fromRecord(description, subfield="a")

  # url (legacy)
  outData["purl"] = xml.fromRecord(record, 856, 4, 0, subfield="u")

  # all urls with titles and notes
  urls = []
  for url in xml.iterateOnRecord(record, 856, 4, 0):
    urls.append({
      "url": xml.fromRecord(url, subfield="u"),
      "title": xml.fromRecord(url, subfield=3),
      "notes": xml.fromRecord(url, subfield="z"),
    })
  outData["urls"] = urls

  # access data
  for letter in ['f', 'a', 'c']:
    for a in xml.iterateOnRecord(record, 506):
      accessValue = xml.fromRecord(a, subfield=letter)
      if accessValue:
        accessValue = accessValue.strip(punctuation) \
                      .replace("Online access with authorization", "Notre Dame faculty, staff, and students") \
                      .replace("Access restricted to subscribers", "Notre Dame faculty, staff, and students") \
                      .replace("Unrestricted online access", "Public")
        outData["access"] = xml.appendDataStr(outData, "access", accessValue)

  # includes
  for inc in xml.iterateOnRecord(record, 740, i2=2):
    outData["includes"] = xml.appendDataStr(outData, "includes", xml.fromRecord(inc, subfield="a").strip(punctuation))

  # meta (platform, publisher, provider)
  for meta in xml.iterateOnRecord(record, 710, i2=" "):
    sub4 = xml.fromRecord(meta, subfield=4)
    metaValue = xml.fromRecord(meta, subfield="a")

    if sub4 == "pltfrm":
      outData["platform"] = xml.appendDataStr(outData, "platform", metaValue)
    elif sub4 == "pbl":
      outData["publisher"] = xml.appendDataStr(outData, "publisher", metaValue)
    elif sub4 == "prv":
      outData["provider"] = xml.appendDataStr(outData, "provider", metaValue)

  heslog.info("Returning success")
  return response.success(outData)


def renewItem(event, context):
  params = event.get("headers", {})
  barcode = params.get("barcode")
  heslog.addLambdaContext(event, context, barcode=barcode)

  alephId = params.get("aleph-id")

  if not barcode:
    heslog.error("No barcode provided")
    return response.error(400)

  if not alephId:
    heslog.error("No aleph id provided")
    return response.error(400)

  aleph = Aleph(alephId)
  renewData = aleph.renew(barcode)
  heslog.info("Returning %s" % renewData)
  return response.success(renewData)


def getUserCircHistory(event, context):
  params = event.get("headers", {})
  alephId = params.get("aleph-id")
  heslog.addLambdaContext(event, context)
  if not alephId:
    heslog.error("No aleph id provided")
    return response.error(400)

  direct = AlephOracle()
  data = direct.userCircHistory(alephId)
  heslog.info("Returning success")
  return response.success(data)

def getUserDetails(event, context):
  heslog.addLambdaContext(event, context)
  netId = event.get("requestContext", {}).get("authorizer", {}).get("netid", None)
  if not netId:
    heslog.error("Invalid token or no token provided")
    return response.error(400)

  direct = AlephOracle()
  data = direct.userDetails(netId)
  heslog.info("Returning success")
  return response.success(data)


def updateUser(event, context):
  params = event.get("headers", {})
  library = params.get("library")
  heslog.addLambdaContext(event, context, library=library)

  alephId = params.get("aleph-id")

  if not library:
    heslog.error("No library provided")
    return response.error(400)

  if not alephId:
    heslog.error("No aleph id provided")
    return response.error(400)

  aleph = Aleph(alephId)
  updateSuccess = aleph.updateHomeLibrary(library)
  if updateSuccess:
    heslog.info("Returning success")
    return response.success({})
  return response.error(500)
