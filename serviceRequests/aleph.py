from hesburgh import heslog, hesutil, hestest
import xml.etree.ElementTree as ET
from requestType import RequestType


class Aleph(RequestType):
  """docstring for Aleph"""
  def __init__(self, netid):
    super(Aleph, self).__init__(netid)
    self.name = "Aleph"

    # self.url = "http://aleph2.library.nd.edu:8991"
    self.url = hesutil.getEnv("ALEPH_URL", throw=True)

    self._setCallback('checkedOut', self.checkedOut)
    self._setCallback('user', self.userData)


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


  def _makeAlephItem(self, alephDir, isHolds = False):
    # no due for holds
    status = self._getZPart(alephDir, 36, "status")
    if status == "A":
      status = "On Loan"
    elif status == "C":
      status = "Claimed Return"
    elif status == "L":
      status = "Lost"

    item = {
      'title': self._getZPart(alephDir, 13, "title"),
      'author': self._getZPart(alephDir, 13, "author"),
      'dueDate': alephDir["due-date"],
      'published': self._getZPart(alephDir, 13, "imprint"),
      'status': status,
    }

    if isHolds:
      item["holdDate"] = self._getZPart(alephDir, 37, "hold-date")
      item["pickupLocation"] = self._getZPart(alephDir, 37, "pickup-location")

    return item


  def _format(self, parsed):
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
    }


  def findItem(self, doc):
    path = hesutil.getEnv("ALEPH_ITEM_PATH", throw=True)

    url = self.url + path.replace("<<doc>>", doc)
    stringResponse = self._makeReq(url, {})
    return self._parseXML(stringResponse)


  def userData(self):
    path = hesutil.getEnv("ALEPH_PATH", throw=True)

    headers = {
      'Content-Type': 'xml',
    }

    url = self._formatUrl(self.url, path)
    stringResponse = self._makeReq(url, headers)
    parsed = self._parseXML(stringResponse)
    return self._format(parsed)


  def checkedOut(self):
    path = hesutil.getEnv("ALEPH_PATH", throw=True)
    if path is None:
      return None;

    headers = {
      'Content-Type': 'xml',
    }

    test = hestest.get(self.netid)
    if test:
      stringResponse = test.get("aleph", "")
    else:
      url = self._formatUrl(self.url, path)
      stringResponse = self._makeReq(url, headers)

    parsed = self._parseXML(stringResponse)
    # 'holds': [ self._makeAlephItem(i, True) for i in parsed.get('item-h', []) ],

    items = parsed.get('item-l', [])
    if type(items) is dict:
      items = [items]
    return [ self._makeAlephItem(i) for i in items ]

