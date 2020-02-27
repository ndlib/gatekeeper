from hesburgh import heslog
import urllib2
import socket

class RequestType(object):
  MAX_RETRIES = 2
  URL_TIMEOUT = 8 #  seconds

  def __init__(self, netid):
    super(RequestType, self).__init__()
    self.netid = netid
    self.name = "Empty"

    self.callbacks = {}


  def _formatUrl(self, base, path):
    return base + path.replace("<<netid>>", self.netid)


  def _makeReq(self, url, headers, retryCount=0):
    req = urllib2.Request(url, None, headers)
    response = ""
    try:
      response = urllib2.urlopen(req, timeout=self.URL_TIMEOUT)
    except urllib2.HTTPError as e:
      heslog.error("%s" % e.code)
      heslog.error(e.read())
      return None
    except urllib2.URLError as e:
      if isinstance(e.reason, socket.timeout) and retryCount < self.MAX_RETRIES:
        heslog.info('Request timed out. Retrying.')
        return self._makeReq(url, headers, retryCount + 1)
      else:
        heslog.error(e.reason)
        return None
    except socket.timeout as e:
      if retryCount < self.MAX_RETRIES:
        heslog.info('Request timed out. Retrying.')
        return self._makeReq(url, headers, retryCount + 1)
      else:
        heslog.error(e.reason)
        return None

    return response.read()


  def _setCallback(self, callType, callback):
    self.callbacks[callType] = callback


  def serviceName(self):
    return self.name


  def request(self, callType):
    if callType in self.callbacks:
      return self.callbacks[callType]()
    else:
      heslog.error("%s is not a registered callback type for %s" % (callType, self.name))
      return None
