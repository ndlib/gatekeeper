from hesburgh import heslog,hesutil
import json
import Queue
import threading
import boto3

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
        la = boto3.client("lambda")
        response = la.invoke(FunctionName=host.get("func", ""), Payload=json.dumps({"netid": self.netid, "type": host.get("type", "")}))
        self.updateOut(json.loads(response['Payload'].read()))
      except Exception as e:
        heslog.error(e)

      self.queue.task_done()


class Requester(object):
  def __init__(self, netid):
    super(Requester, self).__init__()
    self.netid = netid

    self.queue = Queue.Queue()
    self.out = {}

    self.services = [
      hesutil.getEnv("ALEPH_FUNC"),
      hesutil.getEnv("ILLIAD_FUNC"),
    ]

    for i in range(len(self.services)):
      t = ThreadUrl(self.queue, self.out, self.netid)
      t.setDaemon(True)
      t.start()


  def checkedOut(self):
    for service in self.services:
      self.queue.put({ 'func': service, 'type': 'borrowed' })

    self.queue.join()

    return self.out


  def pending(self):
    for service in self.services:
      self.queue.put({ 'func': service, 'type': 'pending' })

    self.queue.join()

    return self.out
