from hesburgh import heslog, hesutil, hestest
import json
import re
import untangle
from requestType import RequestType

class Primo(RequestType):
  def __init__(self, userId=""):
    super(Primo, self).__init__(userId)

    self.name = "Primo"

    self.userId = userId
    self.institution = "NDU"
    self.url = hesutil.getEnv("PRIMO_URL", throw=True)
    self.displayUrl = hesutil.getEnv("PRIMO_DISPLAY_URL", throw=True)

    self._setCallback('favorites', self.favorites)


  def favorites(self):
    url = self.url \
              .replace("<<api>>", "eshelf") \
              .replace("<<institution>>", self.institution) \
              .replace("<<userId>>", self.userId)

    heslog.info("Getting primo favorites")
    res = self._makeReq(url, {})

    if not res:
      heslog.error("Contacting primo failed - likely because of permissions")
      return None

    res = json.loads(res)

    if res.get("errorCode"):
      heslog.error(res)
      return {}

    items = res.get("basket-items")
    heslog.info("Got %s item(s)" % len(items))

    ret = []
    for item in items:
      docId = item.get("pnxId")
      display = None
      if docId:
        display = self.displayUrl \
                      .replace("<<institution>>", self.institution) \
                      .replace("<<docId>>", docId)

      ret.append({
        "title": item.get("title"),
        "author": item.get("author"),
        "display": display,
        "type": item.get("@TYPE"),
        "id": item.get("@id"),
      })

    return ret


  # query primo for aleph ids
  def query(self, docids):
    primoStr = hesutil.getEnv("PRIMO_SEARCH").replace("<<docids>>", docids)
    heslog.info("Running primo query for found docs %s" % primoStr)
    res = self._makeReq(primoStr, {})
    res = untangle.parse(res)

    # parse out availaibility information
    #  contains codes like $$[character][data] where the character denotes data type
    #  these codes/cata are concatonated - eg. $$XFoo$$YBar
    # Finds all code/data combination and grabs each sparately
    availRe = re.compile('\$\$([a-zA-Z0-9])([^$]*)')
    # codes we care about, and a human-readable name
    availFieldsMap = {
      "I": "institution",
      "L": "library",
      "1": "subLibrary",
      "2": "callNumber",
      "S": "availability",
      "O": "recordId",
      "Y": "subLibraryCode",
      "Z": "collectionCode"
    }

    validEntries = []
    # parse pnx record(s) from search above
    records = res.sear_SEGMENTS.sear_JAGROOT.sear_RESULT.sear_DOCSET
    heslog.info("Primo search found %s docs" % len(records))
    for record in records.sear_DOC:
      availability = record.PrimoNMBib.record.display.availlibrary

      for a in availability:
        entry = {}
        split = availRe.findall(a.cdata.strip())
        for match in split:
          if match[0] in availFieldsMap:
            entry[availFieldsMap[match[0]]] = match[1]

        validEntries.append(entry)

    return validEntries