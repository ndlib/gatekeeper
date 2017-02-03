from hesburgh import heslog,hesutil
import xml.etree.ElementTree as ET
from requestType import RequestType


class Aleph(RequestType):
  """docstring for Aleph"""
  def __init__(self, netid):
    super(Aleph, self).__init__(netid)
    self.name = "Aleph"

    # self.url = "http://aleph2.library.nd.edu:8991"
    self.url = "http://10.71.1.130"

    self._setCallback('checkedOut', self.checkedOut)
    self._setCallback('user', self.userData)


  def _parseXML(self, xmlStr):
    def _childLoop(node):
      out = {}
      for child in node:
        value = None
        if len(child):
          value = _childLoop(child)
        else:
          value = child.text

        # if this key exists in the output already, make that value an array of values
        if child.tag in out:
          if isinstance(out[child.tag], list):
            out[child.tag].append(value)
          else:
            currentVal = out[child.tag]
            out[child.tag] = [currentVal, value]
        else:
          out[child.tag] = value

      return out

    root = ET.fromstring(xmlStr)
    out = _childLoop(root)

    return out


  def _getZPart(self, directory, num, index):
    zname = "z%i" % num
    return directory.get(zname, {}).get(zname + "-%s" % index, None)


  def _makeAlephItem(self, alephDir, isHolds = False):
    # no due for holds
    item = {
      'title': self._getZPart(alephDir, 13, "title"),
      'author': self._getZPart(alephDir, 13, "author"),
      'dueDate': alephDir["due-date"],
      'published': self._getZPart(alephDir, 13, "imprint"),
    }

    if isHolds:
      item["holdDate"] = self._getZPart(alephDir, 37, "hold-date")
      item["pickupLocation"] = self._getZPart(alephDir, 37, "pickup-location")

    return item


  def _format(self, parsed):
    return {
      'name': self._getZPart(parsed, 303, "name"),
      'address1': self._getZPart(parsed, 304, "address-1"),
      'address2': self._getZPart(parsed, 304, "address-2"),
      'telephone': self._getZPart(parsed, 304, "telephone"),
      'telephone2': self._getZPart(parsed, 304, "telephone-2"),
      'homeLibrary': self._getZPart(parsed, 303, "home-library"),
      'status': self._getZPart(parsed, 305, "bor-status"),
    }


  def userData(self):
    path = hesutil.getEnv("ALEPH_PATH")

    headers = {
      'Content-Type': 'xml',
    }

    url = self._formatUrl(self.url, path)
    stringResponse = self._makeReq(url, headers)
    parsed = self._parseXML(stringResponse)
    return self._format(parsed)


  def checkedOut(self):
    path = hesutil.getEnv("ALEPH_PATH")

    headers = {
      'Content-Type': 'xml',
    }

    url = self._formatUrl(self.url, path)
    stringResponse = self._makeReq(url, headers)
    parsed = self._parseXML(stringResponse)
    # 'holds': [ self._makeAlephItem(i, True) for i in parsed.get('item-h', []) ],
    return [ self._makeAlephItem(i) for i in parsed.get('item-l', []) ]

