from hesburgh import heslog
import json
import Queue
import urllib2
import threading

class ThreadUrl(threading.Thread):
  def __init__(self, queue, outDict, netid):
    threading.Thread.__init__(self)
    self.queue = queue
    self.outDict = outDict
    self.netid = netid


  def updateOut(self, data):
    for k,v in data.iteritems():
      if isinstance(v, list):
        if k not in self.outDict:
          self.outDict[k] = []
        self.outDict[k].extend(v)
      elif isinstance(v, dict):
        if k not in self.outDict:
          self.outDict[k] = {}
        self.outDict[k].update(v)
      else:
        heslog.error("Not sure what to do with this information %s" % v)


  def run(self):
    while True:
      host = self.queue.get()

      try:
        request = urllib2.Request(host, headers={"netid": self.netid})
        response = urllib2.urlopen(request)
        self.updateOut(json.loads(response.read()))
      except urllib2.HTTPError as e:
        heslog.error(e.code)
        heslog.error(e.read())
      except urllib2.URLError as e:
        heslog.error(e.reason)
      except Exception as e:
        heslog.error(e)

      self.queue.task_done()


class Requester(object):
  def __init__(self, netid):
    super(Requester, self).__init__()
    self.netid = netid

    self.queue = Queue.Queue()
    self.out = {}

    self.baseUrl = "https://bryppoaj0d.execute-api.us-east-1.amazonaws.com/dev/items/"
    self.services = [
      "aleph",
      "illiad",
    ]

    for i in range(len(self.services)):
      t = ThreadUrl(self.queue, self.out, self.netid)
      t.setDaemon(True)
      t.start()


  def checkedOut(self):
    for service in self.services:
      self.queue.put(self.baseUrl + 'borrowed/' + service)

    self.queue.join()

    return self.out


  def pending(self):
    for service in self.services:
      self.queue.put(self.baseUrl + 'pending/' + service)

    self.queue.join()

    return self.out
