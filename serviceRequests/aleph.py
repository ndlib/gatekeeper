from hesburgh import heslog, hesutil, hestest
import xml.etree.ElementTree as ET
from requestType import RequestType
import urllib2
import untangle


class Aleph(RequestType):
  """docstring for Aleph"""
  def __init__(self, netid="", library="ndu50"):
    super(Aleph, self).__init__(netid)
    self.name = "Aleph"

    # self.url = "http://aleph2.library.nd.edu:8991"
    self.url = hesutil.getEnv("ALEPH_URL", throw=True)
    self.alephUrl = self._formatUrl(self.url, hesutil.getEnv("ALEPH_PATH", throw=True)).replace("<<lib>>", library)

    self._setCallback('borrowed', self.borrowed)
    self._setCallback('user', self.userData)
    self._setCallback('pending', self.pending)


  def _parseXML(self, xmlStr):
    if not xmlStr:
      return None
    def _childLoop(node):
      out = {}
      for child in node:
        value = None
        if len(child):
          value = _childLoop(child)
        else:
          value = child.text

        # This is not pretty, but allows us to get what we want
        #  from marc records without a complex parser
        key = child.tag
        kId = child.attrib.get("id")
        kI2 = child.attrib.get("i2")
        if kId and kI2 and kI2 != ' ':
          kId += "_" + kI2

        kLabel = child.attrib.get("label")
        suffix = kLabel or kId

        if suffix is not None:
          key += "_%s" % suffix

        # if this key exists in the output already, make that value an array of values
        if key in out:
          if isinstance(out[key], list):
            out[key].append(value)
          else:
            currentVal = out[key]
            out[key] = [currentVal, value]
        else:
          out[key] = value

      return out

    root = ET.fromstring(xmlStr)
    out = _childLoop(root)

    return out


  def _getZPart(self, directory, num, index):
    zname = "z%i" % num
    return directory.get(zname, {}).get(zname + "-%s" % index, None)


  def _formatDueDate(self, dueStr):
    # '20170531' => 2017-05-31
    if dueStr and len(dueStr) >= 8:
      return "%s-%s-%s" % (dueStr[:4], dueStr[4:6], dueStr[6:8])
    return dueStr


  def _makeAlephItem(self, alephDir, isHolds = False):
    # no due for holds
    status = self._getZPart(alephDir, 36, "status")
    if status == "A":
      status = "On Loan"
    elif status == "C":
      status = "Claimed Return"
    elif status == "L":
      status = "Lost"

    if isHolds:
      status = self._getZPart(alephDir, 37, "status")
      if not status: # blank = ready for pickup
        status = "Ready for Pickup until %s" % (self._getZPart(alephDir, 37, "end-hold-date") or 'Unknown Date')
      elif "In process" in status:
        status = "In Process"
      elif "Waiting" in status:
        status = "Waiting in Queue"

    if not status:
      status = "No status available"

    dueDate = self._formatDueDate(alephDir.get("due-date"))

    item = {
      'title': self._getZPart(alephDir, 13, "title"),
      'author': self._getZPart(alephDir, 13, "author"),
      'dueDate': dueDate,
      'published': self._getZPart(alephDir, 13, "imprint"),
      'status': status,
      'barcode': self._getZPart(alephDir, 30, "barcode"),
    }

    if isHolds:
      item["holdDate"] = self._getZPart(alephDir, 37, "hold-date")
      if "Ready for Pickup" in status:
        item["pickupLocation"] = self._getZPart(alephDir, 37, "pickup-location")

    return item


  def _format(self, parsed):
    balance = 0
    for fine in parsed.get("fine", []):
      isCredit = self._getZPart(fine, 31, "credit-debit") == "C"
      ammount = float(self._getZPart(fine, 31, "sum").strip("()"))
      balance += ammount if isCredit else -ammount

    if not parsed:
      return None
    return {
      'name': self._getZPart(parsed, 303, "name"),
      'address1': self._getZPart(parsed, 304, "address-1"),
      'address2': self._getZPart(parsed, 304, "address-2"),
      'telephone': self._getZPart(parsed, 304, "telephone"),
      'telephone2': self._getZPart(parsed, 304, "telephone-2"),
      'homeLibrary': self._getZPart(parsed, 303, "home-library"),
      'status': self._getZPart(parsed, 305, "bor-status"),
      'alephId': self._getZPart(parsed, 304, "id"),
      'balance': balance,
    }


  def findItem(self, doc):
    path = hesutil.getEnv("ALEPH_ITEM_PATH", throw=True)

    url = self.url + path.replace("<<doc>>", doc)
    heslog.info("Requesting document %s" % doc)
    stringResponse = self._makeReq(url, {})
    return untangle.parse(stringResponse)


  def userData(self):
    headers = {
      'Content-Type': 'xml',
    }

    url = self.alephUrl
    stringResponse = self._makeReq(url, headers)
    parsed = self._parseXML(stringResponse)
    return { "user": self._format(parsed) }


  def renew(self, barcode):
    path = hesutil.getEnv("ALEPH_RENEW_PATH", throw=True)

    heslog.info("Renewing item")
    url = self._formatUrl(self.url, path).replace("<<barcode>>", barcode)
    stringResponse = self._makeReq(url, {})
    parsed = self._parseXML(stringResponse)
    heslog.debug(parsed)

    def status(code, text = None):
      ret = { "renewStatus": code}
      if text:
        ret["statusText"] = text
      return ret

    # handle aleph errors
    error = parsed.get("error", "")
    if "New due date must be bigger than current's loan due date" in error:
      return status(304)
    if "can not be found in library" in error or "is not Loaned in library" in error:
      return status(404)
    if "has no Local Information" in error or "Item provided is not loaned by given bor_id" in error:
      return status(500, "Error in user information")

    error = parsed.get("error-text-1")
    if error:
      return status(500, error)

    error = parsed.get("error-text-2")
    if error:
      return status(500, error)

    ret = status(200)
    ret["dueDate"] = self._formatDueDate(parsed.get("due-date"))
    return ret


  def updateHomeLibrary(self, newLib):
    heslog.info("Updating home library to %s" % newLib)

    updateXml = "<?xml version=\"1.0\"?><p-file-20><patron-record><z303><match-id-type>00</match-id-type><match-id>%s</match-id><record-action>A</record-action><z303-home-library>%s</z303-home-library></z303></patron-record></p-file-20>" % (self.netid, newLib)

    url = self.url + '/X'
    body = hesutil.getEnv("ALEPH_UPDATE_BODY", throw=True) \
                  .replace("<<username>>", hesutil.getEnv("ALEPH_USER", throw=True)) \
                  .replace("<<password>>", hesutil.getEnv("ALEPH_PASS", throw=True)) \
                  .replace("<<reqxml>>", updateXml)

    req = urllib2.Request(url, data=body)
    req.get_method = lambda: "POST"
    response = ""
    try:
      response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
      heslog.error("%s" % e.code)
      heslog.error(e.read())
      return None
    except urllib2.URLError as e:
      heslog.error(e.reason)
      return None

    parsed = self._parseXML(response.read())
    # <error/> is filled with both actual errors and the success message because that makes sense
    if "Succeeded to REWRITE table" in parsed.get("error"):
      return True
    else:
      heslog.error(parsed.get("error"))
      return False


  def borrowed(self):
    headers = {
      'Content-Type': 'xml',
    }

    heslog.info("Requesting checked out items")
    test = hestest.get(self.netid)
    if test:
      heslog.info("Got a test netid")
      stringResponse = test.get("aleph", "")
    else:
      stringResponse = self._makeReq(self.alephUrl, headers)

    parsed = self._parseXML(stringResponse)

    items = parsed.get('item-l', [])
    if type(items) is dict:
      items = [items]
    return { "web": [], "checkedOut": [ self._makeAlephItem(i) for i in items ] }


  def pending(self):
    headers = {
      'Content-Type': 'xml',
    }

    heslog.info("Requesting pending items")
    test = hestest.get(self.netid)
    if test:
      heslog.info("Got a test netid")
      stringResponse = test.get("aleph", "")
    else:
      stringResponse = self._makeReq(self.alephUrl, headers)

    parsed = self._parseXML(stringResponse)

    items = parsed.get('item-h', [])
    if type(items) is dict:
      items = [items]
    return { "pending": [ self._makeAlephItem(i, True) for i in items ] }

