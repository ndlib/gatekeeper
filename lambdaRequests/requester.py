import json
import Queue
import urllib2
import threading

class ThreadUrl(threading.Thread):
  def __init__(self, queue, outDict):
    threading.Thread.__init__(self)
    self.queue = queue
    self.outDict = outDict


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
        print "Not sure what to do with this information %s" % v


  def run(self):
    while True:
      host = self.queue.get()

      try:
        response = urllib2.urlopen(host)
        self.updateOut(json.loads(response.read()))
      except urllib2.HTTPError as e:
        print e.code
        print e.read()
      except urllib2.URLError as e:
        print e.reason
      except Exception as e:
        print e

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

    print len(self.services)
    for i in range(len(self.services)):
      t = ThreadUrl(self.queue, self.out)
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
