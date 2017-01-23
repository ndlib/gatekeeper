import urllib2

class RequestType(object):
  def __init__(self, netid):
    super(RequestType, self).__init__()
    self.netid = netid
    self.name = "Empty"

    self.callbacks = {
      'checked_out': self._default,
      'web': self._default,
      'pending': self._default,
    }


  def _default(self):
    return []


  def _formatUrl(self, base, path):
    return base + path.replace("<<netid>>", self.netid)


  def _makeReq(self, url, headers):
    req = urllib2.Request(url, None, headers)
    response = ""
    try:
      response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
      print e.code
      print e.read()
      return "Error"
    except urllib2.URLError as e:
      print e.reason
      return "Error"

    return response.read()


  def _setCallback(self, callType, callback):
    if callType in self.callbacks:
      self.callbacks[callType] = callback
    else:
      print "%s is not a registered callback type" % callType


  def serviceName(self):
    return self.name


  def request(self, callType):
    if callType in self.callbacks:
      return self.callbacks[callType]()
    else:
      print "%s is not a registered callback type" % callType

