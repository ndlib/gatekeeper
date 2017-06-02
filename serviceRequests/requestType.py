from hesburgh import heslog
import urllib2

class RequestType(object):
  def __init__(self, netid):
    super(RequestType, self).__init__()
    self.netid = netid
    self.name = "Empty"

    self.callbacks = {
      'checkedOut': self._defaultList,
      'web': self._defaultList,
      'pending': self._defaultList,
      'user': self._defaultDict,
    }


  def _defaultList(self):
    return []


  def _defaultDict(self):
    return {}


  def _formatUrl(self, base, path):
    return base + path.replace("<<netid>>", self.netid)


  def _makeReq(self, url, headers):
    req = urllib2.Request(url, None, headers)
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

    return response.read()


  def _setCallback(self, callType, callback):
    if callType in self.callbacks:
      self.callbacks[callType] = callback
    else:
      heslog.error("%s is not a registered callback type" % callType)


  def serviceName(self):
    return self.name


  def request(self, callType):
    if callType in self.callbacks:
      return self.callbacks[callType]()
    else:
      heslog.error("%s is not a registered callback type" % callType)

